"""
Copyright 2024 Eviden
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


This module defines the HiDALGO2 Data Transfer API client class.
It provides methods to transfer datasets between different data providers,
including Cloud, HDFS, CKAN, local filesystems and HPC, using NIFI pipelines.
"""

import sys
from typing import Any, Dict, Optional, Callable
import uuid
import os
from types import SimpleNamespace

from hid_data_transfer_lib.conf.hid_dt_configuration import (
    HidDataTransferConfiguration
)
from hid_data_transfer_lib.exceptions.hid_dt_exceptions import (
    HidDataTransferException
)
from hid_data_transfer_lib.nifi.nifi_client import (
    NIFIClient, ExecutionType, AccountingInfo
)

KERBEROS_PRINCIPAL = "kerberos.principal"
HDFS_DATA_FOLDER = "hdfs.data_folder"
HDFS_FILENAME = "hdfs.filename"
HPC_TARGET_FOLDER = "hpc.target_folder"
HPC_DATA_FOLDER = "hpc.data_folder"
HPC_FILENAME = "hpc.filename"
HPC_FILENAME_REGEX = "hpc.filename.regex"
HPC_2FA = "hpc.2fa"
NIFI_DOWNLOAD_FOLDER = "nifi.download_folder"
RECURSIVE = "recursive"

HPC_ACCOUNT_MSG = "Either hpc_password or hpc_secret_key must be provided"


def default_2fa_callback() -> str:
    ''' request user to enter the 2FA token'''
    return input("Enter 2FA token: ")


