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


This module defines the NIFI API client class.
It provides methods to interface the NIFI server to in instantiate templates,
and run processors in a process group.
"""
from __future__ import annotations
import glob
import json
import os
import sys
import uuid
import logging
import time
from enum import Enum
from time import sleep
from typing import Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from hid_data_transfer_lib.conf.hid_dt_configuration import (
    HidDataTransferConfiguration
)
from hid_data_transfer_lib.exceptions.hid_dt_exceptions import (
    HidDataTransferException
)
from hid_data_transfer_lib.keycloak.keycloak_rest import KeycloakRESTClient
from hid_data_transfer_lib.nifi.nifi_rest import NIFIRESTClient
from hid_data_transfer_lib.util.util import (
    order_process_group, sftp_get, sftp_put,
    ssh_create_folder, ssh_delete_file, ssh_delete_folder,
    ssh_list
)

HPC_2FA = "hpc.2fa"


# Helper functions
def is_binary_file(filename: str) -> bool:
    """
    Guess if a filename corresponds to a binary file based on its extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file is likely binary, False otherwise.
    """
    # List of common binary file extensions
    binary_extensions = [
        ".exe", ".dll", ".bin", ".dat", ".class", ".so", ".o", ".a",
        ".lib", ".dylib", ".jar", ".zip", ".tar", ".gz", ".tgz", ".bz2",
        ".xz", ".7z", ".iso", ".img", ".apk", ".msi", ".deb", ".rpm",
        ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"
    ]

    file_extension = filename.lower().rsplit(".", 1)[-1] \
        if "." in filename else ""
    return f".{file_extension}" in binary_extensions


def flatten_processors(processors: list):
    '''Flatten the pipeline processors list.'''
    flattened = []
    for sublist in processors:
        if isinstance(sublist, dict):
            flattened.append(sublist)
        else:
            flattened.extend(flatten_processors(sublist))
    return flattened


def compute_num_processors(processors: list) -> int:
    '''Compute the number of processors in the pipeline'''
    return len(flatten_processors(processors))


# Helper enums
# An enum describing the types of processor exectution, either once or forever
class ExecutionType(Enum):
    """An enum describing the types of processor exectution,
    either once or forever"""

    ONCE = "once"
    FOREVER = "forever"


# Helper classes
@dataclass
class AccountingInfo:
    """Data structure to hold accounting information for a data transfer"""
    pipeline_timespan: int
    flowfiles_sizes: dict[str, int]


class NIFIClient:
    """main NIFI API client class
    contains methods to interact with the remote NIFI
    (taken from configuration)
    """

    # Commands parameters
    HPC_HOST = "hpc.host"
    HPC_PORT = "hpc.port"
    HPC_USERNAME = "hpc.username"
    HPC_PASSWORD_PROPERTY = "Password"
    HPC_SECRET_KEY_PATH = "hpc.secret_key_path"
    HPC_SECRET_KEY_PATH_PASSWORD_PROPERTY = "Private Key Passphrase"
    CKAN_HOST = "ckan.host"
    CKAN_APIKEY_PROPERTY = "Api_Key"
    CKAN_ORGANIZATION = "ckan.organization"
    CKAN_PACKAGE = "ckan.package"
    CKAN_RESOURCE = "ckan.resource"
    CKAN_CONCURRENT_TASKS = "ckan.concurrent_tasks"
    KERBEROS_PASSWORD = "Kerberos Password"

    def __init__(self):
        """Constructor method"""
        self.__conf = None
        self.nifi_rest_client = None
        self.keycloak_rest_client = None
        self.__logger = None
        self.check_status_sleep_lapse = 1

    def configure(self, conf: HidDataTransferConfiguration,
                  secure: bool = False) -> NIFIClient:
        """constructs a NIFI client,
        with the NIFI endpoint taken from configuration
        """
        self.__conf = conf
        self.nifi_rest_client = NIFIRESTClient().configure(conf, secure)
        self.keycloak_rest_client = KeycloakRESTClient().configure(
            conf, secure, refresh=True)
        self.__logger = self.__conf.logger("nifi.v2.client")
        self.check_status_sleep_lapse = int(
            self.__conf.check_status_sleep_lapse())
        return self

    def get_access_token(self) -> str:
        """gets the NIFI access token,
        using NIFI account taken from configuration
        this access token is required for any further request sent to NIFI
        """
        if self.__conf.nifi_login() and self.__conf.nifi_passwd():
            return self.nifi_rest_client.get_access_token()
        elif self.__conf.keycloak_login() and self.__conf.keycloak_passwd():
            return self.keycloak_rest_client.get_token()
        else:
            raise HidDataTransferException(
                "NIFI or Keycloak login and password must be provided"
            )

    def set_access_token(self, keycloak_token):
        """sets the given JWT token for getting access to NIFI"""
        self.keycloak_rest_client.set_token(
            user=keycloak_token["username"],
            token=keycloak_token["token"],
            expires_in=keycloak_token["expires_in"],
            refresh_token=keycloak_token["refresh_token"],
        )
        return keycloak_token["token"]

    def cancel_access_token(self):
        """cancel the access token refresh timer in case of Keycloak"""
        if self.__conf.keycloak_login() and self.__conf.keycloak_passwd():
            self.keycloak_rest_client.cancel_token()

    def refresh_access_token(self):
        """Refresh the access token in case of Keycloak"""
        if self.__conf.keycloak_login() and self.__conf.keycloak_passwd():
            self.keycloak_rest_client.do_refresh_token()

    # GET requests

    def get_process_group(self, group_id) -> dict:
        """gets a process group identified by id"""
        return self.nifi_rest_client.process_group_get_request(
            group_id, self.token())

    def get_process_group_processors(self, group_id) -> dict:
        """gets the processors of a process group identified by id"""
        return self.nifi_rest_client.process_group_get_request(
            group_id, self.token(), "processors"
        )

    def get_process_group_connections(self, group_id) -> dict:
        """gets the connetions of a process group identified by id"""
        return self.nifi_rest_client.process_group_get_request(
            group_id, self.token(), "connections"
        )

    def get_processors_sequence(self, group_id) -> list:
        """computes the sequence of processors of a process group
        identified by id"""
        connections = self.get_process_group_connections(group_id)
        connections_pairs = []
        for connection in connections["connections"]:
            connections_pairs.append(
                [connection["sourceId"], connection["destinationId"]]
            )
        return order_process_group(connections_pairs)

    def get_processor_error_bulletins(self, processor_id):
        """Get the error bulletins of a processor identified by id"""
        # Retrieve current version of processor
        processor = self.nifi_rest_client.get_processor(
            processor_id, self.token())
        error_bulletins = []
        bulletins = processor["bulletins"]
        for _bulletin in bulletins:
            bulletin = _bulletin["bulletin"]
            if bulletin["level"] == "ERROR":
                error_bulletins.append(bulletin)
        return error_bulletins

    MAX_FLOWFILE_SIZE = 8192

    def get_connection_flowfiles_sizes(self, connection_id):
        '''
        Get the sizes of the flowfiles in a connection
        identified by id
        '''
        flowfiles_sizes = {}
        # Create a flowfile_queues listing_requests
        listing_requests = \
            self.nifi_rest_client.post_flowfile_queues_listing_requests(
                connection_id, self.token())
        # Get the flowfile queues listing_requests flowfile summaries
        listing_request = \
            self.nifi_rest_client.get_flowfile_queues_listing_requests(
                connection_id, listing_requests["id"], self.token())
        # For each flowfile summary, get the content
        for summary in listing_request["flowFileSummaries"]:
            flowfile_key = f"{summary["filename"]}"
            flowfile_size = summary["size"]
            flowfiles_sizes[flowfile_key] = flowfile_size
        # Delete the flowfile queues listing_requests
        self.nifi_rest_client.delete_flowfile_queues_listing_requests(
            connection_id, listing_requests["id"], self.token())

        return flowfiles_sizes

    def get_connection_flowfiles_content(self, connection_id):
        '''
        Get the content of the flowfiles in a connection
        identified by id
        '''

        flowfiles_content = {}
        # Create a flowfile_queues listing_requests
        listing_requests = \
            self.nifi_rest_client.post_flowfile_queues_listing_requests(
                connection_id, self.token())
        # Get the flowfile queues listing_requests flowfile summaries
        listing_request = \
            self.nifi_rest_client.get_flowfile_queues_listing_requests(
                connection_id, listing_requests["id"], self.token())
        # For each flowfile summary, get the content
        for summary in listing_request["flowFileSummaries"]:
            flowfile_id = summary["uuid"]
            flowfile_key = f"{summary["filename"]}({summary["uuid"]})"
            flowfile_size = summary["size"]
            flowfiles_content[flowfile_key] = "empty content or too large"
            # Get the content of the flowfile
            if (
                is_binary_file(summary["filename"]) or
                flowfile_size == 0 or
                flowfile_size > self.MAX_FLOWFILE_SIZE
            ):
                # Flowfile is empty or too large, no content to retrieve
                flowfiles_content[flowfile_key] = \
                    "binary file, empty file or too large"
                continue
            flowfile_content = self.nifi_rest_client.get_flowfile_content(
                connection_id, flowfile_id, self.token())
            flowfiles_content[flowfile_key] = flowfile_content
        # Delete the flowfile queues listing_requests
        self.nifi_rest_client.delete_flowfile_queues_listing_requests(
            connection_id, listing_requests["id"], self.token())

        return flowfiles_content

    # POST requests

    # PUT requests

    def update_parameters(self, parameter_context, arguments) -> bool:
        """updates the parameters of a parameter context
        arguments contains the parameters to inject in the context
        """
        parameters = parameter_context["component"]["parameters"]
        for _, (key, value) in enumerate(arguments.items()):
            self.add_parameter(parameters, key, value)

        parameter_context["component"]["parameters"] = parameters
        modified_parameter_context_json = json.dumps(parameter_context)
        return self.save_parameter_context(
            modified_parameter_context_json, parameter_context["id"],
        )

    def update_processor_property(
        self, processor, property_name, property_value
    ):
        """updates the property of a processor"""
        processor["component"]["config"]["properties"][property_name] = \
            property_value

    def update_processor_configuration(
        self, processor, configuration_name, configuration_value
    ):
        """updates the configuration of a processor"""
        processor["component"]["config"][configuration_name] = \
            configuration_value

    # DELETE requests

    # MULTI-REQUESTS methods

    def run_processor(self, execution_type, processor):
        """run a processor once or forever depending on the execution type"""
        ok, response = None, None
        processor_name = processor["component"]["name"]
        if execution_type[processor_name] == ExecutionType.ONCE:
            ok, response = self._run_processor_once(processor)
        elif execution_type[processor_name] == ExecutionType.FOREVER:
            ok, response = self._run_processor_forever(processor)
        else:
            raise HidDataTransferException(
                f"Incompatible execution type {execution_type[processor_name]}"
                f" for processor {processor_name}"
            )

        return ok, response

    def _run_processor_once(self, processor) -> tuple[bool, str]:
        """run once a given processor"""
        return self.nifi_rest_client.change_processor_run_status(
            processor, self.token(), "RUN_ONCE"
        )

    def _run_processor_forever(self, processor) -> tuple[bool, str]:
        """run a given processor until it is stopped"""
        return self.nifi_rest_client.change_processor_run_status(
            processor, self.token(), "RUNNING"
        )

    def stop_processor(self, processor) -> tuple[bool, str]:
        """stop a given processor"""
        return self.nifi_rest_client.change_processor_run_status(
            processor, self.token(), "STOPPED"
        )

    def are_all_processor_queued_flowfiles_consumed(
        self, processor, process_group_id
    ) -> bool:
        """Check if all queued flowfiles have been consumed by the processor"""
        # Get the process group connections
        connections = self.get_process_group_connections(
            process_group_id)[
            "connections"
        ]
        for connection in connections:
            if connection["destinationId"] == processor["id"]:
                if connection["status"]["aggregateSnapshot"][
                    "flowFilesQueued"
                ] == 0:
                    return True
                else:
                    return False
        raise HidDataTransferException(
            f"Incomming connection not found for processor {processor['id']}"
        )

    def has_processor_incoming_flowfiles(
        self, processor, process_group_id, accounting: bool = False
    ) -> tuple[bool, dict]:
        """Check if the processor has incoming flowfiles"""
        # Get the process group connections
        connections = self.get_process_group_connections(
            process_group_id)[
            "connections"
        ]
        #  Supported parallel execution of processors
        #  Therefore a joining processor may have multiple incoming connections
        flowfiles_sizes = {}
        has_incoming_ff = False
        found_connection = False
        for connection in connections:
            if connection["destinationId"] == processor["id"]:
                found_connection = True
                if connection["status"]["aggregateSnapshot"][
                    "flowFilesQueued"
                ] != 0:
                    # If accounting is enable, collect flowfile size
                    if accounting:
                        # Get flowfiles sizes
                        flowfiles_sizes.update(
                            self.get_connection_flowfiles_sizes(
                                connection['id'])
                        )

                    if self.__logger.isEnabledFor(logging.DEBUG):
                        # Get flowfiles content
                        flowfiles_content = \
                            self.get_connection_flowfiles_content(
                                connection['id'])
                        # Log flowfiles content
                        self.__logger.debug(
                            "Flowfiles content for processor "
                            f"{processor["component"]["name"]}"
                            f"/{processor['id']}:"
                        )
                        for key, value in flowfiles_content.items():
                            self.__logger.debug(
                                f"flowfile: {key}, "
                                f"flowfile content: {value}"
                            )
                    has_incoming_ff = True
        if found_connection:
            return has_incoming_ff, flowfiles_sizes
        else:
            raise HidDataTransferException(
                "Outcomming connection not found "
                f"for processor {processor['id']}"
            )

    def are_expected_outgoing_flowfiles_created(
        self,
        processor,
        process_group_id,
        expected_outgoing_flowfiles,
    ) -> bool:
        """Check if all expected outgoing flowfiles
        have been generated by the processor"""
        # Get the process group connections
        connections = self.get_process_group_connections(
            process_group_id)[
            "connections"
        ]
        for connection in connections:
            if connection["component"]["source"]["id"] == processor["id"]:
                return (
                    connection["status"]["aggregateSnapshot"][
                        "flowFilesQueued"
                    ] == expected_outgoing_flowfiles
                )
        raise HidDataTransferException(
            f"Outgoing connection not found for processor {processor['id']}"
        )

    def has_created_outgoing_flowfiles(
        self,
        processor,
        process_group_id,
    ) -> bool:
        """Check if at least one outgoing flowfile
        has been generated by the processor"""
        # Get the process group connections
        connections = self.get_process_group_connections(
            process_group_id)[
            "connections"
        ]
        for connection in connections:
            if connection["component"]["source"]["id"] == processor["id"]:
                return connection["status"]["aggregateSnapshot"][
                    "flowFilesQueued"
                ] > 0
        raise HidDataTransferException(
            f"Outgoing connection not found for processor {processor['id']}"
        )

    # Class helper methods

    def upload_keys(self, keys, process_group_id) -> dict:
        """upload keys into the NIFI server by using the user's access"""
        remote_keys = {}
        for key, value in keys.items():
            remote_keys[key] = self.upload_key(value, process_group_id)
        return remote_keys

    def set_key_arguments(self, arguments, remote_keys):
        """updates the key-type argument entries with the keys paths
        on the remote NIFI server
        """
        for key, _ in remote_keys.items():
            arguments[key] = remote_keys[key]

    def add_parameter(self, parameters, key, value):
        """add a parameter (k, v) to a dictionary of parameters"""
        parameters.append(
            {"parameter":
                {"name": key, "value": value}}
        )
        return parameters

    def order_processors(self, processors, processors_sequence):
        """order the processors list according to the sequence given"""
        ordered_processors = []
        for identifier in processors_sequence:
            if isinstance(identifier, list):  # Parallel processors
                found = []
                for proc_id in identifier:
                    proc = self.find_processor_by_id(processors, proc_id)
                    if proc is not None:
                        found.append(proc)
            else:  # Single processor
                found = self.find_processor_by_id(processors, identifier)
            if found and len(found) > 0:
                ordered_processors.append(found)
        return ordered_processors

    def find_processor_by_id(self, processors, identifier):
        """finds a processor identified by id
        in the given list of processors"""
        for processor in processors:
            if processor["id"] == identifier:
                return processor
        return None

    def find_flow_definition_by_name(self, flow_definition_name):
        """Find a flow definition, registered in the NIFI Registry, by name"""
        # Assuming there is only one registered Registry
        registries = self.nifi_rest_client.get_registries(self.token())
        assert registries is not None
        registry_id = registries["registries"][0]["id"]

        # Assuming there is only one registered Bucket
        buckets = self.nifi_rest_client.get_buckets(registry_id, self.token())
        assert buckets is not None
        bucket_id = buckets["buckets"][0]["id"]

        flow_definitions = self.nifi_rest_client.get_flow_definitions(
            registry_id, bucket_id, self.token()
        )
        assert flow_definitions is not None
        flow_definition_id = None
        for flow in flow_definitions["versionedFlows"]:
            if (
                flow["versionedFlow"]["flowName"].upper()
                == flow_definition_name.upper()
            ):
                flow_definition_id = flow["versionedFlow"]["flowId"]
                break

        if flow_definition_id is None:
            raise HidDataTransferException(
                f"Flow definition {flow_definition_name} not found"
            )

        versions = self.nifi_rest_client.get_flow_definition_versions(
            registry_id, bucket_id, flow_definition_id, self.token()
        )
        assert versions is not None
        # Take the latest verstion of the flow
        version = versions["versionedFlowSnapshotMetadataSet"][-1][
            "versionedFlowSnapshotMetadata"
        ]["version"]

        return {
            "registry_id": registry_id,
            "bucket_id": bucket_id,
            "flow_definition_id": flow_definition_id,
            "version": version,
        }

    def instantiate_process_group(
        self, flow_definition_name,
        arguments, keys_arguments
    ):
        """create a process group from a template
        and its associated parameter context"""
        try:
            # Get flow definition metadata by name
            flow_definition = self.find_flow_definition_by_name(
                flow_definition_name
            )

            # Instantiate flow definition as process group
            process_group = (
                self.nifi_rest_client.
                instantiate_flow_definition_as_process_group(
                    flow_definition["registry_id"],
                    flow_definition["bucket_id"],
                    flow_definition["flow_definition_id"],
                    flow_definition["version"],
                    self.token(),
                )
            )

            # Transfer keys to NIFI server
            if keys_arguments:
                remote_keys = \
                    self.upload_keys(keys_arguments, process_group["id"])
                self.set_key_arguments(
                    arguments, remote_keys
                )  # update arguments with locations of remote keys

            # Instantiate parameter context with parameters
            parameter_context = \
                self.nifi_rest_client.instantiate_parameter_context(
                    self.token()
                )

            # Update parameters
            ok = self.update_parameters(
                parameter_context, arguments)

            if not ok:
                raise HidDataTransferException(
                    f"Exception updating parameter context "
                    f"{parameter_context['id']}"
                )

            # Associate parameter context to process group
            self.nifi_rest_client.associate_parameter_context_to_group(
                parameter_context, process_group, self.token()
            )

            return process_group, parameter_context
        except Exception as ex:
            dtex = HidDataTransferException(ex)
            dtex.set_produced_object(process_group)
            raise dtex from ex

    def token(self):
        ''' Gets latest updated NIFI access token '''
        return self.get_access_token()

    def run_process_group(
        self,
        template_name,
        execution_type: dict,
        arguments,
        keys_arguments: Optional[dict] = None,
        sensitive_parameters: Optional[dict] = None,
        first_processor_expected_outgoing_flowfiles=None,
        keycloak_token=None,
        processor_with_2fa=None,
        callback_2fa=None,
        accounting_target: Optional[str] = None,
        concurrent_tasks: Optional[dict] = None,
    ) -> tuple[str, AccountingInfo]:
        """MAIN method to run a processor from a template identify by name
        The procedure is as follows:
        - The template is retrieved by name
        - A process group is created from the template
        - A parameter context is created
        - Parameters defined in  arguments are injected in the context
        - The context is associated to the process group
        - For each processor in the group, following the sequence flow,
          the processor is executed once or until it processes all pending
          flowfiles in ingoing connection queue.
          Following processor is executed
          after the termination of the previous one.
        """
        # Manage HPC secret keys
        # Secret key should be read from client side
        # (provided in secret_key_path as local path)
        # Then, transfer to NIFI server in volume
        # (remote path) mounted by NIFI image
        # Using the user account to NIFI server (ssh) to send the key by scp
        # So, this CLI method should read local private_key,
        # transfer the key to a NIFI server folder
        # with read permissions for NIFI account
        # Next, the key remote path is update in parameter private_key_path
        # sent to the NIFI server
        # Upon transfer completion, this key must be automatically removed
        # by this NIFI CLI
        # NOTE: place the key in remote NIFI server upload location,
        # with permissions for user rw only
        # where only the user and NIFI have access but no other users
        # PROCEDURE:
        # - Get user NIFI account from configuration (username, key_path)
        # - Get NIFI upload folder from configuration (e.g. /opt/nifi-data/)
        # - This folder (and root) should have nifi:nifi ownership
        # when mounted in NIFI container
        # - Transfer local key to upload folder in NIFI server
        # - Update private_key_path with remote key path
        # - once this process group ends remote the uploaded key

        # Uses execution_type attribute to determine whether each processor
        # in the group should be executed only once or forever
        # until all incoming flowfiles are consumed
        process_group = {}
        try:
            pipeline_creation_start_time = time.time()
            # Get access token, do not forget to cancel token refresh
            # when done with it
            if keycloak_token:
                self.set_access_token(keycloak_token)

            process_group, parameter_context = self.instantiate_process_group(
                template_name, arguments, keys_arguments,
            )
            self.__logger.info(
                "Process group %s created\n", process_group["id"])

            # Get all processors in the process group
            processors = self.get_process_group_processors(
                process_group["id"])["processors"]

            # For each processor in group ordered by the sequence,
            # execute processor once
            # Check previous processor has an running instance
            # before launching next one
            # Support parallel execution of processors
            # If case the pipeline flow is forked
            # (e.g. after a DistributedLoad processor),
            # take all next parallel processors as the next one in an array,
            # and connect the array to the next processor
            # that merges the parallel flows:
            # Example: [S1, S2, [P1, P2], S3]
            processors_sequence = self.get_processors_sequence(
                process_group["id"])
            processors = self.order_processors(processors, processors_sequence)
            index_processor = 0

            pipeline_creation_end_time = time.time()
            self.__logger.debug(
                "Pipeline created in %s seconds\n",
                round(
                    pipeline_creation_end_time - pipeline_creation_start_time,
                    1
                )
            )

            sys.stdout.write(
                f"{template_name} data transfer with id"
                f": {process_group['id']} initiated\n"
            )

            # Accounting initialization
            flowfile_sizes: dict[str, int] = {}
            pipeline_start_time = time.time()
            # Compute the number of processors in the pipeline
            num_processors = compute_num_processors(processors)
            for processor in processors:
                # Support sequential and parallel execution of processors
                # If case the pipeline flow is forked
                # (e.g. after a DistributedLoad processor),
                # the next processor should be an array.
                # When so, execute them all in parallel according
                # to the execution type, and check them individually
                # for the exhaustion of their incoming flowfiles.
                # Upon this condition, stop them all in parallel.

                processor_name = processor["component"]["name"]
                if concurrent_tasks is not None and \
                   processor_name in concurrent_tasks:
                    processor = self.set_processor_concurrent_tasks(
                        processor, concurrent_tasks[processor_name])

                if isinstance(processor, list):
                    accounting_results = self.run_parallel_processors(
                        processor,
                        template_name,
                        execution_type,
                        sensitive_parameters,
                        first_processor_expected_outgoing_flowfiles,
                        processor_with_2fa,
                        callback_2fa,
                        accounting_target,
                        process_group,
                        parameter_context,
                        num_processors,
                        index_processor
                    )
                    accounting = accounting_results[0][0]
                    if not accounting:
                        ff_sizes: dict[str, int] = {}
                    else:
                        ff_sizes = {}
                        ff_sizes.update(
                            *[result[1] for result in accounting_results]
                        )
                else:
                    accounting, ff_sizes = self.process_processor_execution(
                        processor,
                        template_name,
                        execution_type,
                        sensitive_parameters,
                        first_processor_expected_outgoing_flowfiles,
                        processor_with_2fa,
                        callback_2fa,
                        accounting_target,
                        process_group,
                        parameter_context,
                        num_processors,
                        index_processor,
                    )

                    if accounting:
                        flowfile_sizes = ff_sizes

                index_processor += len(processor) \
                    if isinstance(processor, list) else 1

            pipeline_end_time = time.time()

            sys.stdout.write(
                f"{template_name} data transfer with id"
                f": {process_group['id']} terminated\n"
            )

            accounting_info = AccountingInfo(
                pipeline_timespan=int(pipeline_end_time - pipeline_start_time),
                flowfiles_sizes=flowfile_sizes,
            )

            transfer_time = accounting_info.pipeline_timespan
            number_transfer_files = len(
                accounting_info.flowfiles_sizes)
            transfer_size = sum(
                accounting_info.flowfiles_sizes.values())/(1024*1024)
            transfer_rate = transfer_size / transfer_time
            msg = f"Transfer time: {transfer_time} s"
            self.__logger.debug(msg)
            msg = f"Transfer size: {transfer_size:.2f} MB"
            self.__logger.debug(msg)
            msg = f"Transfer rate: {transfer_rate:.2f} MB/s"
            self.__logger.debug(msg)
            msg = f"Number of transferred files: {number_transfer_files}"
            self.__logger.debug(msg)

            return process_group["id"], accounting_info
            # Process group and associate parameter context cannot be removed
            # until the process group ends its execution
            # A CLI method: cleanup available to remove them
            # given the process group id
        except Exception as ex:
            if process_group and "id" in process_group:
                raise HidDataTransferException(ex, process_group["id"]) from ex
            else:
                raise HidDataTransferException(ex) from ex
        finally:
            if process_group:
                # Refresh NIFI token before cleanup
                self.refresh_access_token()
                # Clean up the process group and associated parameter context
                self.clean_process_group_up(process_group["id"])
                self.__logger.info("Process group %s cleaned up\n",
                                   process_group["id"])
            self.cancel_access_token()

    def run_parallel_processors(self, processors, *args):
        """Run multiple processor executions in parallel"""
        with ThreadPoolExecutor(max_workers=len(processors)) as executor:
            # Submit all tasks
            futures = [
                executor.submit(
                    self.process_processor_execution, processor, *args
                )
                for processor in processors
            ]

            # Collect accounting results
            accounting_results = []
            for future in futures:
                try:
                    result = future.result()
                    accounting_results.append(result)
                except Exception as e:
                    self.__logger.error(f"Processor execution failed: {e}")
                    accounting_results.append(None)

        return accounting_results

    def process_processor_execution(
        self, processor, template_name, execution_type, sensitive_parameters,
        first_processor_expected_outgoing_flowfiles,
        processor_with_2fa, callback_2fa, accounting_target,
        process_group, parameter_context, num_processors,
        index_processor
    ):
        '''Process the execution of a processor'''
        processor_start_time = time.time()
        # Set sensitive processor properties
        processor = self.set_sensitive_processor_properties(
            sensitive_parameters, processor
        )

        # Set 2FA token in context parameter
        # for the processor if required
        self.set_2fa_token(processor, parameter_context,
                           processor_with_2fa, callback_2fa)

        # Run the processor once or forever
        # until all incoming flowfiles are consumed
        processor_name = processor["component"]["name"]

        ff_sizes = {}
        accounting = False
        if index_processor != 0:
            # Check processor has incoming flowfiles before running
            # Check if accounting is enabled
            # and this processor is the accounting target
            accounting = accounting_target == processor_name
            has_incoming_flowfiles, ff_sizes = \
                self.has_processor_incoming_flowfiles(
                    processor, process_group["id"],
                    accounting=accounting)
            if not has_incoming_flowfiles:
                raise HidDataTransferException(
                            f"Processor {processor_name} has no incoming "
                            "flowfiles to process"
                        )

        ok, response = self.run_processor(
                    execution_type, processor)
        if ok:
            self.wait_for_processor_completion(
                execution_type,
                index_processor,
                num_processors,
                processor,
                process_group["id"],
                first_processor_expected_outgoing_flowfiles,
            )
            self.__logger.debug(
                "Processor %s execution completed\n", processor_name
            )
        else:
            raise HidDataTransferException(
                f'Exception running processor {processor["id"]}'
                f" for group {template_name}"
                f" with message: {response}"
            )
        processor_end_time = time.time()
        self.__logger.debug(
            "Processor %s executed in %s seconds\n",
            processor_name,
            round(processor_end_time - processor_start_time, 1)
        )

        return accounting, ff_sizes

    def set_sensitive_processor_properties(
            self, sensitive_parameters, processor):
        """Set sensitive parameters for a processor"""
        processor_name = processor["component"]["name"]

        if sensitive_parameters and processor_name in sensitive_parameters:
            for key in sensitive_parameters[processor_name]:
                self.update_processor_property(
                    processor,
                    key,
                    sensitive_parameters[processor_name][key],
                )
            processor = self.nifi_rest_client.update_processor(
                processor, self.token())
        return processor

    def set_processor_concurrent_tasks(
            self, processor, concurrent_tasks):
        """Set concurrent tasks for a processor"""

        self.update_processor_configuration(
            processor,
            "concurrentlySchedulableTaskCount",
            concurrent_tasks,
        )
        processor = self.nifi_rest_client.update_processor(
            processor, self.token())
        return processor

    def set_2fa_token(self, processor, parameter_context,
                      processor_with_2fa, callback_2fa):
        '''Set the 2FA token in context parameter
        for the processor if required'''
        processor_name = processor["component"]["name"]
        if processor_with_2fa \
           and processor_name.lower() == processor_with_2fa.lower():
            if callback_2fa:
                token_2fa = callback_2fa()
                if token_2fa:
                    # Update parameters
                    arguments = {
                        HPC_2FA: token_2fa
                    }
                    ok = self.update_parameters(parameter_context, arguments)
                    if not ok:
                        raise HidDataTransferException(
                            f"Exception updating parameter context "
                            f"{parameter_context['id']}"
                        )
                else:
                    raise HidDataTransferException(
                        "2FA authentication token "
                        "was not provided when prompted"
                    )
            else:
                raise HidDataTransferException(
                    "2FA authentication token "
                    "callback function was not provided"
                )

    def wait_for_processor_completion(
        self,
        execution_type,
        index_processor,
        num_processors,
        processor,
        process_group_id,
        first_processor_expected_outgoing_flowfiles=None,
    ):
        """Wait for processor to complete its execution"""

        are_all_flowfiles_consumed = False
        status = "RUNNING"
        processor_name = processor["component"]["name"]
        while status != "STOPPED" and not are_all_flowfiles_consumed:
            # Check processor has consumed all queued flowfiles
            # First processor does not have incoming connections
            if index_processor != 0:
                are_all_flowfiles_consumed = (
                    self.are_all_processor_queued_flowfiles_consumed(
                        processor, process_group_id
                    )
                )
            else:
                # First processor does not have incoming connections
                # But it is expected to produce outcoming flowfiles
                # Mark are_all_flowfiles_consumed as True
                # when first processor has been executed FOREVER
                # and it has created all expected outcoming flowfiles
                if execution_type[processor_name] == ExecutionType.FOREVER:
                    are_all_flowfiles_consumed = (
                        self.are_expected_outgoing_flowfiles_created(
                            processor,
                            process_group_id,
                            first_processor_expected_outgoing_flowfiles,
                        )
                    )
            status = self.nifi_rest_client.get_processor_state(
                processor, self.token())
            # If processor is stopped and not the last one,
            # check it has produced at least one flowfile
            if (
                status == "STOPPED"
                and index_processor != (num_processors - 1)
                and not self.has_created_outgoing_flowfiles(
                    processor, process_group_id
                )
            ):
                raise HidDataTransferException(
                    f"Processor {processor_name} "
                    "has not produced outcoming flowfiles"
                )
            # Check if processor execution has failed with exception
            # Collect them all and raise a single exception
            error_bulletins = self.get_processor_error_bulletins(
                processor["id"])
            if error_bulletins:
                # Before raising an exception, stop the processor
                # if it is running for ever
                self.stop_forever_running_processor(
                    execution_type[processor_name], processor)
                # and empty the incoming queue
                self.empty_incoming_queue(processor, process_group_id)
                raise HidDataTransferException(
                    f"Processor {processor_name} has failed with exception: "
                    f"{error_bulletins}"
                )
            sleep(self.check_status_sleep_lapse)
        self.stop_forever_running_processor(
            execution_type[processor_name], processor)

    def stop_forever_running_processor(self, exec_type, processor):
        '''Stop a processor that is running forever'''
        # If processor has executed for ever, stop it
        if exec_type == ExecutionType.FOREVER:
            # Get current processor version
            processor = self.nifi_rest_client.get_processor(
                processor["id"], self.token())
            self.stop_processor(processor)

    def empty_incoming_queue(self, processor, process_group_id):
        '''Empty the incoming queue of a processor'''
        if not self.are_all_processor_queued_flowfiles_consumed(
                processor, process_group_id):
            # Get the process group connections
            connections = self.get_process_group_connections(
                process_group_id)["connections"]
            for connection in connections:
                if (connection["component"]["destination"]["id"]
                    == processor["id"]
                    and connection["status"]["aggregateSnapshot"]
                        ["flowFilesQueued"] != 0):  # Empty the queue
                    self.empty_queue(connection['id'])

    def add_default_hpc_parameters(self, arguments, args):
        """adds default parameters for HPC connection"""
        arguments[self.HPC_HOST] = args.hpc_host
        arguments[self.HPC_PORT] = args.hpc_port if args.hpc_port else 22
        arguments[self.HPC_USERNAME] = args.hpc_username
        arguments[self.HPC_SECRET_KEY_PATH] = args.hpc_secret_key

    def add_default_ckan_parameters(self, arguments, args):
        """adds default parameters for CKAN connection"""
        arguments[self.CKAN_HOST] = args.ckan_host
        arguments[self.CKAN_ORGANIZATION] = args.ckan_organization
        arguments[self.CKAN_PACKAGE] = args.ckan_dataset

    def set_sensitive_hpc_parameters(
        self, processors_with_hpc_sensitive_parameters, args
    ):
        """Set sensitive parameters for HPC connection"""
        sensitive_parameters = {}
        for processor in processors_with_hpc_sensitive_parameters:
            inner_sensitive_parameters = {}
            sensitive_parameters[processor] = inner_sensitive_parameters
            if args.hpc_password:
                inner_sensitive_parameters[self.HPC_PASSWORD_PROPERTY] = (
                    args.hpc_password
                )
            if args.hpc_secret_key_password:
                inner_sensitive_parameters[
                    self.HPC_SECRET_KEY_PATH_PASSWORD_PROPERTY
                ] = args.hpc_secret_key_password
        return sensitive_parameters

    def set_sensitive_ckan_parameters(
        self, processors_with_ckan_sensitive_parameters, args
    ):
        """Set sensitive parameters for CKAN connection"""
        sensitive_parameters = {}
        for processor in processors_with_ckan_sensitive_parameters:
            inner_sensitive_parameters = {}
            sensitive_parameters[processor] = inner_sensitive_parameters
            if args.ckan_api_key:
                inner_sensitive_parameters[self.CKAN_APIKEY_PROPERTY] = (
                    args.ckan_api_key
                )
        return sensitive_parameters

    def set_sensitive_hdfs_parameters(
        self, processors_with_hdfs_sensitive_parameters, args
    ):
        """Set sensitive parameters for HDFS connection"""
        sensitive_parameters = {}
        for processor in processors_with_hdfs_sensitive_parameters:
            inner_sensitive_parameters = {}
            sensitive_parameters[processor] = inner_sensitive_parameters
            if args.kerberos_password:
                inner_sensitive_parameters[self.KERBEROS_PASSWORD] = (
                    args.kerberos_password
                )
        return sensitive_parameters

    def clean_process_group_up(self, process_group_id, retry=True):
        """Clean up the process group and associated parameter context"""
        # Get process group
        process_group = self.get_process_group(process_group_id)

        try:
            # Remove transferred keys
            self.__logger.debug("Removing uploaded keys\n")
            self.remove_uploaded_keys(process_group["id"])

            # Get parameter context
            if "parameterContext" in process_group["component"]:
                # parameter context exists
                parameter_context_id = process_group["component"][
                    "parameterContext"
                ]["id"]
                parameter_context = self.nifi_rest_client. \
                    get_parameter_context(
                        parameter_context_id, self.token()
                    )

                # Remove parameter_context
                if parameter_context:
                    self.nifi_rest_client.remove_parameter_context(
                        parameter_context, self.token())

            # Remove process_group
            self.nifi_rest_client.remove_process_group(
                process_group, self.token())
        except HidDataTransferException:
            # If parameter context or process group cannot be removed, try
            # empty all process queues
            # stop any running processor
            # Then try again
            if retry:
                self.stop_process_group(
                    process_group["id"])
                self.empty_process_group_queues(
                    process_group["id"])
                self.clean_process_group_up(
                    process_group["id"], retry=False)

    def stop_process_group(self, process_group_id):
        ''' This method request NIFI to stop
        the processors of a process group'''
        # Stop local process_group
        self.nifi_rest_client.stop_local_process_group(
            process_group_id, self.token())
        # Stop remote process group
        self.nifi_rest_client.stop_remote_process_group(
            process_group_id, self.token())

    def empty_process_group_queues(self, process_group_id):
        ''' This method request NIFI to empty
        all the queues in a process group'''
        # Request empty all connections
        request_id, state = \
            self.nifi_rest_client.request_empty_process_group_queues(
                process_group_id, self.token())
        # Check request state
        attempts = 5
        while not state and attempts > 0:
            # wait and check again
            attempts -= 1
            sleep(self.check_status_sleep_lapse)
            state = \
                self.nifi_rest_client.get_state_empty_process_group_queues_request(
                    process_group_id,
                    request_id,
                    self.token()
                )

        # remove request
        self.nifi_rest_client.remove_empty_process_group_queues_request(
            process_group_id, request_id, self.token())

    def empty_queue(self, connection_id):
        """empties a connection queue"""
        # Create a drop request
        drop_request_id = self.nifi_rest_client.initiates_drop_request(
            connection_id, self.token())
        if drop_request_id:
            # Check status of drop request
            state = self.nifi_rest_client.check_drop_request_status(
                connection_id, drop_request_id, self.token()
            )
            attempts = 5
            while not state and attempts > 0:
                # wait and check again
                attempts -= 1
                sleep(self.check_status_sleep_lapse)
                state = self.nifi_rest_client.check_drop_request_status(
                    connection_id, drop_request_id, self.token()
                )
            # DELETE drop request once complete (or attempts exhausted)
            self.nifi_rest_client.delete_drop_request(
                connection_id, drop_request_id, self.token()
            )
            return state
        else:
            raise HidDataTransferException(
                f"Failed to empty the queue for connection_id: {connection_id}"
            )

    def save_parameter_context(
        self, parameter_context, parameter_context_id
    ) -> bool:
        """saves a parameter context identified by id"""
        # Initiates an update request
        request_id = self.nifi_rest_client.initiate_update_request(
            "parameter-contexts",
            parameter_context,
            parameter_context_id,
            self.token(),
        )
        if request_id:
            # Check status of update request
            state = self.nifi_rest_client.check_update_request_status(
                parameter_context_id, request_id, self.token()
            )
            attempts = 5
            while not state and attempts > 0:
                # wait and check again
                attempts -= 1
                sleep(self.check_status_sleep_lapse)
                state = self.nifi_rest_client.check_update_request_status(
                    parameter_context_id, request_id, self.token()
                )
            # DELETE update request once complete (or attempts exhausted)
            self.nifi_rest_client.delete_update_request(
                "parameter-contexts", parameter_context_id,
                request_id, self.token()
            )
            return state
        else:
            raise HidDataTransferException(
                "Failed to initiate update parameter context request"
            )

    def format_args_to_string(self, args):
        """Format dtcli command arguments to string for logging"""
        return " ".join(
            [
                (f"cka_host={args.ckan_host},"
                 if hasattr(args, "ckan_host") else ""),
                (
                    f"ckan_organization={args.ckan_organization},"
                    if hasattr(args, "ckan_organization")
                    else ""
                ),
                (
                    f"ckan_dataset={args.ckan_dataset},"
                    if hasattr(args, "ckan_dataset")
                    else ""
                ),
                (
                    f"ckan_resource={args.ckan_resource},"
                    if hasattr(args, "ckan_resource")
                    else ""
                ),
                (
                    f"data_source={args.data_source},"
                    if hasattr(args, "data_source")
                    else ""
                ),
                (
                    f"data_target={args.data_target},"
                    if hasattr(args, "data_target")
                    else ""
                ),
                (f"hpc_host={args.hpc_host},"
                 if hasattr(args, "hpc_host") else ""),
                (f"hpc_port={args.hpc_port},"
                 if hasattr(args, "hpc_port") else ""),
                (
                    f"hpc_username={args.hpc_username},"
                    if hasattr(args, "hpc_username")
                    else ""
                ),
                (
                    f"hpc_secret_key={args.hpc_secret_key},"
                    if hasattr(args, "hpc_secret_key")
                    else ""
                ),
                (
                    f"command_id={args.command_id},"
                    if hasattr(args, "command_id")
                    else ""
                ),
            ]
        )

    # Methods to upload/download files to/from the NIFI server

    def upload_key(self, key, process_group_id) -> str:
        """upload a single key into the NIFI server
        by using the user's access"""
        __uuid = uuid.uuid4()
        __key_name = f"{process_group_id}_{__uuid}"
        __target = os.path.join(
            self.__conf.nifi_upload_folder(), str(__key_name))
        ownership = f"{self.__conf.nifi_server_user_name()}:nifi"
        sftp_put(
            server=self.__conf.nifi_server(),
            private_key=self.__conf.nifi_server_private_key(),
            username=self.__conf.nifi_server_user_name(),
            target_permissions="660",
            target_ownership=ownership,
            source=key,
            target=__target,
        )
        # Check if the key is accompanied by a certificate in the same folder
        # If so, upload the certificate as well
        cert_prefix = "-cert.pub"
        if os.path.exists(os.path.expanduser(key) + cert_prefix):
            __target_cert = os.path.join(
                self.__conf.nifi_upload_folder(),
                str(__key_name) + cert_prefix)
            sftp_put(
                server=self.__conf.nifi_server(),
                private_key=self.__conf.nifi_server_private_key(),
                username=self.__conf.nifi_server_user_name(),
                target_permissions="660",
                target_ownership=ownership,
                source=key + cert_prefix,
                target=__target_cert,
            )

        return __target

    def upload_files(self, local_folder: str,
                     local_regexp: str) -> tuple[str, int]:
        """Upload files from the local folder to the NIFI upload subfolder."""
        # TODO investigate parallel upload using threads
        __uuid = uuid.uuid4()
        upload_folder = os.path.join(
            self.__conf.nifi_upload_folder(), str(__uuid))
        # Create upload folder in the NIFI server
        self.create_folder(upload_folder)
        # Read files in local_folder that matches the local_regexp
        num_files = 0
        for file in self.find_files(local_folder, local_regexp):
            num_files += 1
            target = os.path.join(upload_folder, os.path.basename(file))
            sftp_put(
                server=self.__conf.nifi_server(),
                private_key=self.__conf.nifi_server_private_key(),
                username=self.__conf.nifi_server_user_name(),
                target_permissions="660",
                target_ownership=f"{self.__conf.nifi_server_user_name()}:nifi",
                source=file,
                target=target,
            )
        return upload_folder, num_files

    def download_files(self, download_folder, target_folder):
        """Download files from the NIFI server to the local folder."""
        remote_files = ssh_list(
            server=self.__conf.nifi_server(),
            path=download_folder,
            username=self.__conf.nifi_server_user_name(),
            private_key=self.__conf.nifi_server_private_key(),
        )
        for file in remote_files:
            local_file = os.path.join(target_folder, os.path.basename(file))
            sftp_get(
                source=file,
                server=self.__conf.nifi_server(),
                username=self.__conf.nifi_server_user_name(),
                private_key=self.__conf.nifi_server_private_key(),
                target=local_file,
            )

    def find_files(self, local_folder: str, local_regexp: str) -> list[str]:
        """Find files in a local folder that match a regular expression."""
        if local_regexp == "":
            local_regexp = "*"
        pattern = os.path.join(local_folder, local_regexp)
        return glob.glob(pattern)

    def create_folder(self, upload_folder: str) -> None:
        """Create an upload folder in the NIFI server"""
        ssh_create_folder(
            folder=upload_folder,
            server=self.__conf.nifi_server(),
            username=self.__conf.nifi_server_user_name(),
            private_key=self.__conf.nifi_server_private_key(),
        )

    def remove_download_folder(self, download_folder):
        """Delete an download folder in the NIFI server"""
        ssh_delete_folder(
            folder=download_folder,
            server=self.__conf.nifi_server(),
            username=self.__conf.nifi_server_user_name(),
            private_key=self.__conf.nifi_server_private_key(),
        )

    def remove_upload_folder(self, upload_folder: str) -> None:
        """Remove an upload folder in the NIFI server"""
        # Add your implementation here
        ssh_delete_folder(
            folder=upload_folder,
            server=self.__conf.nifi_server(),
            username=self.__conf.nifi_server_user_name(),
            private_key=self.__conf.nifi_server_private_key(),
        )

    def remove_uploaded_keys(self, process_group_id):
        """deletes the keys uploaded into the NIFI server"""
        # find all keys uploaded in the NIFI server
        # corresponding to the process group
        remote_keys = ssh_list(
            path=self.__conf.nifi_upload_folder(),
            server=self.__conf.nifi_server(),
            username=self.__conf.nifi_server_user_name(),
            private_key=self.__conf.nifi_server_private_key(),
            prefix=process_group_id,
        )
        for file in remote_keys:
            self.remove_uploaded_key(file)

    def remove_uploaded_key(self, remote_key):
        """deletes a keys uploaded into the NIFI server"""
        ssh_delete_file(
            server=self.__conf.nifi_server(),
            private_key=self.__conf.nifi_server_private_key(),
            username=self.__conf.nifi_server_user_name(),
            file=remote_key,
        )
