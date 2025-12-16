#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""Retrieve WellLog data from an OSDU instance and save to a LAS format file"""
import os

import click
from wbdutil.commands.download import download_las

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wbdutil.config_file import get_config_path


# click entry point
@click.command(cls=CustomClickCommand, help="Download WellLog data to LAS file")
@click.option("-id", "--id", "_id", help="WellLog id to retrieve", required=True)
@click.option("-o", "--out", "_file", help="The output file path", required=True)
@click.option("-c", "--curves", "_curves", help="List of curves to retrieve, or none to get all curves", required=False)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, _id: str, _file: str, _curves: list[str]):
    client = CliOsduClient(state.config)
    client.token_refresher.authorize()
    token = client.token_refresher.access_token
    config_path = get_config_path(state.config)
    try:
        download_las(_id, _file, token, config_path, _curves)
    finally:
        os.remove(config_path)
