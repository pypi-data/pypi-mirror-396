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

This module defines the Keycloak API client class.
It provides methods to interface the Keycloak server to
authenticate users and retrieve tokens.
"""
from __future__ import annotations
from typing import Optional
from urllib.parse import urlparse, urlunparse, quote_plus
import threading
import requests
from hid_data_transfer_lib.conf.hid_dt_configuration import (
    HidDataTransferConfiguration
)
from hid_data_transfer_lib.exceptions.hid_dt_exceptions import (
    HidDataTransferException
)

# External Helper methods


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


class KeycloakRESTClient:
    """main Keycloak REST client class
    contains methods to interact with the remote Keycloak
    (taken from configuration)
    """

    # Requests constants
    __REQUEST_TIMEOUT = 60

    # Properties
    __token = None
    __refresh_token = None
    __expires_in = None
    __refresh_timer = None

    def __init__(self):
        """Constructor method"""
        self.__conf = None
        self.__keycloak_login = None
        self.__keycloak_endpoint = None
        self.__logger = None
        self.__refresh = False
        self.__refresh_timer = None

    def configure(
        self, conf: HidDataTransferConfiguration,
        secure: bool = False, refresh: bool = False
    ) -> KeycloakRESTClient:
        """constructs a API client,
        with the Keycloak endpoint taken from configuration
        """
        conf.check_keycloak_conf()
        self.__conf = conf
        self.__refresh = refresh
        self.__keycloak_login = conf.keycloak_login()
        self.__keycloak_endpoint = parse_base_url(
            self.__conf.keycloak_endpoint(), secure
        )
        self.__logger = self.__conf.logger("keycloak.keycloak_api")
        return self

    def info(self, *args):
        ''' do info logging'''
        if self.__conf.is_logger_valid(self.__logger):
            self.__logger.info(args)

    def debug(self, *args):
        ''' do debug logging'''
        if self.__conf.is_logger_valid(self.__logger):
            self.__logger.debug(args)

    def __del__(self):
        """Destructor method"""
        self.cancel_token(do_logging=False)

    def get_token(self):
        """Get a token that is renewed every time it expires"""
        if self.__token is None:
            self.info(
                "Getting Keycloak token for user", self.__keycloak_login
            )
            self.__get_token()
            self.debug(
                "Refreshed Keycloak token:", self.__token
            )
            if self.__refresh:
                self.__refresh_timer = threading.Timer(
                    self.__expires_in, self.refresh_token_periodically
                )
                self.__refresh_timer.start()
        return self.__token

    def set_token(self, user, token, expires_in, refresh_token):
        """Set the given token and renews it every time it expires"""
        self.__token = token
        self.__refresh_token = refresh_token
        self.__set_expires_in(expires_in)
        self.info(
            "Setting Keycloak token for user %s with given one", user
        )

        if self.__refresh:
            self.__refresh_timer = threading.Timer(
                self.__expires_in, self.refresh_token_periodically
            )
            self.__refresh_timer.start()

    def do_refresh_token(self, do_logging=True):
        """Refresh the token"""
        self.__get_refreshed_token()
        if do_logging:
            self.info(
                "Refreshing Keycloak token for user %s",
                self.__keycloak_login
            )

    def cancel_token(self, do_logging=True):
        """Cancel the token refresh timer"""
        if do_logging:
            self.info(
                "Cancelling the token refresh timer for user ",
                self.__keycloak_login,
            )
        self.__refresh = False
        self.__token = None
        if self.__refresh_timer is not None:
            self.__refresh_timer.cancel()

    def get_expires_in(self):
        """Get the expiration time of the token"""
        return self.__expires_in

    def __set_expires_in(self, expires_in):
        """Set value for __expires_in"""
        # Set as expires_in half of its value
        # To avoid token to get expired before it is refreshed
        self.__expires_in = expires_in / 2

    def refresh_token(self):
        """Get the refresh token"""
        return self.__refresh_token

    def keycloak_login(self):
        """Get the keycloak login"""
        return self.__keycloak_login

    def refresh_token_periodically(self):
        """Refresh the token with the expiration period
        given by the Keycloak server"""
        if self.__refresh:
            self.info(
                "Refreshing Keycloak token for user ", self.__keycloak_login
            )
            self.__get_refreshed_token()
            self.debug(
                "Refreshed Keycloak token: ", self.__token
            )
            self.__refresh_timer = threading.Timer(
                self.__expires_in, self.refresh_token_periodically
            )
            self.__refresh_timer.start()

    def __build_url(
        self, *paths: str, parameters: Optional[dict] = None
    ) -> str:
        """constructs a Keycloak query endpoint,
        appending paths and optional query parameters
        """
        url = "/".join(
            [self.__keycloak_endpoint.lstrip("/")] + [p.strip("/")
                                                      for p in paths]
        )
        if parameters is not None:
            parameter_len = len(parameters)
            url += "?"
            for i, (k, v) in enumerate(parameters.items()):
                url += k + "=" + str(v)
                if i < parameter_len - 1:
                    url += "&"
        return url

    def __get_token(self):
        """
        Obtains a JWT token from the Keycloak server
        This token is required to authenticate the user in the NIFI server
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        safe_password = quote_plus(self.__conf.keycloak_passwd())
        safe_client_secret = quote_plus(self.__conf.keycloak_client_secret())
        payload = (
            f"client_id={self.__conf.keycloak_client_id()}"
            f"&grant_type=password"
            f"&client_secret={safe_client_secret}"
            f"&scope=openid"
            f"&username={self.__keycloak_login}"
            f"&password={safe_password}"
        )
        response = requests.post(
            url=self.__build_url(
                "realms", "hidalgo2", "protocol", "openid-connect", "token"
            ),
            data=payload,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            self.__token = response.json()["access_token"]
            self.__refresh_token = response.json()["refresh_token"]
            self.__set_expires_in(response.json()["expires_in"])
        else:
            raise HidDataTransferException(
                f"Get Keycloak token exception: {response.content.decode()}"
            )

    def __get_refreshed_token(self):
        """
        Refresh a JWT token from the Keycloak server before it expires
        This token is required to authenticate the user in the NIFI server
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        safe_client_secret = quote_plus(self.__conf.keycloak_client_secret())
        payload = (
            f"client_id={self.__conf.keycloak_client_id()}"
            f"&grant_type=refresh_token"
            f"&client_secret={safe_client_secret}"
            f"&refresh_token={self.__refresh_token}"
        )
        response = requests.post(
            url=self.__build_url(
                "realms", "hidalgo2", "protocol", "openid-connect", "token"
            ),
            data=payload,
            verify=self.__conf.nifi_secure_connection(),
            headers=headers,
            timeout=self.__REQUEST_TIMEOUT,
        )
        if response.ok:
            self.__token = response.json()["access_token"]
            self.__refresh_token = response.json()["refresh_token"]
            self.__set_expires_in(response.json()["expires_in"])
        else:
            raise HidDataTransferException(
                f"Get Keycloak token exception: {response.content.decode()}"
            )
