'''
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

CLI tool for data transfer based on Apache NIFI
Initial Poc features
- hdfs2hpc: transfer data from hdfs to target hpc, using sftp processor:
  - inputs:
      - hpc_host: hpc frontend hostname
      - hpc_username: user account name
      - hpc_secret_key_path: user's secret key location
      - data-source: HDFS file path
      - data-target: HPC remote folder

- hpc2hdfs: transfer data file from hpc folder to target hdfs folder,
using sftp processor:
  - inputs:
      - hpc_host: hpc frontend hostname
      - hpc_username: user account name
      - hpc_secret_key_path: user's secret key location
      - data-source: HPC file path
      - data-target: HDFS remote folder

- ckan2hpc: transfer data from ckan to target hpc,
    using ckan and sftp processors:
    - inputs:
        - ckan_host: CKAN host endpoint
        - ckan_api_key: CKAN API key
        - ckan_organization: CKAN organization
        - ckan_dataset: CKAN dataset
        - ckan_resource: CKAN resource
        - hpc_host: hpc frontend hostname
        - hpc_username: user account name
        - hpc_secret_key_path: user's secret key location
        - data-target: HPC remote folder

- hpc2ckan: transfer data from hpc to target ckan,
    using ckan and sftp processors:
    - inputs:
        - ckan_host: CKAN host endpoint
        - ckan_api_key: CKAN API key
        - ckan_organization: CKAN organization
        - ckan_dataset: CKAN dataset
        - hpc_host: hpc frontend hostname
        - hpc_username: user account name
        - hpc_secret_key_path: user's secret key location
        - data_source: HPC file path

- local2ckan: transfer data from a local filesystem to a target ckan
    - inputs:
        - ckan_host: CKAN host endpoint
        - ckan_api_key: CKAN API key
        - ckan_organization: CKAN organization
        - ckan_dataset: CKAN dataset
        - ckan_resource: CKAN resource to receive the data
        - data_source: local file path to the data to transfer

- ckan2local: transfer data from ckan to a local filesystem
    - inputs:
        - ckan_host: CKAN host endpoint
        - ckan_api_key: CKAN API key
        - ckan_organization: CKAN organization
        - ckan_dataset: CKAN dataset
        - ckan_resource: CKAN resource to transfer
        - data_target: local target directory where to transfer the resource

- check-status: check the execution state of a command
  - inputs:
      - command_id: uuid of command executed
        (uuid is reported after command execution)


This CLI uses NIFI account to get an access token,
It uses NIFI REST API to send requests.
It uses a predefined and installed process group HDSF2HPC template
with associated parameter context
'''

import sys
import os
import threading
import traceback
import warnings

from hid_data_transfer_lib.exceptions.hid_dt_exceptions import HidDataTransferException
from hid_data_transfer_lib.conf.hid_dt_configuration import HidDataTransferConfiguration

from data_transfer_cli.dtproxy import DataTransferProxy
from data_transfer_cli.parser.cli_parser import CLIParser


warnings.filterwarnings("ignore")


# Get CLI configuration

# Check if file ~/dtcli/dtcli.cfg exists
USER_CONFIG_FILE = None
if os.path.exists(os.path.expanduser("~/.dtcli/dtcli.cfg")):
    USER_CONFIG_FILE = os.path.expanduser("~/.dtcli/dtcli.cfg")

config = HidDataTransferConfiguration().configure(user_config_file=USER_CONFIG_FILE)

# Data Transfer proxy to the library
dt_proxy = DataTransferProxy(config, True)


class ThreadRaisingExceptions(threading.Thread):
    """Thread class that raises exceptions in the main thread
    when the thread finishes with an exception"""

    def __init__(self, *args, **kwargs):
        self._exception = None
        self._process_group_id = None
        self.accounting = kwargs['args'][0].accounting \
            if 'args' in kwargs and kwargs['args'] else False
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            self._process_group_id, accounting_info = \
                self._target(*self._args, **self._kwargs)
            if self.accounting:  # Report accounting information
                transfer_time = accounting_info.pipeline_timespan
                number_transfer_files = len(
                    accounting_info.flowfiles_sizes)
                transfer_size = sum(
                    accounting_info.flowfiles_sizes.values())/(1024*1024)
                transfer_rate = transfer_size / transfer_time

                msg = "Data transfer report:\n"
                msg += f"Transfer time: {transfer_time} s\n"
                msg += f"Transfer size: {transfer_size:.2f} MB\n"
                msg += f"Transfer rate: {transfer_rate:.2f} MB/s\n"
                msg += f"Number of transferred files: {number_transfer_files}\n"
                print(msg)
        except HidDataTransferException as e:
            self._exception = e
            raise e

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        if self._exception:
            raise self._exception
        return self._process_group_id


def main(args=None):
    """Main entry point for the Data Transfer CLI"""
    if not args:
        args = sys.argv[1:]
    # Parse arguments
    cli_parser = CLIParser(args)

    try:
        if len(args) == 0:
            cli_parser.print_help()
            sys.exit(1)

        # Read user's config file to complete missing arguments with default ones
        args = cli_parser.fill_missing_args_from_config(args)
        args = cli_parser.parse_arguments(args, dt_proxy)

        # executes associated command in data_transfer_cli module
        thread = ThreadRaisingExceptions(target=args.func, args=(args,))
        thread.start()
        thread.join()
    except HidDataTransferException as e:
        if e.process_group_id():
            sys.stderr.write(
                (
                    f"Got error{e} when executing process group "
                    f"with id {e.process_group_id()}"
                )
            )
        else:
            traceback.print_exc(file=sys.stderr)
            raise e


if __name__ == "__main__":
    main()
