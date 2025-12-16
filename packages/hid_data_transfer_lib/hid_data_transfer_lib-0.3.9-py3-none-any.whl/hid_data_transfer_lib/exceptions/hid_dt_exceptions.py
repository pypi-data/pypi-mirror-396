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

This module defines the exceptions for the Data Transfer CLI
"""


class HidDataTransferException(Exception):
    """Base class for Data Transfer CLI exceptions"""

    __produced_object = None

    def __init__(self, message, process_group_id=None):
        super().__init__(message)
        self.__process_group_id = process_group_id

    def produced_object(self):
        """Returns the object that was produced "
        "before the exception was raised"""
        return self.__produced_object

    def set_produced_object(self, produced_object):
        """Stores the object that was produced "
        "before the exception was raised"""
        self.__produced_object = produced_object

    def process_group_id(self):
        """Returns the process group id causing the exception"""
        return self.__process_group_id
