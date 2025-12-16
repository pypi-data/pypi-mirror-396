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


This module defines the NIFI REST client class.
It provides methods to interface the NIFI server to in instantiate templates,
and run processors in a process group.
"""
from __future__ import annotations
import json
from typing import Optional
import uuid
from urllib.parse import urlparse, urlunparse

import requests
from hid_data_transfer_lib.conf.hid_dt_configuration import (
    HidDataTransferConfiguration
)
from hid_data_transfer_lib.exceptions.hid_dt_exceptions import (
    HidDataTransferException
)


# External Helper methods
# TODO extract to a helper module
def parse_base_url(url, secure=False):
    """constructs an incomplete url with secure schema"""
    scheme = "https" if secure else "http"
    if "http" not in url:
        url = scheme + "://" + url
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.rstrip("/")
    if not parsed_url.scheme:
        netloc = scheme + "://" + netloc
    return urlunparse((scheme, netloc, "", "", "", ""))


class NIFIRESTClient:
    """main NIFI REST client class
    contains methods to interact with the remote NIFI
    (taken from configuration)
    """

    # Requests constants
    __REQUEST_TIMEOUT = 60
    __JSON_CONTENT_TYPE = "application/json"
    __TEXT_PLAIN_CONTENT_TYPE = "text/plain"

    def __init__(self):
        """initializes the NIFI REST client"""
        self.__conf = None
        self.__nifi_endpoint = None

    def configure(self, conf: HidDataTransferConfiguration,
                  secure: bool = False) -> NIFIRESTClient:
        """constructs a NIFI REST client,
        with the NIFI endpoint taken from configuration
        """
        conf.check_nifi_conf()
        self.__conf = conf
        self.__nifi_endpoint = parse_base_url(
            self.__conf.nifi_endpoint(), secure)
        return self

    def build_url(self, *paths: str, parameters: Optional[dict] = None) -> str:
        """constructs a NIFI query endpoint,
        appending paths and optional query parameters
        """
        url = "/".join(
            [self.__nifi_endpoint.lstrip("/")] + [p.strip("/") for p in paths]
        )
        if parameters is not None:
            parameter_len = len(parameters)
            url += "?"
            for i, (k, v) in enumerate(parameters.items()):
                url += k + "=" + str(v)
                if i < parameter_len - 1:
                    url += "&"
        return url

    def get_access_token(self) -> str:
        """gets the NIFI access token,
        using NIFI account taken from configuration
        this access token is required for any further request sent to NIFI
        """
        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(
                url=self.build_url("nifi-api", "access", "token"),
                data=f"username={self.__conf.nifi_login()}"
                f"&password={self.__conf.nifi_passwd()}",
                verify=self.__conf.nifi_secure_connection(),
                headers=headers,
                timeout=self.__REQUEST_TIMEOUT,
            )
            if not response.ok:
                error_message = (
                    "Authentication error, cannot get NIFI access token: "
                    f"{response.content.decode()}"
                )
                raise HidDataTransferException(error_message)
            return response.content.decode()
        except requests.exceptions.RequestException as e:
            raise HidDataTransferException(
                f"Authentication error, cannot get NIFI access token: {str(e)}"
            ) from e

    # GET requests

    def get_root_process_group(self, token) -> dict:
        """helper method to get the root process group"""
        url = self.build_url("nifi-api", "flow", "process-groups", "root")
        return self._get_entity(url, token)

    def process_group_get_request(self, group_id, token, entity=None) -> dict:
        """helper method to process a get request for a process group
        identified by id"""
        url = (
            self.build_url("nifi-api", "process-groups", group_id, entity)
            if entity
            else self.build_url("nifi-api", "process-groups", group_id)
        )
        return self._get_entity(url, token)

    def get_templates(self, token) -> dict:
        """helper method to get the templates registered in NIFI"""
        url = self.build_url("nifi-api", "flow", "templates")
        return self._get_entity(url, token)

    def get_registries(self, token) -> dict:
        """helper method to get the registries registered in NIFI"""
        url = self.build_url("nifi-api", "flow", "registries")
        return self._get_entity(url, token)

    def get_buckets(self, registry_id, token) -> dict:
        """helper method to get the buckers registered in NIFI Registry"""
        url = self.build_url("nifi-api", "flow", "registries",
                             registry_id, "buckets")
        return self._get_entity(url, token)

    def get_flow_definitions(self, registry_id, bucket_id, token) -> dict:
        """helper method to get the flow definitions
        registered in NIFI Registry bucket"""
        url = self.build_url(
            "nifi-api", "flow", "registries", registry_id,
            "buckets", bucket_id, "flows"
        )
        return self._get_entity(url, token)

    def get_flow_definition_versions(
        self, registry_id, bucket_id, flow_definition_id, token
    ) -> dict:
        """helper method to get the buckers registered in NIFI Registry"""
        url = self.build_url(
            "nifi-api",
            "flow",
            "registries",
            registry_id,
            "buckets",
            bucket_id,
            "flows",
            flow_definition_id,
            "versions",
        )
        return self._get_entity(url, token)

    def get_parameter_context(self, parameter_context_id, token) -> dict:
        """gets a parameter context identified by id"""
        url = self.build_url(
            "nifi-api",
            "parameter-contexts",
            parameter_context_id,
        )
        return self._get_entity(url, token)

    def _get_entity(self, url, token) -> dict:
        """gets an entity given by url"""
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            url=url,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            response_json = response.content.decode()
            return json.loads(response_json)
        else:
            raise HidDataTransferException(
                f"GET {url} exception: {response.content.decode()}"
            )

    def check_update_request_status(self, entity_id,
                                    request_id, token) -> bool:
        """checks the status of an update request identify by id
        for an entity identified by id
        """
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            url=self.build_url(
                "nifi-api",
                "parameter-contexts",
                entity_id,
                "update-requests",
                request_id,
            ),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.json()["request"]["complete"]
        else:
            raise HidDataTransferException(
                f"Check request status exception: {response.content.decode()}"
            )

    def get_processor(self, processor_id, token) -> dict:
        """gets a processor identified by id"""
        url = self.build_url("nifi-api", "processors", processor_id)
        return self._get_entity(url, token)

    def get_flowfile_queues_listing_requests(
            self, connection_id, listing_requests_id, token) -> dict:
        """gets a listing request for a processor identified by id"""
        url = self.build_url("nifi-api", "flowfile-queues", connection_id,
                             "listing-requests", listing_requests_id)
        return self._get_entity(url, token)['listingRequest']

    def get_flowfile_content(
            self, connection_id, flowfile_id, token) -> str:
        """gets the textual content of a flowfile identified by id"""
        url = self.build_url("nifi-api", "flowfile-queues", connection_id,
                             "flowfiles", flowfile_id, "content")
        headers = {
            "Content-Type": self.__TEXT_PLAIN_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            url=url,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            try:
                return response.content.decode()
            except UnicodeDecodeError:
                return "binary content"
        else:
            raise HidDataTransferException(
                f"GET {url} exception: {response.content.decode()}"
            )

    # POST requests

    def instantiate_template_as_process_group(self, template, token) -> dict:
        """creates a process group from a given template"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        root_group_id = template["template"]["groupId"]
        template_id = template["template"]["id"]
        payload = {"originX": 2.0, "originY": 3.0, "templateId": template_id}
        payload_json = json.dumps(payload)
        response = requests.post(
            url=self.build_url(
                "nifi-api", "process-groups",
                root_group_id, "template-instance"
            ),
            data=payload_json,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            response_json = response.content.decode()
            process_group_response = json.loads(response_json)
            process_group = process_group_response["flow"]["processGroups"][0]
            # Rename process_group as template_name + process_group_id
            template_name = template["template"]["name"]
            process_group = self.rename_process_group(
                process_group, template_name, token
            )
            process_group_response["flow"]["processGroups"][0] = process_group

            return process_group_response
        else:
            raise HidDataTransferException(
                "Instantiate template as process group exception: "
                f"{response.content.decode()}"
            )

    def instantiate_flow_definition_as_process_group(
        self, registry_id, bucket_id, flow_definition_id, version, token
    ) -> dict:
        """creates a process group from a given
        flow definition from the NIFI Registry"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "revision": {"version": 0},
            "disconnectedNodeAcknowledged": False,
            "component": {
                "position": {"x": 2.0, "y": 3.0},
                "versionControlInformation": {
                    "registryId": registry_id,
                    "bucketId": bucket_id,
                    "flowId": flow_definition_id,
                    "version": version,
                },
            },
        }
        payload_json = json.dumps(payload)
        root_process_group = self.get_root_process_group(token)
        root_group_id = root_process_group["processGroupFlow"]["id"]
        response = requests.post(
            url=self.build_url(
                "nifi-api",
                "process-groups",
                root_group_id,
                "process-groups",
                parameters={
                    "parameterContextHandlingStrategy": "KEEP_EXISTING"},
            ),
            data=payload_json,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            response_json = response.content.decode()
            process_group = json.loads(response_json)
            # Rename process_group as flow_definition_name + process_group_id
            process_group_name = process_group["component"]["name"]
            process_group = self.rename_process_group(
                process_group, process_group_name, token
            )
            return process_group
        else:
            raise HidDataTransferException(
                "Instantiate template as process group exception: "
                f"{response.content.decode()}"
            )

    def rename_process_group(self, process_group, name, token) -> str:
        """creates a process group from a given template"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        process_group_id = process_group["id"]
        process_group["component"]["name"] = name + "_" + process_group_id
        payload = json.dumps(process_group)
        response = requests.put(
            url=self.build_url("nifi-api", "process-groups", process_group_id),
            data=payload,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            response_json = response.content.decode()
            process_group = json.loads(response_json)
            return process_group
        else:
            raise HidDataTransferException(
                f"Process group rename exception: {response.content.decode()}"
            )

    def instantiate_parameter_context(self, token) -> dict:
        """creates a parameter context"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }

        client_id = str(uuid.uuid4())
        payload = {
            "component": {
                "name": f"Parameter_Context_{client_id}",
                "description": "",
                "parameters": [],
                "inheritedParameterContexts": [],
            },
            "revision": {"clientId": client_id, "version": 0},
        }
        payload_json = json.dumps(payload)
        response = requests.post(
            url=self.build_url("nifi-api", "parameter-contexts"),
            data=payload_json,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            response_json = response.content.decode()
            return json.loads(response_json)
        else:
            raise HidDataTransferException(
                "Instantiate parameter context exception: "
                f"{response.content.decode()}"
            )

    def initiate_update_request(self, entity_name,
                                entity, entity_id, token) -> str:
        """creates a update request, to modify any entity,
        given its name and id"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.post(
            url=self.build_url("nifi-api", entity_name,
                               entity_id, "update-requests"),
            data=entity,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.json()["request"]["requestId"]
        else:
            raise HidDataTransferException(
                "Initiate Request context exception: "
                f"{response.content.decode()}"
            )

    def post_flowfile_queues_listing_requests(
            self, connection_id, token) -> str:
        """initiates a flowfile queues listing request, for a connection
        given its id"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.post(
            url=self.build_url("nifi-api", "flowfile-queues",
                               connection_id, "listing-requests"),
            data={},
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.json()["listingRequest"]
        else:
            raise HidDataTransferException(
                "Initiate flowfile queues listing request exception: "
                f"{response.content.decode()}"
            )

    # PUT requests

    def associate_parameter_context_to_group(
        self, parameter_context, process_group, token
    ):
        """associates a parameter context to a process group"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "revision": {
                "version": process_group["revision"]["version"],
                # "clientId": parameter_context['revision']['clientId']
            },
            "disconnectedNodeAcknowledged": False,
            "component": {
                "id": process_group["id"],
                "name": process_group["component"]["name"],
                "comments": "",
                "parameterContext": {"id": parameter_context["id"]},
                "flowfileConcurrency": "UNBOUNDED",
                "flowfileOutboundPolicy": "STREAM_WHEN_AVAILABLE",
                "defaultFlowFileExpiration": "0 sec",
                "defaultBackPressureObjectThreshold": "10000",
                "defaultBackPressureDataSizeThreshold": "1 GB",
                "logFileSuffix": "",
            },
        }
        payload_json = json.dumps(payload)
        response = requests.put(
            url=self.build_url(
                "nifi-api",
                "process-groups",
                process_group["id"],
            ),
            verify=self.__conf.nifi_secure_connection(),
            data=payload_json,
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if not response.ok:
            raise HidDataTransferException(
                "Associate parameter context to group exception: "
                f"{response.content.decode()}"
            )

    def update_processor(self, processor, token) -> dict:
        """updates a processor identified by id"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.put(
            url=self.build_url("nifi-api", "processors", processor["id"]),
            verify=self.__conf.nifi_secure_connection(),
            data=json.dumps(processor),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            response_json = response.content.decode()
            return json.loads(response_json)
        else:
            raise HidDataTransferException(
                f"Processor exception: {response.content.decode()}"
            )

    # DELETE requests
    def delete_update_request(self, entity_name,
                              entity_id, request_id, token) -> bool:
        """deletes an update request create to inject
        modification in an entity"""
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.delete(
            url=self.build_url(
                "nifi-api", entity_name, entity_id,
                "update-requests", request_id
            ),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.ok
        else:
            raise HidDataTransferException(
                "Delete request context exception: "
                f"{response.content.decode()}"
            )

    def remove_parameter_context(self, parameter_context, token):
        """deletes a parameter context"""
        headers = {
            "Authorization": f"Bearer {token}",
        }
        parameters = {
            "disconnectedNodeAcknowledged": "false",
            "clientId": parameter_context["revision"]["clientId"],
            "version": parameter_context["revision"]["version"],
        }
        response = requests.delete(
            url=self.build_url(
                "nifi-api",
                "parameter-contexts",
                parameter_context["id"],
                parameters=parameters,
            ),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.ok
        else:
            raise HidDataTransferException(
                "Delete parameter context exception: "
                f"{response.content.decode()}"
            )

    def remove_process_group(self, process_group, token):
        """deletes a process group"""
        headers = {
            "Authorization": f"Bearer {token}",
        }
        parameters = {
            "disconnectedNodeAcknowledged": "false",
            "version": process_group["revision"]["version"],
        }
        response = requests.delete(
            url=self.build_url(
                "nifi-api", "process-groups",
                process_group["id"], parameters=parameters
            ),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.ok
        else:
            raise HidDataTransferException(
                f"Delete process group exception: {response.content.decode()}"
            )

    def request_empty_process_group_queues(self, process_group_id, token):
        ''' This method make a request to NIFI to empty
        all the queues in a process group'''
        request_id = None
        state = False

        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.post(
            url=self.build_url("nifi-api", "process-groups",
                               process_group_id,
                               "empty-all-connections-requests"),
            data={},
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            request_id = response.json()["dropRequest"]["id"]
            state = "Completed successfully" \
                in response.json()["dropRequest"]["state"]
        else:
            raise HidDataTransferException(
                "Exception creating request to empty a process group queues: "
                f"{response.content.decode()}"
            )

        return request_id, state

    def get_state_empty_process_group_queues_request(self, process_group_id,
                                                     request_id, token):
        ''' This method checks the status of a request to NIFI to empty
        all the queues in a process group'''
        state = None

        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            url=self.build_url(
                "nifi-api", "process-groups",
                process_group_id, "empty-all-connections-requests",
                request_id),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            state = "Completed successfully" in \
                response.json()["dropRequest"]["state"]
        else:
            raise HidDataTransferException(
                "Exception checking request to empty a process group queues: "
                f"{response.content.decode()}"
            )

        return state

    def remove_empty_process_group_queues_request(self, process_group_id,
                                                  request_id, token):
        ''' This method deletes a request to NIFI to empty
        all the queues in a process group'''
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.delete(
            url=self.build_url(
                "nifi-api", "process-groups",
                process_group_id, "empty-all-connections-requests",
                request_id),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.ok
        else:
            raise HidDataTransferException(
                "Exception deleting request to empty a process group queues: "
                f"{response.content.decode()}"
            )

    def stop_local_process_group(self, process_group_id, token):
        ''' This method request NIFI to stop
        the processors of a local process group'''
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }

        payload_json = {
                "id": process_group_id,
                "disconnectedNodeAcknowledged": False,
                "state": "STOPPED",
            }
        payload = json.dumps(payload_json)

        response = requests.put(
            url=self.build_url(
                "nifi-api", "flow", "process-groups", process_group_id),
            verify=self.__conf.nifi_secure_connection(),
            data=payload,
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return
        else:
            raise HidDataTransferException(
                "Exception stopping local process_group: "
                f"{response.content.decode()}"
            )

    def stop_remote_process_group(self, process_group_id, token):
        ''' This method request NIFI to stop
        the processors of a remote process group'''
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }

        payload_json = {
                "id": process_group_id,
                "state": "STOPPED",
                "disconnectedNodeAcknowledged": False,
            }
        payload = json.dumps(payload_json)

        response = requests.put(
            url=self.build_url(
                "nifi-api", "remote-process-groups", "process-group",
                process_group_id, "run-status"),
            verify=self.__conf.nifi_secure_connection(),
            data=payload,
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return
        else:
            raise HidDataTransferException(
                "Exception stopping remote process_group: "
                f"{response.content.decode()}"
            )

    def initiates_drop_request(self, connection_id, token):
        '''initiates a drop request to empty a connection queue'''
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.post(
            url=self.build_url("nifi-api", "flowfile-queues",
                               connection_id, "drop-requests"),
            data={},
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.json()["dropRequest"]["id"]
        else:
            raise HidDataTransferException(
                "Creating drop request exception: "
                f"{response.content.decode()}"
            )

    def check_drop_request_status(self, connection_id, drop_request_id, token):
        '''checks the status of a drop request'''
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            url=self.build_url(
                "nifi-api", "flowfile-queues",
                connection_id, "drop-requests", drop_request_id),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.json()["dropRequest"]["finished"]
        else:
            raise HidDataTransferException(
                "Check drop request status exception: "
                f"{response.content.decode()}"
            )

    def delete_drop_request(self, connection_id, drop_request_id, token):
        '''deletes a drop request'''
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.delete(
            url=self.build_url(
                "nifi-api", "flowfile-queues",
                connection_id, "drop-requests", drop_request_id),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.ok
        else:
            raise HidDataTransferException(
                f"Delete drop request exception: {response.content.decode()}"
            )

    def delete_flowfile_queues_listing_requests(self, connection_id,
                                                listing_request_id, token):
        '''deletes a listing request'''
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.delete(
            url=self.build_url(
                "nifi-api", "flowfile-queues",
                connection_id, "listing-requests", listing_request_id),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.ok
        else:
            raise HidDataTransferException(
                "Delete listing request exception: "
                f"{response.content.decode()}"
            )

    # MULTI-REQUESTS methods
    def change_processor_run_status(
        self, processor, token, run_type
    ) -> tuple[bool, str]:
        """run given processor with a given run type"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        client_id = (
            processor["revision"]["clientId"]
            if "clientId" in processor["revision"]
            else None
        )
        version = processor["revision"]["version"]
        process_id = processor["id"]
        payload = f'{{"state":"{run_type}",'
        if client_id:
            payload += (
                f'"revision": {{"clientId": "{client_id}", '
                f'"version":{version}}}}}'
            )
        else:
            payload += f'"revision": {{"version":{version}}}}}'
        response = requests.put(
            url=self.build_url("nifi-api", "processors",
                               process_id, "run-status"),
            data=payload,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        return response.ok, response.content.decode()

    def get_processor_state(self, processor, token) -> str:
        """get the state of a given processor"""
        headers = {
            "Content-Type": self.__JSON_CONTENT_TYPE,
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            url=self.build_url("nifi-api", "processors", processor["id"]),
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.json()["component"]["state"]
        else:
            raise HidDataTransferException(
                f"Get processor state exception: {response.content.decode()}"
            )
