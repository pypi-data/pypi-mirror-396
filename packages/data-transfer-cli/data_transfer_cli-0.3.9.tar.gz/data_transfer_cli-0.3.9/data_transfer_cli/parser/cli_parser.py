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


This module provides a parser for the command line arguments.
It defines the command line arguments that the user can pass to the CLI
"""

import argparse
import os

import yaml


class CLIParser(argparse.ArgumentParser):
    """Parser of the command line arguments"""

    def fill_missing_args_from_config(self, args):
        """Fill missing arguments from the config file"""
        # Read default dtcli YAML config file from ~/.dtcli/config if exists
        dtcli_config_file = os.path.expanduser("~/.dtcli/server_config")
        if not os.path.exists(dtcli_config_file):
            return args
        with open(dtcli_config_file, "r", encoding="utf8") as f:
            config = yaml.safe_load(f)

            # For each host in command, find it in the config file,
            # For each host in command, complete the arguments collected
            # from the config file that are not already set in the command line
            for host in config.keys():
                if host in args:
                    host_index = args.index(host)
                    if (args[host_index-1] == "-H" or
                            args[host_index-1] == "--hpc-host"):
                        self.process_hpc_args(args, config[host])
                    elif (args[host_index-1] == "-c" or
                            args[host_index-1] == "--ckan-host"):
                        self.process_ckan_args(args, config[host])
                # Kerberos
                if host.upper() == "KERBEROS" and 'hdfs' in args[0]:
                    kerberos_config = config[host]
                    self.process_kerberos_args(args, kerberos_config)
        return args

    def process_kerberos_args(self, args, kerberos_config):
        """Process the Kerberos arguments from the config file"""
        if (("-kpr" not in args and "--kerberos-principal" not in args)
                and "principal" in kerberos_config):
            args.append("-kpr")
            args.append(str(kerberos_config["principal"]))
        if (("-kp" not in args and "--kerberos-password" not in args)
                and "password" in kerberos_config):
            args.append("-kp")
            args.append(str(kerberos_config["password"]))

    def process_hpc_args(self, args, hpc_config):
        """Process the HPC arguments from the config file"""
        if (("-z" not in args and "--hpc-port" not in args)
                and "port" in hpc_config):
            args.append("-z")
            args.append(str(hpc_config["port"]))
        if (("-u" not in args and "--hpc-username" not in args)
                and "username" in hpc_config):
            args.append("-u")
            args.append(hpc_config["username"])
        if (("-p" not in args and "--hpc-password" not in args)
                and "password" in hpc_config):
            args.append("-p")
            args.append(hpc_config["password"])
        if (("-k" not in args and "--hpc-secret-key" not in args)
                and "secret-key" in hpc_config):
            args.append("-k")
            args.append(hpc_config["secret-key"])
        if (("-P" not in args and "--hpc-secret-key-password" not in args)
                and "secret-key-password" in hpc_config):
            args.append("-P")
            args.append(hpc_config["secret-key-password"])

    def process_ckan_args(self, args, ckan_config):
        """Process the CKAN arguments from the config file"""
        if (("-a" not in args and "--ckan-api-key" not in args)
                and "api-key" in ckan_config):
            args.append("-a")
            args.append(ckan_config["api-key"])
        if (("-o" not in args and "--ckan-organization" not in args)
                and "organization" in ckan_config):
            args.append("-o")
            args.append(ckan_config["organization"])
        if (("-d" not in args and "--ckan-dataset" not in args)
                and "dataset" in ckan_config):
            args.append("-d")
            args.append(ckan_config["dataset"])

    def add_default_hpc_arguments(self, parser):
        """Add default HPC arguments to the parser"""
        parser.add_argument(
            "-H", "--hpc-host", required=True, help="Target HPC ssh host"
        )
        parser.add_argument(
            "-z", "--hpc-port", required=False, help="[Optional] Target HPC ssh port"
        )
        parser.add_argument(
            "-u", "--hpc-username", required=True, help="Username for HPC account"
        )
        parser.add_argument(
            "-p",
            "--hpc-password",
            required=False,
            help="[Optional] Password for HPC account. "
            "Either password or secret key is required",
        )
        parser.add_argument(
            "-k",
            "--hpc-secret-key",
            required=False,
            help="[Optional] Path to HPC secret key. "
            "Either password or secret key is required",
        )
        parser.add_argument(
            "-P",
            "--hpc-secret-key-password",
            required=False,
            help="[Optional] Password for HPC secret key",
        )
        return parser

    def add_default_ckan_arguments(self, parser):
        """Add default CKAN arguments to the parser"""
        parser.add_argument(
            "-c", "--ckan-host", required=True, help="CKAN host endpoint"
        )
        parser.add_argument(
            "-a",
            "--ckan-api-key",
            required=True,
            help="CKAN API key",
        )
        parser.add_argument(
            "-o",
            "--ckan-organization",
            required=True,
            help="Identifier of the CKAN organization that hosts \
            the dataset resource to transfer. \
            Could be identified by the organization id, name or title",
        )
        parser.add_argument(
            "-d",
            "--ckan-dataset",
            required=True,
            help="Identifier of the CKAN dataset that hosts the resource to transfer. \
            Could be identified by the dataset id, name or title",
        )
        return parser

    def add_default_kerberos_arguments(self, parser):
        """Add default Kerberos arguments to the parser"""
        parser.add_argument(
            "-kpr", "--kerberos-principal",
            required=False,
            help="[Optional] Kerberos principal (mandatory for a Kerberized HDFS)"
        )
        parser.add_argument(
            "-kp", "--kerberos-password",
            required=False,
            help="[Optional] Kerberos principal password "
            "(mandatory for a Kerberized HDFS)"
        )
        return parser

    def parse_arguments(self, args, target):
        """parse the command line arguments

        Args:
            args (list): list of command line arguments
            target (object): target object to execute the command

        Returns:
            dict: a dictionary of parsed arguments
        """

        # commands
        commands_parsers = self.add_subparsers(
            help="supported commands to transfer data"
        )
        # check status
        check_status_parser = commands_parsers.add_parser(
            "check-status", help="check the status of a command"
        )
        check_status_parser.add_argument(
            "-i",
            "--command_id",
            required=True,
            help="id of command to check status",
        )
        check_status_parser.set_defaults(func=target.check_command_status)

        # hdfs2hpc
        hdfs2hpc_parser = commands_parsers.add_parser(
            "hdfs2hpc", help="transfer data from HDFS to target HPC"
        )
        hdfs2hpc_parser.add_argument(
            "-s", "--data-source",
            required=True, help="HDFS file path"
        )
        hdfs2hpc_parser.add_argument(
            "-t", "--data-target",
            required=False, help="[Optional] HPC folder"
        )
        hdfs2hpc_parser = self.add_default_kerberos_arguments(hdfs2hpc_parser)
        hdfs2hpc_parser = self.add_default_hpc_arguments(hdfs2hpc_parser)
        hdfs2hpc_parser.add_argument(
            "-2fa", "--two-factor-authentication",
            required=False, action="store_true", default=False,
            help="[Optional] HPC requires 2FA authentication"
        )
        hdfs2hpc_parser.add_argument(
            "-acct", "--accounting",
            required=False, action="store_true", default=False,
            help="[Optional] Enable returning accounting information of data transfer"
        )
        hdfs2hpc_parser.add_argument(
            "-ct", "--concurrent-tasks",
            required=False, type=int, default=1,
            help="[Optional] set the number of concurrent tasks"
            " for parallel data transfer"
        )
        hdfs2hpc_parser.add_argument(
            "-R", "--recursive",
            required=False, action="store_true", default=False,
            help="[Optional] if True the data-source subdirectories"
            " will be transferred as well, otherwise only the root data-source folder"
        )
        hdfs2hpc_parser.set_defaults(func=target.hdfs2hpc)

        # hpc2hdfs
        hpc2hdfs_parser = commands_parsers.add_parser(
            "hpc2hdfs", help="transfer data from HPC to target HDFS"
        )

        hpc2hdfs_parser.add_argument(
            "-s", "--data-source", required=True, help="HPC file path"
        )
        hpc2hdfs_parser.add_argument(
            "-t", "--data-target", required=True, help="HDFS folder"
        )
        hpc2hdfs_parser = self.add_default_kerberos_arguments(hpc2hdfs_parser)
        hpc2hdfs_parser = self.add_default_hpc_arguments(hpc2hdfs_parser)
        hpc2hdfs_parser.add_argument(
            "-2fa", "--two-factor-authentication",
            required=False, action="store_true", default=False,
            help="[Optional] HPC requires 2FA authentication"
        )
        hpc2hdfs_parser.add_argument(
            "-acct", "--accounting",
            required=False, action="store_true", default=False,
            help="[Optional] Enable returning accounting information of data transfer"
        )
        hpc2hdfs_parser.add_argument(
            "-ct", "--concurrent-tasks",
            required=False, type=int, default=1,
            help="[Optional] set the number of concurrent tasks"
            " for parallel data transfer"
        )
        hpc2hdfs_parser.add_argument(
            "-R", "--recursive",
            required=False, action="store_true", default=False,
            help="[Optional] if True the data-source subdirectories"
            " will be transferred as well, otherwise only the root data-source folder"
        )
        hpc2hdfs_parser.set_defaults(func=target.hpc2hdfs)

        # ckan2hdfs
        ckan2hdfs_parser = commands_parsers.add_parser(
            "ckan2hdfs", help="transfer data from CKAN to target HDFS"
        )
        ckan2hdfs_parser = self.add_default_ckan_arguments(ckan2hdfs_parser)
        ckan2hdfs_parser.add_argument(
            "-r",
            "--ckan-resource",
            required=False,
            help="[Optional] CKAN resource to transfer. \
            Could be identified by the dataset id or name. \
            If empty, all resources in the dataset will be transferred. \
            A regex is also accepted to filter the resources to transfer",
        )
        ckan2hdfs_parser.add_argument(
            "-t", "--data-target", required=False, help="[Optional] target HDFS folder"
        )
        ckan2hdfs_parser = self.add_default_kerberos_arguments(ckan2hdfs_parser)
        ckan2hdfs_parser.add_argument(
            "-acct", "--accounting",
            required=False, action="store_true", default=False,
            help="[Optional] Enable returning accounting information of data transfer"
        )
        ckan2hdfs_parser.add_argument(
            "-ct", "--concurrent-tasks",
            required=False, type=int, default=1,
            help="[Optional] set the number of concurrent tasks"
            " for parallel data transfer"
        )
        ckan2hdfs_parser.set_defaults(func=target.ckan2hdfs)

        # hdfs2ckan
        hdfs2ckan_parser = commands_parsers.add_parser(
            "hdfs2ckan", help="transfer data from HDFS to a target CKAN"
        )
        hdfs2ckan_parser = self.add_default_ckan_arguments(hdfs2ckan_parser)
        hdfs2ckan_parser.add_argument(
            "-r",
            "--ckan-resource",
            required=False,
            help="[Optional] CKAN resource to create from transferred sources. \
            If omitted, target resource name will adopt the source file or folder name",
        )
        hdfs2ckan_parser = self.add_default_kerberos_arguments(hdfs2ckan_parser)
        hdfs2ckan_parser.add_argument(
            "-s",
            "--data-source",
            required=True,
            help="File path to HDFS file or directory to transfer",
        )
        hdfs2ckan_parser.add_argument(
            "-acct", "--accounting",
            required=False, action="store_true", default=False,
            help="[Optional] Enable returning accounting information of data transfer"
        )
        hdfs2ckan_parser.add_argument(
            "-ct", "--concurrent-tasks",
            required=False, type=int, default=1,
            help="[Optional] set the number of concurrent tasks"
            " for parallel data transfer"
        )
        hdfs2ckan_parser.add_argument(
            "-R", "--recursive",
            required=False, action="store_true", default=False,
            help="[Optional] if True the data-source subdirectories"
            " will be transferred as well, otherwise only the root data-source folder"
        )
        hdfs2ckan_parser.set_defaults(func=target.hdfs2ckan)

        # ckan2hpc
        ckan2hpc_parser = commands_parsers.add_parser(
            "ckan2hpc", help="transfer data from CKAN to target HPC"
        )
        ckan2hpc_parser = self.add_default_ckan_arguments(ckan2hpc_parser)
        ckan2hpc_parser.add_argument(
            "-r",
            "--ckan-resource",
            required=False,
            help="[Optional] CKAN resource to transfer. \
            Could be identified by the dataset id or name. \
            If empty, all resources in the dataset will be transferred. \
            A regex is also accepted to filter the resources to transfer",
        )
        ckan2hpc_parser.add_argument(
            "-t", "--data-target", required=False, help="[Optional] target HPC folder"
        )
        ckan2hpc_parser = self.add_default_hpc_arguments(ckan2hpc_parser)
        ckan2hpc_parser.add_argument(
            "-2fa", "--two-factor-authentication",
            required=False, action="store_true", default=False,
            help="[Optional] HPC requires 2FA authentication"
        )
        ckan2hpc_parser.add_argument(
            "-acct", "--accounting",
            required=False, action="store_true", default=False,
            help="[Optional] Enable returning accounting information of data transfer"
        )
        ckan2hpc_parser.add_argument(
            "-ct", "--concurrent-tasks",
            required=False, type=int, default=1,
            help="[Optional] set the number of concurrent tasks"
            " for parallel data transfer"
        )
        ckan2hpc_parser.set_defaults(func=target.ckan2hpc)

        # hpc2ckan
        hpc2ckan_parser = commands_parsers.add_parser(
            "hpc2ckan", help="transfer data from HPC to a target CKAN"
        )
        hpc2ckan_parser = self.add_default_ckan_arguments(hpc2ckan_parser)
        hpc2ckan_parser.add_argument(
            "-r",
            "--ckan-resource",
            required=False,
            help="[Optional] CKAN resource to create from transferred sources. \
            If omitted, target resource name will adopt the source file or folder name",
        )
        hpc2ckan_parser = self.add_default_hpc_arguments(hpc2ckan_parser)
        hpc2ckan_parser.add_argument(
            "-2fa", "--two-factor-authentication",
            required=False, action="store_true", default=False,
            help="[Optional] HPC requires 2FA authentication"
        )
        hpc2ckan_parser.add_argument(
            "-s",
            "--data-source",
            required=True,
            help="File path to HPC file or directory to transfer",
        )
        hpc2ckan_parser.add_argument(
            "-acct", "--accounting",
            required=False, action="store_true", default=False,
            help="[Optional] Enable returning accounting information of data transfer"
        )
        hpc2ckan_parser.add_argument(
            "-ct", "--concurrent-tasks",
            required=False, type=int, default=1,
            help="[Optional] set the number of concurrent tasks"
            " for parallel data transfer"
        )
        hpc2ckan_parser.add_argument(
            "-R", "--recursive",
            required=False, action="store_true", default=False,
            help="[Optional] if True the data-source subdirectories"
            " will be transferred as well, otherwise only the root data-source folder"
        )
        hpc2ckan_parser.set_defaults(func=target.hpc2ckan)

        # local2ckan
        local2ckan_parser = commands_parsers.add_parser(
            "local2ckan", help="transfer data from a local filesystem to a target CKAN"
        )
        local2ckan_parser = self.add_default_ckan_arguments(local2ckan_parser)
        local2ckan_parser.add_argument(
            "-r",
            "--ckan-resource",
            required=False,
            help="[Optional] CKAN resource to create from transferred sources. \
            If omitted, target resource name will adopt the source file or folder name",
        )
        local2ckan_parser.add_argument(
            "-s",
            "--data-source",
            required=True,
            help="File path to local file or directory to transfer",
        )
        local2ckan_parser.add_argument(
            "-acct", "--accounting",
            required=False, action="store_true", default=False,
            help="[Optional] Enable returning accounting information of data transfer"
        )
        local2ckan_parser.set_defaults(func=target.local2ckan)

        # ckan2local
        ckan2local_parser = commands_parsers.add_parser(
            "ckan2local", help="transfer data from CKAN to a local filesystem"
        )
        ckan2local_parser = self.add_default_ckan_arguments(ckan2local_parser)
        ckan2local_parser.add_argument(
            "-r",
            "--ckan-resource",
            required=False,
            help="[Optional] CKAN resource to transfer. \
            If omitted, all resources in the dataset will be transferred",
        )
        ckan2local_parser.add_argument(
            "-t",
            "--data-target",
            required=False,
            help="Local directory where to transfer the data. \
            If omitted, data will be transferred to the current directory",
        )
        ckan2local_parser.add_argument(
            "-acct", "--accounting",
            required=False, action="store_true", default=False,
            help="[Optional] Enable returning accounting information of data transfer"
        )
        ckan2local_parser.set_defaults(func=target.ckan2local)

        return self.parse_args(args)
