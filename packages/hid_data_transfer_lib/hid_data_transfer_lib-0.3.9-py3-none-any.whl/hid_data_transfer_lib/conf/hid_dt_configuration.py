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

This module manages the configuration of the Data Transfer CLI
"""
from __future__ import annotations
import configparser
import os
import logging
from typing import Optional
from urllib.parse import urlparse
from hid_data_transfer_lib.exceptions.hid_dt_exceptions import (
    HidDataTransferException
)


class HidDataTransferConfiguration:
    """This class manages the configuration of the Data Transfer library"""

    __nifi_endpoint = None
    __nifi_server_user_name = None
    __nifi_server_private_key = None
    __nifi_upload_folder = None
    __nifi_download_folder = None
    __nifi_secure_connection = True
    __nifi_login = None
    __nifi_passwd = None
    __nifi_concurrent_tasks = 1

    __keycloak_endpoint = None
    __keycloak_client_id = None
    __keycloak_client_secret = None
    __keycloak_login = None
    __keycloak_passwd = None

    __check_status_sleep_lapse = 10  # seconds

    def __init__(self, logging_level: Optional[int] = logging.INFO):
        self.__logging_level = logging_level

    def check_keycloak_conf(self):
        """Check if keycloak configuration is valid"""
        if self.__keycloak_login is None:
            raise HidDataTransferException(
                "Keycloak login must be set in the configuration"
            )
        if self.__keycloak_passwd is None:
            raise HidDataTransferException(
                "Keycloak passwd must be set in the configuration"
            )
        if self.__keycloak_endpoint is None:
            raise HidDataTransferException(
                "Keycloak endpoint must be set in the configuration"
            )
        if self.__keycloak_client_id is None:
            raise HidDataTransferException(
                "Keycloak client id must be set in the configuration"
            )
        if self.__keycloak_client_secret is None:
            raise HidDataTransferException(
                "Keycloak client secret must be set in the configuration"
            )

    def check_nifi_conf(self):
        """Check if NIFI configuration is valid"""
        if self.__nifi_endpoint is None:
            raise HidDataTransferException(
                "NIFI endpoint must be set in the configuration"
            )
        if self.__nifi_upload_folder is None:
            raise HidDataTransferException(
                "NIFI upload folder must be set in the configuration"
            )
        if self.__nifi_download_folder is None:
            raise HidDataTransferException(
                "NIFI download must be set in the configuration"
            )

    def nifi_endpoint(self):
        """Returns the NIFI endpoint"""
        if self.__nifi_endpoint:
            return self.__nifi_endpoint
        else:
            raise HidDataTransferException(
                "NIFI endpoint is not set in the configuration"
            )

    def nifi_server(self):
        """Returns the NIFI server name"""
        if self.nifi_endpoint():
            return urlparse(self.nifi_endpoint()).netloc.split(":")[0]
        else:
            raise HidDataTransferException(
                "NIFI endpoint is not set in the configuration"
            )

    def nifi_login(self):
        """Returns the NIFI login name"""
        return self.__nifi_login

    def nifi_passwd(self):
        """Returns the NIFI login password"""
        return self.__nifi_passwd

    def nifi_secure_connection(self):
        """Returns the NIFI connection security"""
        return self.__nifi_secure_connection

    def nifi_concurrent_tasks(self):
        """Returns the NIFI concurrent tasks for parallel processors"""
        return self.__nifi_concurrent_tasks

    def nifi_upload_folder(self):
        """Returns the NIFI upload folder, where to copy files"""
        if self.__nifi_upload_folder:
            return self.__nifi_upload_folder
        else:
            raise HidDataTransferException(
                "NIFI upload folder is not set in the configuration"
            )

    def nifi_download_folder(self):
        """Returns the NIFI download folder, where to copy files from"""
        if self.__nifi_download_folder:
            return self.__nifi_download_folder
        else:
            raise HidDataTransferException(
                "NIFI download folder is not set in the configuration"
            )

    def nifi_server_user_name(self):
        """Returns the NIFI server ssh user name,
        required to copy secret files to NIFI server"""
        if self.__nifi_server_user_name:
            return self.__nifi_server_user_name
        else:
            raise HidDataTransferException(
                "NIFI server user name is not set in the configuration"
            )

    def nifi_server_private_key(self):
        """Returns the NIFI server ssh private key,
        required to copy secret files to NIFI server"""
        if self.__nifi_server_private_key:
            return self.__nifi_server_private_key
        else:
            raise HidDataTransferException(
                "NIFI server private key is not set in the configuration"
            )

    def keycloak_endpoint(self):
        """Returns the Keycloak server endpoint"""
        if self.__keycloak_endpoint:
            return self.__keycloak_endpoint
        else:
            raise HidDataTransferException(
                "Keycloak endpoint is not set in the configuration"
            )

    def keycloak_client_id(self):
        """Returns the Keycloak client id for NIFI"""
        if self.__keycloak_client_id:
            return self.__keycloak_client_id
        else:
            raise HidDataTransferException(
                "Keycloak client id for NIFI is not set in the configuration"
            )

    def keycloak_client_secret(self):
        """Returns the Keycloak secret for NIFI"""
        if self.__keycloak_client_secret:
            return self.__keycloak_client_secret
        else:
            raise HidDataTransferException(
                "Keycloak client secret for NIFI "
                "is not set in the configuration"
            )

    def keycloak_login(self):
        """Returns the NIFI login name"""
        return self.__keycloak_login

    def keycloak_passwd(self):
        """Returns the NIFI login password"""
        return self.__keycloak_passwd

    def logger(self, logger_name):
        """Returns the logging level"""
        return self.__set_logger(logger_name)

    def is_logger_valid(self, logger):
        """Check if the logger is valid:
        checks if the FileHandler file is still open
        """
        file_handler = self.__get_file_handler(logger)
        if file_handler is not None:
            return not file_handler.stream.closed
        else:
            return False

    def __get_file_handler(self, logger):
        '''Returns the FileHandler of the logger'''
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                return handler
        return None

    def check_status_sleep_lapse(self):
        """Returns the NIFI login name"""
        return self.__check_status_sleep_lapse

    def read_configuration(
        self,
        user_config_file: Optional[str] = None,
        user_config_dict: Optional[dict] = None
    ) -> configparser.RawConfigParser:
        """
        Reads the configuration file and returns a configparser object.
        """

        if user_config_file is not None and user_config_dict is not None:
            raise HidDataTransferException(
                (
                    "Only one of user_config_file or user_config_dict "
                    "should be provided"
                )
            )
        if user_config_file is None and user_config_dict is None:
            raise HidDataTransferException(
                "One of user_config_file or user_config_dict "
                "should be provided"
            )

        config = configparser.RawConfigParser()
        config_file = str(os.path.dirname(os.path.realpath(__file__))) + \
            "/hid_dt.cfg"
        config.read(config_file)
        if user_config_file is not None:
            config.read(user_config_file)
        if user_config_dict is not None:
            config.read_dict(user_config_dict)
        return config

    def configure(
        self,
        user_config_file: Optional[str] = None,
        user_config_dict: Optional[dict] = None,
        logging_level: Optional[int] = None
    ) -> HidDataTransferConfiguration:
        """
        Reads the configuration and sets this class' configuration values
        It reads the configuration
        from the default library configuration directory.
        If the user_config_file is provided, this files is read, and its values
        override those in the default configuration file.
        If the user_config_dict is provided, this dictionary is read,
        and its values override those in the default configuration file.
        Only one of user_config_file or user_config_dict should be provided.

        """
        config = self.read_configuration(user_config_file, user_config_dict)

        try:
            # NIFI section
            self.load_nifi_configuration(config)

            # Keycloak section
            self.load_keycloak_configuration(config)

            # Check if either NIFI or Keycloak login and password are set
            if (self.__nifi_login is None and self.__nifi_passwd is None) and (
                self.__keycloak_login is None and
                self.__keycloak_passwd is None
            ):
                raise HidDataTransferException(
                    "Either (KEYCLOAK_LOGIN and KEYCLOAK_PASSWORD) "
                    "or (NIFI_LOGIN and NIFI_PASSWORD) "
                    "environment variables must be set"
                )

            # Logging section
            if logging_level is not None:
                self.__logging_level = logging_level
            else:
                logging_level_str = config.get("Logging", "logging_level")
                self.__logging_level = getattr(
                    logging, logging_level_str.upper(), logging.INFO)

            # Network section
            self.__check_status_sleep_lapse = config.get(
                "Network", "check_status_sleep_lapse")

            # Network section
            self.__check_status_sleep_lapse = config.get(
                "Network", "check_status_sleep_lapse")

            # Network section
            self.__check_status_sleep_lapse = config.get(
                "Network", "check_status_sleep_lapse")

            return self

        except configparser.NoSectionError as ex:
            raise HidDataTransferException(
                "Error parsing CLI configuration file"
            ) from ex

    def load_keycloak_configuration(self, config):
        """Load Keycloak configuration from config file"""
        # Read Keycloak login and password from configuration
        self.__keycloak_login = config.get("Keycloak", "keycloak_login")
        self.__keycloak_passwd = config.get("Keycloak", "keycloak_password")
        if (self.__keycloak_login and self.__keycloak_passwd is None) or (
            self.__keycloak_login is None and self.__keycloak_passwd
        ):
            raise HidDataTransferException(
                "Both KEYCLOAK_LOGIN and KEYCLOAK_PASSWORD "
                "environment variables must be set"
            )

        # Read other keycloak configuration from config file
        if self.__keycloak_login or self.__keycloak_passwd:
            self.__keycloak_endpoint = config.get(
                "Keycloak", "keycloak_endpoint")
            if self.__keycloak_endpoint is None:
                raise HidDataTransferException(
                    "Could not find Keycloak endpoint in config file."
                )

            self.__keycloak_client_id = config.get(
                "Keycloak", "keycloak_client_id")
            if self.__keycloak_client_id is None:
                raise HidDataTransferException(
                    "Could not find Keycloak client id "
                    "for NIFI in config file."
                )

            keycloak_client_secret = config.get(
                "Keycloak", "keycloak_client_secret")
            if keycloak_client_secret is not None:
                self.__keycloak_client_secret = keycloak_client_secret
            else:
                raise HidDataTransferException(
                    "Could not find Keycloak client secret "
                    "for NIFI in config file."
                )

    def load_nifi_configuration(self, config):
        """Load NIFI configuration from config file"""
        self.__nifi_endpoint = config.get("Nifi", "nifi_endpoint")
        if self.__nifi_endpoint is None:
            raise HidDataTransferException(
                "Could not find Nifi endpoint in config file."
            )

        nifi_secure_connection = config.get("Nifi", "nifi_secure_connection")
        if nifi_secure_connection is not None:
            self.__nifi_secure_connection = \
                nifi_secure_connection.lower() == "true"
        else:
            self.__nifi_secure_connection = False

        self.__nifi_upload_folder = config.get("Nifi", "nifi_upload_folder")
        if self.__nifi_upload_folder is None:
            raise HidDataTransferException(
                "Could not find Nifi nifi_upload_folder in config file"
            )

        self.__nifi_download_folder = config.get(
            "Nifi", "nifi_download_folder")
        if self.__nifi_download_folder is None:
            raise HidDataTransferException(
                "Could not find Nifi nifi_download_folder in config file"
            )

        # Optional NIFI server account in case of local file transfer
        self.__nifi_server_user_name = config.get(
            "Nifi", "nifi_server_username")
        self.__nifi_server_private_key = config.get(
            "Nifi", "nifi_server_private_key")

        if (
            self.__nifi_server_user_name and
            self.__nifi_server_private_key is None
        ) or (self.__nifi_server_user_name is None and
              self.__nifi_server_private_key):
            raise HidDataTransferException(
                "Both NIFI_SERVER_USERNAME and NIFI_SERVER_PRIVATE_KEY "
                "environment variables must be set"
            )

        nifi_concurrent_tasks = config.get("Nifi", "nifi_concurrent_tasks")
        if nifi_concurrent_tasks is not None:
            self.__nifi_concurrent_tasks = int(nifi_concurrent_tasks)
        else:
            self.__nifi_concurrent_tasks = 1

    def __set_logger(self, logger_name):
        """
        Set up logging configuration
        """

        # Create a console handler
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging_level)

        # Create a file handler
        file_handler = logging.FileHandler("dtcli.log")
        file_handler.setLevel(self.__logging_level)

        # Create a formatter and set it for the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        # console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Get the root logger and set its level
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.__logging_level)

        # Add the custom filter to the root logger
        # class_filter = ClassFilter("KeycloakAPIClient")
        # package_filter = PackageFilter('keycloak')
        # logger.addFilter(package_filter)

        # Add the console handler to the logger
        # logger.addHandler(console_handler)
        if len(logger.handlers) == 0:
            logger.addHandler(file_handler)

        return logger


class ClassFilter(logging.Filter):
    """Class to filter log messages based on their class name"""

    def __init__(self, *class_names):
        super().__init__()
        self.class_names = class_names

    def filter(self, record):
        # Check if the log message is from one of the specified classes
        return any(class_name in record.name
                   for class_name in self.class_names)


class PackageFilter(logging.Filter):
    """Class to filter log messages based on their package name"""

    def __init__(self, *package_names):
        super().__init__()
        self.package_names = package_names

    def filter(self, record):
        # Check if the log message is from one of the specified packages
        return any(
            record.name.startswith(package_name)
            for package_name in self.package_names
        )