class HIDDataTransfer:
    """main HiDALGO  API client class
    contains methods to transfer datasets between different data providers
    using NIFI pipelines
    """

    def __init__(
        self, conf: HidDataTransferConfiguration,
        secure: bool = False,
        keycloak_token: Optional[Dict[Any, Any]] = None,
    ) -> None:
        """constructs a NIFI client,
        with the NIFI endpoint taken from configuration
        """
        self.__conf = conf
        self.__secure = secure
        self.__nifi_client = NIFIClient().configure(conf, secure)
        self.__logger = self.__conf.logger("hid_data_transfer_lib")
        self.__keycloak_token = keycloak_token

    def reset(self):
        """ Reset NIFIClient configuration"""
        self.__nifi_client = NIFIClient().configure(self.__conf, self.__secure)

    # Helper methods
    def process_wildcards(self, name):
        '''Process shell like wildcards in the name
        as regular expressions'''
        if not name or name == "":
            name = "[^\\.].*"
        else:
            name = name.replace(".", "\\.")
            name = name.replace("*", ".*")
            name = name.replace("?", ".")
        return name

    def generate_ckan_resource_name(self, args):
        '''computes the ckan resource name'''
        ckan_resource = args.ckan_resource
        if ckan_resource:
            ckan_resource = ckan_resource + ".zip" \
                    if not ckan_resource.endswith(".zip") \
                    else ckan_resource
        else:
            ckan_resource = (
                    args.data_source.replace("/", "_")
                    if not args.data_source.endswith("/")
                    else args.data_source[:-1].replace("/", "_")
                )
            if not ckan_resource.endswith(".zip"):
                ckan_resource += ".zip"
        return ckan_resource

    # MAIN API methods
    def hdfs2hpc(
        self,
        hpc_host,
        hpc_username,
        data_source,
        data_target,
        hpc_port=None,
        hpc_password=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        kerberos_principal=None,
        kerberos_password=None,
        concurrent_tasks: Optional[int] = None,
        recursive: bool = False,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HDFS to HPC using SFTP
        Args:
            hpc_host (str): The hostname of the HPC server.
            hpc_port (int): The port number of the HPC server.
            hpc_username (str): The username for the HPC server.
            hpc_password (str): The password for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The path to the secret key
                for HPC authentication.
            data_source (str): The source path in HDFS.
            data_target (str): The target path in HPC.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            concurrent_tasks (int, optional): The number of concurrent tasks
            for parallel processors. If None, the default value from
            the configuration will be used.
            recursive (bool): if True, files in data_source subfolders are
            also transferred, otherwise not
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """
        args = SimpleNamespace(
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=hpc_password,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            data_source=data_source,
            data_target=data_target,
            kerberos_principal=kerberos_principal,
            kerberos_password=kerberos_password,
            recursive=recursive,
        )

        self.__logger.info(
            "executing hdfs2hpc command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_TARGET_FOLDER] = args.data_target
            arguments[HDFS_DATA_FOLDER] = \
                "/".join(args.data_source.split("/")[:-1])
            arguments[HDFS_FILENAME] = \
                self.process_wildcards(args.data_source.split("/")[-1])
            arguments[KERBEROS_PRINCIPAL] = args.kerberos_principal
            arguments[RECURSIVE] = args.recursive

            execution_type = {
                "ListHDFS": ExecutionType.ONCE,
                "FetchHDFS": ExecutionType.FOREVER,
                "UpdateAttribute": ExecutionType.FOREVER,
                "PutSFTP": ExecutionType.FOREVER,
            }
            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            processors_with_hpc_sensitive_parameters = ["PutSFTP"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_hpc_parameters(
                    processors_with_hpc_sensitive_parameters,
                    args
                )

            processors_with_hdfs_sensitive_parameters = \
                ["ListHDFS", "FetchHDFS"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_hdfs_parameters(
                    processors_with_hdfs_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key and not args.hpc_password:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "PutSFTP": concurrent_tasks,
                "FetchHDFS": concurrent_tasks,
            }

            return self.__nifi_client.run_process_group(
                "hdfs2hpc",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="PutSFTP",
                concurrent_tasks=concurrent_tasks_dict,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def hdfs2hpc_2fa(
        self,
        hpc_host,
        hpc_username,
        data_source,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        kerberos_principal=None,
        kerberos_password=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HDFS to HPC using SFTP with a 2FA token
        Args:
            hpc_host (str): The hostname of the HPC server.
            hpc_port (int): The port number of the HPC server.
            hpc_username (str): The username for the HPC server.
            hpc_secret_key_password (str): The password for the HPC
                secret key.
            hpc_secret_key_path (str): The path to the secret key
                for HPC authentication.
            data_source (str): The source path in HDFS.
            data_target (str): The target path in HPC.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """
        return self._hdfs2hpc_2fa_opt(
            hpc_host,
            hpc_username,
            data_source,
            data_target,
            hpc_port,
            hpc_secret_key_password,
            hpc_secret_key_path,
            kerberos_principal,
            kerberos_password,
            callback_2fa,
            concurrent_tasks=concurrent_tasks
        )

    def _hdfs2hpc_2fa(
        self,
        hpc_host,
        hpc_username,
        data_source,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        kerberos_principal=None,
        kerberos_password=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HDFS to HPC using SFTP with a 2FA token
        Single pipeline implementation - not optimized
        Args:
            hpc_host (str): The hostname of the HPC server.
            hpc_port (int): The port number of the HPC server.
            hpc_username (str): The username for the HPC server.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The path to the secret key
                for HPC authentication.
            data_source (str): The source path in HDFS.
            data_target (str): The target path in HPC.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
            concurrent_tasks (int, optional): The number of concurrent tasks
            for parallel processors. If None, the default value from
            the configuration will be used.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """
        return self._hdfs2hpc_2fa_opt(
            hpc_host,
            hpc_username,
            data_source,
            data_target,
            hpc_port,
            hpc_secret_key_password,
            hpc_secret_key_path,
            kerberos_principal,
            kerberos_password,
            callback_2fa,
            concurrent_tasks=concurrent_tasks
        )

    def _hdfs2hpc_2fa_opt(
        self,
        hpc_host,
        hpc_username,
        data_source,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        kerberos_principal=None,
        kerberos_password=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HDFS to HPC using SFTP with a 2FA token
        Double pipeline implementation - optimized
        Args:
            hpc_host (str): The hostname of the HPC server.
            hpc_port (int): The port number of the HPC server.
            hpc_username (str): The username for the HPC server.
            hpc_secret_key_path (str): The path to the secret key
                for HPC authentication.
            data_source (str): The source path in HDFS.
            data_target (str): The target path in HPC.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """
        args = SimpleNamespace(
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=None,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            data_source=data_source,
            data_target=data_target,
            kerberos_principal=kerberos_principal,
            kerberos_password=kerberos_password,
        )

        self.__logger.info(
            "executing hdfs2hpc_2fa command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_TARGET_FOLDER] = args.data_target
            arguments[HDFS_DATA_FOLDER] = \
                "/".join(args.data_source.split("/")[:-1])
            arguments[HDFS_FILENAME] = \
                self.process_wildcards(args.data_source.split("/")[-1])
            arguments[KERBEROS_PRINCIPAL] = args.kerberos_principal

            # set local.data_folder to keep dataset retrieved from HDFS
            __uuid = uuid.uuid4()
            download_folder = os.path.join(
                self.__conf.nifi_download_folder(), str(__uuid)
            )
            self.__nifi_client.create_folder(download_folder)
            arguments[NIFI_DOWNLOAD_FOLDER] = download_folder

            execution_type = {
                "ListHDFS": ExecutionType.ONCE,
                "FetchHDFS": ExecutionType.FOREVER,
                "PutFile": ExecutionType.FOREVER,
                "GenerateFlowFile": ExecutionType.ONCE,
                "SftpTransferToHPCWithVPNCode": ExecutionType.ONCE,
            }
            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            sensitive_parameters = {}

            processors_with_hdfs_sensitive_parameters = \
                ["ListHDFS", "FetchHDFS"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_hdfs_parameters(
                    processors_with_hdfs_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "PutFile": concurrent_tasks,
                "FetchHDFS": concurrent_tasks,
            }

            process_ids = []
            process_id, accounting_info = self.__nifi_client.run_process_group(
                "hdfs2hpcwith2fa_part1",
                execution_type,
                arguments,
                keys_arguments=keys_arguments,
                sensitive_parameters=sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="PutFile",
                concurrent_tasks=concurrent_tasks_dict,
            )
            process_ids.append(process_id)

            process_id, _ = self.__nifi_client.run_process_group(
                "hdfs2hpcwith2fa_part2",
                execution_type,
                arguments,
                keys_arguments=keys_arguments,
                sensitive_parameters=sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                processor_with_2fa="SftpTransferToHPCWithVPNCode",
                callback_2fa=callback_2fa,
            )
            process_ids.append(process_id)

            return '|'.join(process_ids), accounting_info

        except Exception as ex:
            raise HidDataTransferException(ex) from ex
        finally:
            # Remove uploaded files
            if download_folder is not None:
                self.__nifi_client.remove_download_folder(download_folder)

    def hpc2hdfs(
        self,
        hpc_host,
        hpc_username,
        data_source,
        data_target,
        hpc_port=None,
        hpc_password=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        kerberos_principal=None,
        kerberos_password=None,
        concurrent_tasks: Optional[int] = None,
        recursive: bool = False,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HPC to HDFS using SFTP

        Args:
            hpc_host (str): The hostname of the HPC server.
            hpc_port (int): The port number of the HPC server.
            hpc_username (str): The username for the HPC server.
            hpc_password (str): The password for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
                secret key.
            hpc_secret_key_path (str): The path to the secret
                key for HPC authentication.
            data_source (str): The source path in HPC.
            data_target (str): The target path in HDFS.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            concurrent_tasks (int, optional): The number of concurrent tasks
                for parallel processors. If None, the default value from
                the configuration will be used.
            recursive (bool): if True, files in data_source subfolders are
            also transferred, otherwise not
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """

        args = SimpleNamespace(
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=hpc_password,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            data_source=data_source,
            data_target=data_target,
            kerberos_principal=kerberos_principal,
            kerberos_password=kerberos_password,
            recursive=recursive,
        )

        self.__logger.info(
            "executing hpc2hdfs command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            hpc_filename = args.data_source[args.data_source.rfind("/") + 1 :]
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_FILENAME] = hpc_filename if hpc_filename else ".*"
            arguments[HPC_DATA_FOLDER] = args.data_source[
                : args.data_source.rfind("/")
            ]
            arguments[HDFS_DATA_FOLDER] = args.data_target
            arguments[KERBEROS_PRINCIPAL] = args.kerberos_principal
            arguments[RECURSIVE] = args.recursive

            execution_type = {
                "ListSFTP": ExecutionType.ONCE,
                "DistributeLoad": ExecutionType.FOREVER,
                "FetchSFTP": ExecutionType.FOREVER,
                "UpdateAttribute": ExecutionType.FOREVER,
                "PutHDFS": ExecutionType.FOREVER,
            }
            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            processors_with_hpc_sensitive_parameters = \
                ["ListSFTP", "FetchSFTP"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_hpc_parameters(
                    processors_with_hpc_sensitive_parameters, args
                )

            processors_with_hdfs_sensitive_parameters = \
                ["PutHDFS"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_hdfs_parameters(
                    processors_with_hdfs_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key and not args.hpc_password:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "FetchSFTP": concurrent_tasks,
                "PutHDFS": concurrent_tasks,
            }

            return self.__nifi_client.run_process_group(
                "hpc2hdfs",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="PutHDFS",
                concurrent_tasks=concurrent_tasks_dict
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def hpc2hdfs_2fa(
        self,
        hpc_host,
        hpc_username,
        data_source,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        kerberos_principal=None,
        kerberos_password=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HPC to HDFS using SFTP with a 2FA token

        Args:
            hpc_host (str): The hostname of the HPC server.
            hpc_port (int): The port number of the HPC server.
            hpc_username (str): The username for the HPC server.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The path to the secret
                key for HPC authentication.
            data_source (str): The source path in HPC.
            data_target (str): The target path in HDFS.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """
        return self._hpc2hdfs_2fa_opt(
            hpc_host,
            hpc_username,
            data_source,
            data_target,
            hpc_port=hpc_port,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key_path=hpc_secret_key_path,
            kerberos_principal=kerberos_principal,
            kerberos_password=kerberos_password,
            callback_2fa=callback_2fa,
            concurrent_tasks=concurrent_tasks
        )

    def _hpc2hdfs_2fa_opt(
        self,
        hpc_host,
        hpc_username,
        data_source,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        kerberos_principal=None,
        kerberos_password=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HPC to HDFS using SFTP with a 2FA token
        using an optimized double pipeline

        Args:
            hpc_host (str): The hostname of the HPC server.
            hpc_port (int): The port number of the HPC server.
            hpc_username (str): The username for the HPC server.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The path to the secret
                key for HPC authentication.
            data_source (str): The source path in HPC.
            data_target (str): The target path in HDFS.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """

        args = SimpleNamespace(
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=None,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            data_source=data_source,
            data_target=data_target,
            kerberos_principal=kerberos_principal,
            kerberos_password=kerberos_password,
        )

        self.__logger.info(
            "executing hpc2hdfs_2fa command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            hpc_filename = args.data_source[args.data_source.rfind("/") + 1 :]
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_FILENAME] = hpc_filename if hpc_filename else "*"
            arguments[HPC_FILENAME_REGEX] = self.process_wildcards(
                hpc_filename
            ) if hpc_filename else "[^\\s]+"
            arguments[HPC_DATA_FOLDER] = args.data_source[
                : args.data_source.rfind("/")
            ]
            arguments[HDFS_DATA_FOLDER] = args.data_target
            arguments[KERBEROS_PRINCIPAL] = args.kerberos_principal

            # set local.data_folder to keep dataset retrieved from HPC
            __uuid = uuid.uuid4()
            download_folder = os.path.join(
                self.__conf.nifi_download_folder(), str(__uuid)
            )
            self.__nifi_client.create_folder(download_folder)
            arguments[NIFI_DOWNLOAD_FOLDER] = download_folder

            execution_type = {
                "GenerateFlowFile": ExecutionType.ONCE,
                "SftpTransferFromHPCWithVPNCode": ExecutionType.ONCE,
                "ListFile": ExecutionType.ONCE,
                "FetchFile": ExecutionType.FOREVER,
                "PutHDFS": ExecutionType.FOREVER,
            }
            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            processors_with_hpc_sensitive_parameters = \
                ["ListSFTP", "FetchSFTP"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_hpc_parameters(
                    processors_with_hpc_sensitive_parameters, args
                )

            processors_with_hdfs_sensitive_parameters = \
                ["PutHDFS"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_hdfs_parameters(
                    processors_with_hdfs_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key and not args.hpc_password:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "PutHDFS": concurrent_tasks,
                "FetchFile": concurrent_tasks,
            }

            process_ids = []
            process_id, _ = self.__nifi_client.run_process_group(
                "hpc2hdfswith2fa_part1",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                processor_with_2fa="SftpTransferFromHPCWithVPNCode",
                callback_2fa=callback_2fa,
                accounting_target="PutHDFS",
                concurrent_tasks=concurrent_tasks_dict,
            )
            process_ids.append(process_id)

            process_id, accounting_info = self.__nifi_client.run_process_group(
                "hpc2hdfswith2fa_part2",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="PutHDFS",
                concurrent_tasks=concurrent_tasks_dict,
            )
            process_ids.append(process_id)

            return "|".join(process_ids), accounting_info

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def _hpc2hdfs_2fa(
        self,
        hpc_host,
        hpc_username,
        data_source,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        kerberos_principal=None,
        kerberos_password=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HPC to HDFS using SFTP with a 2FA token
        using a single non-optimized pipeline

        Args:
            hpc_host (str): The hostname of the HPC server.
            hpc_port (int): The port number of the HPC server.
            hpc_username (str): The username for the HPC server.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The path to the secret
                key for HPC authentication.
            data_source (str): The source path in HPC.
            data_target (str): The target path in HDFS.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer process group(s) executed.
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """
        return self._hpc2hdfs_2fa_opt(
            hpc_host,
            hpc_username,
            data_source,
            data_target,
            hpc_port=hpc_port,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key_path=hpc_secret_key_path,
            kerberos_principal=kerberos_principal,
            kerberos_password=kerberos_password,
            callback_2fa=callback_2fa,
            concurrent_tasks=concurrent_tasks
        )

    def hdfs2ckan(
        self,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        data_source,
        ckan_resource=None,
        kerberos_principal=None,
        kerberos_password=None,
        concurrent_tasks: Optional[int] = None,
        recursive: bool = False,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HDFS to CKAN
        Args:
                ckan_host (str): The CKAN host URL.
                ckan_api_key (str): The CKAN API key.
                ckan_organization (str): The CKAN organization name.
                ckan_dataset (str): The CKAN dataset name.
                ckan_resource (str): The name of the CKAN resource
                    to be created with the data.
                data_source (str): The source path in HDFS.
                kerberos_principal (str): The kerberos principal.
                kerberos_password (str): The kerberos password.
                concurrent_tasks (int, optional): The number of concurrent
                    tasks for parallel processors.
                    If None, the default value from the configuration
                    will be used.
                recursive (bool): if True, files in data_source subfolders are
                also transferred, otherwise not
            Returns:
                str: The id(s) of the data tranfer NIFI process group(s).
                AccountingInfo: The information of the transferred data.
            Raises:
                HidDataTransferException: If an error occurs during
                the data transfer process
        """
        args = SimpleNamespace(
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            data_source=data_source,
            kerberos_principal=kerberos_principal,
            kerberos_password=kerberos_password,
            recursive=recursive,
        )

        self.__logger.info(
            "executing hdfs2ckan command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            arguments: Dict[str, Any] = {}
            arguments[HDFS_DATA_FOLDER] = \
                "/".join(args.data_source.split("/")[:-1])
            arguments[HDFS_FILENAME] = \
                self.process_wildcards(args.data_source.split("/")[-1])
            arguments[KERBEROS_PRINCIPAL] = args.kerberos_principal
            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.generate_ckan_resource_name(args)
            arguments[RECURSIVE] = args.recursive

            execution_type = {
                "ListHDFS": ExecutionType.ONCE,
                "FetchHDFS": ExecutionType.FOREVER,
                "MergeContent": ExecutionType.FOREVER,
                "UpdateAttribute": ExecutionType.ONCE,
                "CKANFileUploader": ExecutionType.ONCE,
            }

            processors_with_ckan_sensitive_parameters = ["CKANFileUploader"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )

            processors_with_hdfs_sensitive_parameters = \
                ["ListHDFS", "FetchHDFS"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_hdfs_parameters(
                    processors_with_hdfs_sensitive_parameters, args
                )
            )

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "FetchHDFS": concurrent_tasks,
                "CKANFileUploader": concurrent_tasks,
            }

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "FetchHDFS": concurrent_tasks,
                "CKANFileUploader": concurrent_tasks,
            }

            return self.__nifi_client.run_process_group(
                "hdfs2ckan",
                execution_type,
                arguments,
                None,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="MergeContent",
                concurrent_tasks=concurrent_tasks_dict
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def ckan2hdfs(
        self,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        data_target,
        ckan_resource=None,
        kerberos_principal=None,
        kerberos_password=None,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from CKAN to HDFS
        Args:
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            data_target (str): The target path in HDFS.
            ckan_resource (str, optional): The specific CKAN resource
                to transfer. Defaults to None.
            kerberos_principal (str): The kerberos principal.
            kerberos_password (str): The kerberos password.
            concurrent_tasks (int, optional): The number of concurrent tasks
                for parallel processors. If None, the default value from
                the configuration will be used.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process
        """

        args = SimpleNamespace(
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            data_target=data_target,
            kerberos_principal=kerberos_principal,
            kerberos_password=kerberos_password,
        )

        self.__logger.info(
            "executing ckan2hdfs command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.process_wildcards(args.ckan_resource)
            arguments[HDFS_DATA_FOLDER] = args.data_target
            arguments[KERBEROS_PRINCIPAL] = args.kerberos_principal

            execution_type = {
                "CKANFileDownloader": ExecutionType.ONCE,
                "PutHDFS": ExecutionType.FOREVER,
            }

            processors_with_ckan_sensitive_parameters = ["CKANFileDownloader"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )

            processors_with_hdfs_sensitive_parameters = \
                ["PutHDFS"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_hdfs_parameters(
                    processors_with_hdfs_sensitive_parameters, args
                )
            )

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "PutHDFS": concurrent_tasks,
            }
            arguments[self.__nifi_client.CKAN_CONCURRENT_TASKS] \
                = concurrent_tasks

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "PutHDFS": concurrent_tasks,
            }
            arguments[self.__nifi_client.CKAN_CONCURRENT_TASKS] \
                = concurrent_tasks

            return self.__nifi_client.run_process_group(
                "ckan2hdfs",
                execution_type,
                arguments,
                None,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="PutHDFS",
                concurrent_tasks=concurrent_tasks_dict
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def ckan2hpc(
        self,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        hpc_host,
        hpc_username,
        data_target,
        hpc_port=None,
        hpc_password=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        ckan_resource=None,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from CKAN to HPC using SFTP

        Args:
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            hpc_host (str): The HPC host URL.
            hpc_port (int): The port number for the HPC connection.
            hpc_username (str): The username for the HPC connection.
            hpc_password (str): The password for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
                secret key.
            hpc_secret_key_path (str): The file path to the HPC secret key.
            data_target (str): The target directory on the HPC where
                the data will be transferred.
            ckan_resource (str, optional): The specific CKAN resource
                to transfer. Defaults to None.
            concurrent_tasks (int, optional): The number of concurrent tasks
                for parallel processors. If None, the default value from
                the configuration will be used.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.
        """

        args = SimpleNamespace(
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=hpc_password,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            data_target=data_target,
        )

        self.__logger.info(
            "executing ckan2hpc command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_TARGET_FOLDER] = args.data_target
            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.process_wildcards(args.ckan_resource)

            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            processors_with_hpc_sensitive_parameters = ["PutSFTP"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_hpc_parameters(
                    processors_with_hpc_sensitive_parameters, args
                )

            processors_with_ckan_sensitive_parameters = ["CKANFileDownloader"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key and not args.hpc_password:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            execution_type = {
                "CKANFileDownloader": ExecutionType.ONCE,
                "PutSFTP": ExecutionType.FOREVER,
            }

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "PutSFTP": concurrent_tasks,
            }
            arguments[self.__nifi_client.CKAN_CONCURRENT_TASKS] \
                = concurrent_tasks

            return self.__nifi_client.run_process_group(
                "ckan2hpc",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="PutSFTP",
                concurrent_tasks=concurrent_tasks_dict
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

        return sensitive_parameters

    def ckan2hpc_2fa(
        self,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        hpc_host,
        hpc_username,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        ckan_resource=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from CKAN to HPC using SFTP with a 2FA token

        Args:
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            hpc_host (str): The HPC host URL.
            hpc_port (int): The port number for the HPC connection.
            hpc_username (str): The username for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The file path to the HPC secret key.
            data_target (str): The target directory on the HPC where
                the data will be transferred.
            ckan_resource (str, optional): The specific CKAN resource
                to transfer. Defaults to None.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.
        """
        return self._ckan2hpc_2fa_opt(
            ckan_host,
            ckan_api_key,
            ckan_organization,
            ckan_dataset,
            hpc_host,
            hpc_username,
            data_target,
            hpc_port=hpc_port,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key_path=hpc_secret_key_path,
            ckan_resource=ckan_resource,
            callback_2fa=callback_2fa,
            concurrent_tasks=concurrent_tasks
        )

    def _ckan2hpc_2fa_opt(
        self,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        hpc_host,
        hpc_username,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        ckan_resource=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from CKAN to HPC using SFTP with a 2FA token
        using an optimized double pipeline

        Args:
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            hpc_host (str): The HPC host URL.
            hpc_port (int): The port number for the HPC connection.
            hpc_username (str): The username for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The file path to the HPC secret key.
            data_target (str): The target directory on the HPC where
                the data will be transferred.
            ckan_resource (str, optional): The specific CKAN resource
                to transfer. Defaults to None.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.
        """

        args = SimpleNamespace(
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=None,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            data_target=data_target,
        )

        self.__logger.info(
            "executing ckan2hpc_2fa command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_TARGET_FOLDER] = args.data_target
            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.process_wildcards(args.ckan_resource)

            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            processors_with_hpc_sensitive_parameters = ["PutSFTP"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_hpc_parameters(
                    processors_with_hpc_sensitive_parameters, args
                )

            processors_with_ckan_sensitive_parameters = ["CKANFileDownloader"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key and not args.hpc_password:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            # set local.data_folder to keep dataset retrieved from CKAN
            __uuid = uuid.uuid4()
            download_folder = os.path.join(
                self.__conf.nifi_download_folder(), str(__uuid)
            )
            self.__nifi_client.create_folder(download_folder)
            arguments[NIFI_DOWNLOAD_FOLDER] = download_folder

            execution_type = {
                "CKANFileDownloader": ExecutionType.ONCE,
                "PutFile": ExecutionType.FOREVER,
                "GenerateFlowFile": ExecutionType.ONCE,
                "SftpTransferToHPCWithVPNCode": ExecutionType.ONCE,
            }

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "PutFile": concurrent_tasks,
            }
            arguments[self.__nifi_client.CKAN_CONCURRENT_TASKS] \
                = concurrent_tasks

            process_ids = []
            process_id, accounting_info = self.__nifi_client.run_process_group(
                "ckan2hpcwith2fa_part1",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="PutFile",
                concurrent_tasks=concurrent_tasks_dict,
            )
            process_ids.append(process_id)

            process_id, _ = self.__nifi_client.run_process_group(
                "ckan2hpcwith2fa_part2",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                processor_with_2fa="SftpTransferToHPCWithVPNCode",
                callback_2fa=callback_2fa,
                accounting_target="PutFile",
                concurrent_tasks=concurrent_tasks_dict,
            )
            process_ids.append(process_id)

            return '|'.join(process_ids), accounting_info

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

        return sensitive_parameters

    def _ckan2hpc_2fa(
        self,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        hpc_host,
        hpc_username,
        data_target,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        ckan_resource=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from CKAN to HPC using SFTP with a 2FA token
        using a single non-optimized pipeline

        Args:
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            hpc_host (str): The HPC host URL.
            hpc_port (int): The port number for the HPC connection.
            hpc_username (str): The username for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The file path to the HPC secret key.
            data_target (str): The target directory on the HPC where
                the data will be transferred.
            ckan_resource (str, optional): The specific CKAN resource
                to transfer. Defaults to None.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.
        """
        return self._ckan2hpc_2fa_opt(
            ckan_host,
            ckan_api_key,
            ckan_organization,
            ckan_dataset,
            hpc_host,
            hpc_username,
            data_target,
            hpc_port=hpc_port,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key_path=hpc_secret_key_path,
            ckan_resource=ckan_resource,
            callback_2fa=callback_2fa,
            concurrent_tasks=concurrent_tasks
        )

    def hpc2ckan(
        self,
        hpc_host,
        hpc_username,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        data_source,
        ckan_resource=None,
        hpc_port=None,
        hpc_password=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        concurrent_tasks: Optional[int] = None,
        recursive: bool = False,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HPC to CKAN using SFTP

        Args:
            hpc_host (str): The HPC host URL.
            hpc_port (int): The port number for the HPC connection.
            hpc_username (str): The username for the HPC connection.
            hpc_password (str): The password for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
                secret key.
            hpc_secret_key_path (str): The file path to the HPC secret key.
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            ckan_resource (str): The name of the CKAN resource
                to be created with the data.
            data_source (str): The source directory on the HPC
                whose data will be transferred.
            concurrent_tasks (int, optional): The number of concurrent tasks
                for parallel processors. If None, the default value from
                the configuration will be used.
            recursive (bool): if True, files in data_source subfolders are
            also transferred, otherwise not
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.

        """
        args = SimpleNamespace(
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=hpc_password,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            data_source=data_source,
            recursive=recursive,
        )

        self.__logger.info(
            "executing hpc2ckan command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            hpc_filename = args.data_source[args.data_source.rfind("/") + 1 :]
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_FILENAME] = hpc_filename if hpc_filename else ".*"
            arguments[HPC_DATA_FOLDER] = args.data_source[
                : args.data_source.rfind("/")
            ]
            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.generate_ckan_resource_name(args)
            arguments[RECURSIVE] = args.recursive

            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            processors_with_hpc_sensitive_parameters = \
                ["ListSFTP", "FetchSFTP"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_hpc_parameters(
                    processors_with_hpc_sensitive_parameters, args
                )

            processors_with_ckan_sensitive_parameters = ["CKANFileUploader"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key and not args.hpc_password:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            execution_type = {
                "ListSFTP": ExecutionType.ONCE,
                "DistributeLoad": ExecutionType.FOREVER,
                "FetchSFTP": ExecutionType.FOREVER,
                "MergeContent": ExecutionType.FOREVER,
                "UpdateAttribute": ExecutionType.ONCE,
                "CKANFileUploader": ExecutionType.ONCE,
            }

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "FetchSFTP": concurrent_tasks,
                "CKANFileUploader": concurrent_tasks,
            }

            return self.__nifi_client.run_process_group(
                "hpc2ckanv2",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="MergeContent",
                concurrent_tasks=concurrent_tasks_dict
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def hpc2ckan_2fa(
        self,
        hpc_host,
        hpc_username,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        data_source,
        ckan_resource=None,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HPC to CKAN using SFTP with a 2FA token

        Args:
            hpc_host (str): The HPC host URL.
            hpc_port (int): The port number for the HPC connection.
            hpc_username (str): The username for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The file path to the HPC secret key.
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            ckan_resource (str): The name of the CKAN resource
                to be created with the data.
            data_source (str): The source directory on the HPC
                whose data will be transferred.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.

        """
        return self._hpc2ckan_2fa_opt(
            hpc_host=hpc_host,
            hpc_username=hpc_username,
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            data_source=data_source,
            ckan_resource=ckan_resource,
            hpc_port=hpc_port,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key_path=hpc_secret_key_path,
            callback_2fa=callback_2fa,
            concurrent_tasks=concurrent_tasks
        )

    def _hpc2ckan_2fa_opt(
        self,
        hpc_host,
        hpc_username,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        data_source,
        ckan_resource=None,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HPC to CKAN using SFTP with a 2FA token
        using an optimized double pipeline

        Args:
            hpc_host (str): The HPC host URL.
            hpc_port (int): The port number for the HPC connection.
            hpc_username (str): The username for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The file path to the HPC secret key.
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            ckan_resource (str): The name of the CKAN resource
                to be created with the data.
            data_source (str): The source directory on the HPC
                whose data will be transferred.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.

        """
        args = SimpleNamespace(
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=None,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            data_source=data_source,
        )

        self.__logger.info(
            "executing hpc2ckan_2fa command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            hpc_filename = args.data_source[args.data_source.rfind("/") + 1 :]
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_FILENAME] = hpc_filename if hpc_filename else "*"
            arguments[HPC_FILENAME_REGEX] = self.process_wildcards(
                hpc_filename
            ) if hpc_filename else "[^\\s]+"
            arguments[HPC_DATA_FOLDER] = args.data_source[
                : args.data_source.rfind("/")
            ]
            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.generate_ckan_resource_name(args)

            # set local.data_folder to keep dataset retrieved from HDFS
            __uuid = uuid.uuid4()
            download_folder = os.path.join(
                self.__conf.nifi_download_folder(), str(__uuid)
            )
            self.__nifi_client.create_folder(download_folder)
            arguments[NIFI_DOWNLOAD_FOLDER] = download_folder

            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            processors_with_hpc_sensitive_parameters = \
                ["ListSFTP", "FetchSFTP"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_hpc_parameters(
                    processors_with_hpc_sensitive_parameters, args
                )

            processors_with_ckan_sensitive_parameters = ["CKANFileUploader"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key and not args.hpc_password:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            execution_type = {
                "GenerateFlowFile": ExecutionType.ONCE,
                "SftpTransferFromHPCWithVPNCode": ExecutionType.ONCE,
                "ListFile": ExecutionType.ONCE,
                "FetchFile": ExecutionType.FOREVER,
                "CKANFileUploader": ExecutionType.FOREVER,
            }

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "FetchFile": concurrent_tasks,
                "CKANFileUploader": concurrent_tasks,
            }

            process_ids = []
            process_id, _ = self.__nifi_client.run_process_group(
                "hpc2ckanwith2fa_part1",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                processor_with_2fa="SftpTransferFromHPCWithVPNCode",
                callback_2fa=callback_2fa,
            )
            process_ids.append(process_id)

            process_id, accounting_info = self.__nifi_client.run_process_group(
                "hpc2ckanwith2fa_part2",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                accounting_target="CKANFileUploader",
                concurrent_tasks=concurrent_tasks_dict,
            )
            process_ids.append(process_id)

            return '|'.join(process_ids), accounting_info

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def _hpc2ckan_2fa(
        self,
        hpc_host,
        hpc_username,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        data_source,
        ckan_resource=None,
        hpc_port=None,
        hpc_secret_key_password=None,
        hpc_secret_key_path=None,
        callback_2fa: Callable[[], str] = default_2fa_callback,
        concurrent_tasks: Optional[int] = None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from HPC to CKAN using SFTP with a 2FA token
        using a single non-optimized pipeline

        Args:
            hpc_host (str): The HPC host URL.
            hpc_port (int): The port number for the HPC connection.
            hpc_username (str): The username for the HPC connection.
            hpc_secret_key_password (str): The password for the HPC
            secret key.
            hpc_secret_key_path (str): The file path to the HPC secret key.
            ckan_host (str): The CKAN host URL.
            ckan_api_key (str): The CKAN API key.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            ckan_resource (str): The name of the CKAN resource
                to be created with the data.
            data_source (str): The source directory on the HPC
                whose data will be transferred.
            callback_2fa (str): a callback method to provide the 2FA token
                when invoked.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.
        """
        args = SimpleNamespace(
            hpc_host=hpc_host,
            hpc_port=hpc_port,
            hpc_username=hpc_username,
            hpc_password=None,
            hpc_secret_key_password=hpc_secret_key_password,
            hpc_secret_key=hpc_secret_key_path,
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            data_source=data_source,
        )

        self.__logger.info(
            "executing hpc2ckan_2fa command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            hpc_filename = args.data_source[args.data_source.rfind("/") + 1 :]
            arguments: Dict[str, Any] = {}
            self.__nifi_client.add_default_hpc_parameters(arguments, args)
            arguments[HPC_FILENAME] = hpc_filename if hpc_filename else "*"
            arguments[HPC_FILENAME_REGEX] = self.process_wildcards(
                hpc_filename
            ) if hpc_filename else "[^\\s]+"
            arguments[HPC_DATA_FOLDER] = args.data_source[
                : args.data_source.rfind("/")
            ]
            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.generate_ckan_resource_name(args)

            # set local.data_folder to keep dataset retrieved from HDFS
            __uuid = uuid.uuid4()
            download_folder = os.path.join(
                self.__conf.nifi_download_folder(), str(__uuid)
            )
            self.__nifi_client.create_folder(download_folder)
            arguments[NIFI_DOWNLOAD_FOLDER] = download_folder

            keys_arguments = {
                self.__nifi_client.HPC_SECRET_KEY_PATH: arguments[
                    self.__nifi_client.HPC_SECRET_KEY_PATH
                ],
            }

            processors_with_hpc_sensitive_parameters = \
                ["ListSFTP", "FetchSFTP"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_hpc_parameters(
                    processors_with_hpc_sensitive_parameters, args
                )

            processors_with_ckan_sensitive_parameters = ["CKANFileUploader"]
            sensitive_parameters.update(
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )
            )

            if not args.hpc_secret_key and not args.hpc_password:
                raise HidDataTransferException(HPC_ACCOUNT_MSG)

            execution_type = {
                "GenerateFlowFile": ExecutionType.ONCE,
                "SftpTransferFromHPCWithVPNCode": ExecutionType.ONCE,
                "RouteText": ExecutionType.ONCE,
                "ReplaceText": ExecutionType.ONCE,
                "SplitText": ExecutionType.ONCE,
                "ExtractText": ExecutionType.FOREVER,
                "UpdateAttribute": ExecutionType.FOREVER,
                "FetchFile": ExecutionType.FOREVER,
                "CKANFileUploader": ExecutionType.FOREVER,
            }

            # Set the number of concurrent tasks
            # for parallel processors in the pipeline
            if concurrent_tasks is None:
                concurrent_tasks = self.__conf.nifi_concurrent_tasks()
            concurrent_tasks_dict = {
                "FetchFile": concurrent_tasks,
                "CKANFileUploader": concurrent_tasks,
            }

            return self.__nifi_client.run_process_group(
                "hpc2ckanwith2fa",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                keycloak_token=self.__keycloak_token,
                processor_with_2fa="SftpTransferFromHPCWithVPNCode",
                callback_2fa=callback_2fa,
                accounting_target="CKANFileUploader",
                concurrent_tasks=concurrent_tasks_dict,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def local2ckan(
        self,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        data_source,
        ckan_resource=None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from local filesystem to CKAN using SFTP

        Args:
            ckan_host (str): The CKAN host URL.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            ckan_resource (str): The name of the CKAN resource
                to be created with the data.
            data_source (str): The directory on the local filesystem
                whose data will be transferred.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
            the data transfer process.
        """

        args = SimpleNamespace(
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            data_source=data_source,
        )

        self.__logger.info(
            "executing local2ckan command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        upload_folder = None
        try:
            local_regexp = \
                args.data_source[args.data_source.rfind("/") + 1 :]
            local_folder = args.data_source[: args.data_source.rfind("/")]

            arguments: Dict[str, Any] = {}

            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.generate_ckan_resource_name(args)

            # Transfer files from data source to NIFI upload subfolder
            # (within user folder)
            upload_folder, num_files = self.__nifi_client.upload_files(
                local_folder, local_regexp
            )
            if num_files == 0:
                raise HidDataTransferException(
                    f"No files found in {local_folder} "
                    "with pattern {local_regexp}"
                )
            arguments["local.folder"] = upload_folder
            arguments["local.numfiles"] = num_files

            keys_arguments: Dict[str, Any] = {}

            processors_with_ckan_sensitive_parameters = ["CKANFileUploader"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )

            execution_type = {
                "GetFile": ExecutionType.FOREVER,
                "MergeContent": ExecutionType.FOREVER,
                "UpdateAttribute": ExecutionType.ONCE,
                "CKANFileUploader": ExecutionType.ONCE,
            }

            return self.__nifi_client.run_process_group(
                "local2ckan",
                execution_type,
                arguments,
                keys_arguments,
                sensitive_parameters,
                first_processor_expected_outgoing_flowfiles=num_files,
                keycloak_token=self.__keycloak_token,
                accounting_target="MergeContent",
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex
        finally:
            # Remove uploaded files
            if upload_folder is not None:
                self.__nifi_client.remove_upload_folder(upload_folder)

    def ckan2local(
        self,
        ckan_host,
        ckan_api_key,
        ckan_organization,
        ckan_dataset,
        data_target,
        ckan_resource=None,
    ) -> tuple[str, AccountingInfo]:
        """
        transfer data from CKAN to the local filesystem using SFTP

        Args:
            ckan_host (str): The CKAN host URL.
            ckan_organization (str): The CKAN organization name.
            ckan_dataset (str): The CKAN dataset name.
            ckan_resource (str): The name of the CKAN resource to transfer.
            data_source (str): The  directory on the local filesystem
                where to transfer the data.
        Returns:
            str: The id(s) of the data tranfer NIFI process group(s).
            AccountingInfo: The information of the transferred data.
        Raises:
            HidDataTransferException: If an error occurs during
                the data transfer process.
        """

        args = SimpleNamespace(
            ckan_host=ckan_host,
            ckan_api_key=ckan_api_key,
            ckan_organization=ckan_organization,
            ckan_dataset=ckan_dataset,
            ckan_resource=ckan_resource,
            data_target=data_target,
        )

        self.__logger.info(
            "executing ckan2local command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )
        try:
            arguments: Dict[str, Any] = {}

            __uuid = uuid.uuid4()
            download_folder = os.path.join(
                self.__conf.nifi_download_folder(), str(__uuid)
            )
            self.__nifi_client.create_folder(download_folder)
            arguments[NIFI_DOWNLOAD_FOLDER] = download_folder

            self.__nifi_client.add_default_ckan_parameters(arguments, args)
            arguments[self.__nifi_client.CKAN_RESOURCE] = \
                self.process_wildcards(args.ckan_resource)

            keys_arguments: Dict[str, Any] = {}

            processors_with_ckan_sensitive_parameters = ["CKANFileDownloader"]
            sensitive_parameters = \
                self.__nifi_client.set_sensitive_ckan_parameters(
                    processors_with_ckan_sensitive_parameters, args
                )

            execution_type = {
                "CKANFileDownloader": ExecutionType.ONCE,
                "PutFile": ExecutionType.FOREVER,
            }

            process_group_id, accounting = \
                self.__nifi_client.run_process_group(
                    "ckan2local",
                    execution_type,
                    arguments,
                    keys_arguments,
                    sensitive_parameters,
                    keycloak_token=self.__keycloak_token,
                    accounting_target="PutFile",
                )

            # Transfer files from NIFI upload subfolder to the target folder

            self.__nifi_client.download_files(
                download_folder, args.data_target)

            sys.stdout.write(
                f"{args.ckan_resource} CKAN resource transferred to \
                {args.data_target} local folder\n"
            )

            return process_group_id, accounting

        except Exception as ex:
            raise HidDataTransferException(ex) from ex
        finally:
            # Remove uploaded files
            if download_folder is not None:
                self.__nifi_client.remove_download_folder(download_folder)

    def check_command_status(self, command_id):
        """
        Checks the status of a NIFI pipeline (process group) by ID

        Args:
            command_id (str): The id of the process group whose status
                is to be checked.
        Returns:
            Prints the status
        Raises:
            HidDataTransferException: If an error occurs
                while processing this method.
        """

        args = SimpleNamespace(
            command_id=command_id,
        )

        # Check process group state by id
        # This implies to check the execution state of
        # the last processor in the group
        self.__logger.info(
            "executing check_command_status command with args: %s",
            self.__nifi_client.format_args_to_string(args),
        )

        # Read arguments
        process_group_id = args.command_id

        try:
            # Get all processors in the process group
            processors = self.__nifi_client.get_process_group_processors(
                process_group_id
            )["processors"]

            # Order processor by pipeline sequence
            processors_sequence = self.__nifi_client.get_processors_sequence(
                process_group_id
            )
            processors = self.__nifi_client.order_processors(
                processors, processors_sequence
            )

            # Get status of last processor
            last_processor = processors[-1]

            if last_processor:
                state = \
                    self.__nifi_client.nifi_rest_client.get_processor_state(
                        last_processor, self.__nifi_client.get_access_token()
                    )
                # Get if there remains pending incoming flowfiles
                # to be processed
                are_all_flowfiles_consumed = (
                    self.__nifi_client
                    .are_all_processor_queued_flowfiles_consumed(
                        last_processor, process_group_id
                    )
                )
                if state == "STOPPED" and are_all_flowfiles_consumed:
                    state = "TERMINATED"
                else:
                    state = "RUNNING"

                sys.stdout.write(f"State of command {process_group_id} "
                                 "is {state}\n")
                # Determine if errors/warnings have been produced
                # in the process.
                # Get processors on group and display bulletins reports
                processors = self.__nifi_client.get_process_group_processors(
                    process_group_id
                )
                for processor in processors["processors"]:
                    bulletins = processor["bulletins"]
                    for _bulletin in bulletins:
                        # display bulletin
                        bulletin = _bulletin["bulletin"]
                        msg = (
                            f'{bulletin["level"]}: "{bulletin["message"]}" '
                            f'reported at {bulletin["timestamp"]} '
                            'by processor '
                            f'{bulletin["sourceName"]} '
                            'with id {bulletin["sourceId"]}\n'
                        )
                        sys.stderr.write(msg)
            else:
                raise HidDataTransferException(
                    f"Could not find last processor of command with id "
                    f"{process_group_id}"
                )
        except Exception as ex:
            raise HidDataTransferException(ex) from ex
        finally:
            self.__nifi_client.cancel_access_token()
