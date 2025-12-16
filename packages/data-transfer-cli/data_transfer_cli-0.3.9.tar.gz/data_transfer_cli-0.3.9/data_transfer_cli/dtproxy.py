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

from hid_data_transfer_lib.exceptions.hid_dt_exceptions import HidDataTransferException
from hid_data_transfer_lib.conf.hid_dt_configuration import HidDataTransferConfiguration
from hid_data_transfer_lib.hid_dt_lib import HIDDataTransfer, AccountingInfo


class DataTransferProxy:
    """interface to the hid_data_transfer_lib to run data transfer commands"""

    def __init__(
        self, conf: HidDataTransferConfiguration, secure: bool = False
    ) -> None:
        """constructs a data transfer client,"""
        self.__conf = conf
        self.dt_client = HIDDataTransfer(conf=conf, secure=secure)
        self.__logger = self.__conf.logger("nifi.v2.client")

    def format_args_to_string(self, args):
        """Format dtcli command arguments to string for logging"""
        return " ".join(
            [
                f"ckan_host={args.ckan_host}," if hasattr(args, "ckan_host") else "",
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
                f"hpc_host={args.hpc_host}," if hasattr(args, "hpc_host") else "",
                f"hpc_port={args.hpc_port}," if hasattr(args, "hpc_port") else "",
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
                f"command_id={args.command_id}," if hasattr(args, "command_id") else "",
            ]
        )

    # MAIN CLI commands

    def hdfs2hpc(self, args) -> tuple[str, AccountingInfo]:
        """transfer data from HDFS to hpc using SFTP"""
        self.__logger.info(
            "executing hdfs2hpc command with args: %s", self.format_args_to_string(args)
        )
        try:
            # Check if 2FA is enabled
            if args.two_factor_authentication:
                return self.dt_client.hdfs2hpc_2fa(
                    hpc_host=args.hpc_host,
                    hpc_port=args.hpc_port,
                    hpc_username=args.hpc_username,
                    hpc_secret_key_path=args.hpc_secret_key,
                    hpc_secret_key_password=args.hpc_secret_key_password,
                    data_source=args.data_source,
                    data_target=args.data_target,
                    kerberos_principal=args.kerberos_principal,
                    kerberos_password=args.kerberos_password,
                    concurrent_tasks=args.concurrent_tasks,
                )
            return self.dt_client.hdfs2hpc(
                hpc_host=args.hpc_host,
                hpc_port=args.hpc_port,
                hpc_username=args.hpc_username,
                hpc_password=args.hpc_password,
                hpc_secret_key_path=args.hpc_secret_key,
                hpc_secret_key_password=args.hpc_secret_key_password,
                data_source=args.data_source,
                data_target=args.data_target,
                kerberos_principal=args.kerberos_principal,
                kerberos_password=args.kerberos_password,
                concurrent_tasks=args.concurrent_tasks,
                recursive=args.recursive,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def hpc2hdfs(self, args) -> tuple[str, AccountingInfo]:
        """transfer data from HPC to hdfs using SFTP"""
        self.__logger.info(
            "executing hpc2hdfs command with args: %s", self.format_args_to_string(args)
        )
        try:
            # Check if 2FA is enabled
            if args.two_factor_authentication:
                return self.dt_client.hpc2hdfs_2fa(
                    hpc_host=args.hpc_host,
                    hpc_port=args.hpc_port,
                    hpc_username=args.hpc_username,
                    hpc_secret_key_path=args.hpc_secret_key,
                    hpc_secret_key_password=args.hpc_secret_key_password,
                    data_source=args.data_source,
                    data_target=args.data_target,
                    kerberos_principal=args.kerberos_principal,
                    kerberos_password=args.kerberos_password,
                    concurrent_tasks=args.concurrent_tasks,
                )
            return self.dt_client.hpc2hdfs(
                    hpc_host=args.hpc_host,
                    hpc_port=args.hpc_port,
                    hpc_username=args.hpc_username,
                    hpc_password=args.hpc_password,
                    hpc_secret_key_path=args.hpc_secret_key,
                    hpc_secret_key_password=args.hpc_secret_key_password,
                    data_source=args.data_source,
                    data_target=args.data_target,
                    kerberos_principal=args.kerberos_principal,
                    kerberos_password=args.kerberos_password,
                    concurrent_tasks=args.concurrent_tasks,
                    recursive=args.recursive,
                )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def hdfs2ckan(self, args) -> tuple[str, AccountingInfo]:
        """transfer data from HDFS to CKAN using SFTP"""
        self.__logger.info(
            "executing hpc2ckan command with args: %s", self.format_args_to_string(args)
        )
        try:
            return self.dt_client.hdfs2ckan(
                ckan_host=args.ckan_host
                if args.ckan_host.startswith("https") else f"https://{args.ckan_host}",
                ckan_api_key=args.ckan_api_key,
                ckan_organization=args.ckan_organization,
                ckan_dataset=args.ckan_dataset,
                ckan_resource=args.ckan_resource,
                data_source=args.data_source,
                kerberos_principal=args.kerberos_principal,
                kerberos_password=args.kerberos_password,
                concurrent_tasks=args.concurrent_tasks,
                recursive=args.recursive,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def ckan2hdfs(self, args) -> tuple[str, AccountingInfo]:
        """transfer data from CKAN to HPC using SFTP"""
        self.__logger.info(
            "executing ckan2hpc command with args: %s", self.format_args_to_string(args)
        )
        try:
            return self.dt_client.ckan2hdfs(
                ckan_host=args.ckan_host
                if args.ckan_host.startswith("https") else f"https://{args.ckan_host}",
                ckan_api_key=args.ckan_api_key,
                ckan_organization=args.ckan_organization,
                ckan_dataset=args.ckan_dataset,
                ckan_resource=args.ckan_resource,
                data_target=args.data_target,
                kerberos_principal=args.kerberos_principal,
                kerberos_password=args.kerberos_password,
                concurrent_tasks=args.concurrent_tasks,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def hpc2ckan(self, args) -> tuple[str, AccountingInfo]:
        """transfer data from hpc to CKAN using SFTP"""
        self.__logger.info(
            "executing hpc2ckan command with args: %s", self.format_args_to_string(args)
        )
        try:
            # Check if 2FA is enabled
            if args.two_factor_authentication:
                return self.dt_client.hpc2ckan_2fa(
                    ckan_host=args.ckan_host
                    if args.ckan_host.startswith("https")
                    else f"https://{args.ckan_host}",
                    ckan_api_key=args.ckan_api_key,
                    ckan_organization=args.ckan_organization,
                    ckan_dataset=args.ckan_dataset,
                    ckan_resource=args.ckan_resource,
                    hpc_host=args.hpc_host,
                    hpc_port=args.hpc_port,
                    hpc_username=args.hpc_username,
                    hpc_secret_key_path=args.hpc_secret_key,
                    hpc_secret_key_password=args.hpc_secret_key_password,
                    data_source=args.data_source,
                    concurrent_tasks=args.concurrent_tasks,
                )
            return self.dt_client.hpc2ckan(
                ckan_host=args.ckan_host
                if args.ckan_host.startswith("https") else f"https://{args.ckan_host}",
                ckan_api_key=args.ckan_api_key,
                ckan_organization=args.ckan_organization,
                ckan_dataset=args.ckan_dataset,
                ckan_resource=args.ckan_resource,
                hpc_host=args.hpc_host,
                hpc_port=args.hpc_port,
                hpc_username=args.hpc_username,
                hpc_password=args.hpc_password,
                hpc_secret_key_path=args.hpc_secret_key,
                hpc_secret_key_password=args.hpc_secret_key_password,
                data_source=args.data_source,
                concurrent_tasks=args.concurrent_tasks,
                recursive=args.recursive,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def ckan2hpc(self, args) -> tuple[str, AccountingInfo]:
        """transfer data from CKAN to hpc using SFTP"""
        self.__logger.info(
            "executing ckan2hpc command with args: %s", self.format_args_to_string(args)
        )
        try:
            # Check if 2FA is enabled
            if args.two_factor_authentication:
                return self.dt_client.ckan2hpc_2fa(
                    ckan_host=args.ckan_host
                    if args.ckan_host.startswith("https")
                    else f"https://{args.ckan_host}",
                    ckan_api_key=args.ckan_api_key,
                    ckan_organization=args.ckan_organization,
                    ckan_dataset=args.ckan_dataset,
                    ckan_resource=args.ckan_resource,
                    hpc_host=args.hpc_host,
                    hpc_port=args.hpc_port,
                    hpc_username=args.hpc_username,
                    hpc_secret_key_path=args.hpc_secret_key,
                    hpc_secret_key_password=args.hpc_secret_key_password,
                    data_target=args.data_target,
                    concurrent_tasks=args.concurrent_tasks,
                )
            return self.dt_client.ckan2hpc(
                ckan_host=args.ckan_host
                if args.ckan_host.startswith("https") else f"https://{args.ckan_host}",
                ckan_api_key=args.ckan_api_key,
                ckan_organization=args.ckan_organization,
                ckan_dataset=args.ckan_dataset,
                ckan_resource=args.ckan_resource,
                hpc_host=args.hpc_host,
                hpc_port=args.hpc_port,
                hpc_username=args.hpc_username,
                hpc_password=args.hpc_password,
                hpc_secret_key_path=args.hpc_secret_key,
                hpc_secret_key_password=args.hpc_secret_key_password,
                data_target=args.data_target,
                concurrent_tasks=args.concurrent_tasks,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def local2ckan(self, args) -> tuple[str, AccountingInfo]:
        """transfer data from local filesystem to CKAN using SFTP"""
        self.__logger.info(
            "executing local2ckan command with args: %s",
            self.format_args_to_string(args),
        )

        try:
            return self.dt_client.local2ckan(
                ckan_host=args.ckan_host
                if args.ckan_host.startswith("https") else f"https://{args.ckan_host}",
                ckan_api_key=args.ckan_api_key,
                ckan_organization=args.ckan_organization,
                ckan_dataset=args.ckan_dataset,
                ckan_resource=args.ckan_resource,
                data_source=args.data_source,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def ckan2local(self, args) -> tuple[str, AccountingInfo]:
        """transfer data from CKAN to the local filesystem using SFTP"""
        self.__logger.info(
            "executing ckan2local command with args: %s",
            self.format_args_to_string(args),
        )
        try:
            return self.dt_client.ckan2local(
                ckan_host=args.ckan_host
                if args.ckan_host.startswith("https") else f"https://{args.ckan_host}",
                ckan_api_key=args.ckan_api_key,
                ckan_organization=args.ckan_organization,
                ckan_dataset=args.ckan_dataset,
                ckan_resource=args.ckan_resource,
                data_target=args.data_target,
            )

        except Exception as ex:
            raise HidDataTransferException(ex) from ex

    def check_command_status(self, args):
        """Checks the status of a CLI command by ID"""
        # Check process group state by id
        # This implies to check the execution state of the last processor in the group
        self.__logger.info(
            "executing check_command_status command with args: %s",
            self.format_args_to_string(args),
        )
        try:
            return self.dt_client.check_command_status(args.command_id)

        except Exception as ex:
            raise HidDataTransferException(ex) from ex
