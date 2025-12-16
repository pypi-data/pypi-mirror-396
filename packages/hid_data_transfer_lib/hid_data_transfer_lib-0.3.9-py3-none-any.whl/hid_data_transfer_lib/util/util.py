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


This module provides a number of utility functions that are used by the CLI
"""

import os
from typing import Optional
import paramiko
from hid_data_transfer_lib.exceptions.hid_dt_exceptions import (
    HidDataTransferException
)


def order_process_group(connections):
    """Order a sequence of processors from an array of connections"""
    # Build a connections mapping
    # Support parallel connections by using a inner dictionary
    connections_mapping = {}
    for pair in connections:
        if pair[0] not in connections_mapping:
            connections_mapping[pair[0]] = pair[1]
        else:
            # If the key already exists, we assume it's a parallel connection
            connections_mapping[pair[0]] = {
                connections_mapping[pair[0]],
                pair[1]
            }

    # Find the starting processor (an element that is only a key, not a value)
    all_values = {pair[1] for pair in connections}
    start_processor = None
    for key in connections_mapping.keys():
        if key not in all_values:
            start_processor = key
            break

    if start_processor is None:
        raise ValueError(
            "No valid starting processor for process group ordering")

    # Traverse the mapping to construct the sorted processors sequence
    sorted_process_group = [start_processor]
    while start_processor in connections_mapping:
        start_processor = connections_mapping[start_processor]
        if isinstance(start_processor, set):  # Parallel connections
            sorted_process_group.append(list(start_processor))
            # Get one of the parallel connections
            start_processor = next(iter(start_processor))
        else:
            sorted_process_group.append(start_processor)

    return sorted_process_group


def flatten(sequence):
    """Flatten a nested list into a single list"""
    result = []
    for elem in sequence:
        if isinstance(elem, list):
            for item in elem:
                result.append(item)
        else:
            result.append(elem)
    return result


def swap(sequence, index1, index2):
    """Swap two elements in a list at the given indices"""
    sequence[index1], sequence[index2] = sequence[index2], sequence[index1]
    return sequence


def get_index(target, sequence) -> Optional[int]:
    """Get the index of an element in a list or nested list"""
    for index, elem in enumerate(sequence):
        if isinstance(elem, list):
            if target in elem:
                return index
        else:
            if target == elem:
                return index
    return None


def sftp_put(
    server,
    source,
    target,
    username,
    private_key=None,
    target_permissions=None,
    target_ownership=None,
):
    """Transfer a file from the local machine to a remote server using SFTP"""
    if source.startswith("~"):
        source = os.path.expanduser(os.path.join(*source.split("/")))
    if private_key.startswith("~"):
        private_key = os.path.expanduser(os.path.join(*private_key.split("/")))
    with paramiko.SSHClient() as ssh:
        ssh.load_host_keys(os.path.expanduser(
            os.path.join("~", ".ssh", "known_hosts")))
        if not private_key:
            ssh.connect(server, username=username)
        else:
            ssh.connect(server, username=username, key_filename=private_key)
        with ssh.open_sftp() as sftp:
            sftp.put(source, target)
            if target_permissions:
                command = f"chmod {target_permissions} {target}"
                ssh.exec_command(command)
            if target_ownership:
                command = f"chown {target_ownership} {target}"
                ssh.exec_command(command)


def sftp_get(server, source, target, username, private_key=None):
    """Transfer a file from a remote server to the local machine using SFTP"""
    if target.startswith("~"):
        target = os.path.expanduser(os.path.join(*target.split("/")))
    if private_key.startswith("~"):
        private_key = os.path.expanduser(os.path.join(*private_key.split("/")))
    with paramiko.SSHClient() as ssh:
        ssh.load_host_keys(os.path.expanduser(
            os.path.join("~", ".ssh", "known_hosts")))
        if not private_key:
            ssh.connect(server, username=username)
        else:
            ssh.connect(server, username=username, key_filename=private_key)
        with ssh.open_sftp() as sftp:
            sftp.get(remotepath=source, localpath=target)


def ssh_delete_file(file, server, username, private_key=None):
    """Delete a file on a remote server using SSH"""
    command = f"rm {file}"
    __ssh_execute_command(server, username, command, private_key)


def ssh_create_folder(folder, server, username, private_key=None):
    """Delete a file on a remote server using SSH"""
    command = f"mkdir -p {folder}"
    __ssh_execute_command(server, username, command, private_key)

    # set ownership and permissions
    ownership_command = f"chown {username}:nifi {folder}"
    __ssh_execute_command(server, username, ownership_command, private_key)
    permissions_command = f"chmod 775 {folder}"
    __ssh_execute_command(server, username, permissions_command, private_key)


def ssh_delete_folder(folder, server, username, private_key=None):
    """Delete a file on a remote server using SSH"""
    command = f"rm -rf {folder}"
    __ssh_execute_command(server, username, command, private_key)


def __ssh_execute_command(server, username, command, private_key=None):
    """Execute a command on a remote server using SSH"""
    if private_key.startswith("~"):
        private_key = os.path.expanduser(os.path.join(*private_key.split("/")))
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(
            os.path.join("~", ".ssh", "known_hosts")))
        if not private_key:
            ssh.connect(server, username=username)
        else:
            ssh.connect(server, username=username, key_filename=private_key)
        _, _, stderr = ssh.exec_command(command)
        error = stderr.read().decode("utf-8")
        if error:
            raise HidDataTransferException(
                f"Error '{error}' executing command '{command}'"
            )


# list all files in path starting with prefix
def ssh_list(path, server, username, private_key=None, prefix=None) -> list:
    """List files on a remote server using SSH"""
    if private_key.startswith("~"):
        private_key = os.path.expanduser(os.path.join(*private_key.split("/")))
    with paramiko.SSHClient() as ssh:
        ssh.load_host_keys(os.path.expanduser(
            os.path.join("~", ".ssh", "known_hosts")))
        if not private_key:
            ssh.connect(server, username=username)
        else:
            ssh.connect(server, username=username, key_filename=private_key)
        if prefix is not None:
            command = (
                f'find {path} -maxdepth 1 '
                f'-name "{prefix}*" -type f -printf "%p\n"'
            )
        else:
            command = f'find {path} -maxdepth 1 -type f -printf "%p\n"'
        _, stdout, _ = ssh.exec_command(command)

        # read lines from stdout in a list
        files = []
        for line in stdout:
            files.append(line.strip())
        return files
