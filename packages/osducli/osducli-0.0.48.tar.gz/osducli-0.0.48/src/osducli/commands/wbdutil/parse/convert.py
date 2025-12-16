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
"""Convert a LAS file to Wellbore and Well Log and write to JSON files"""

import os

import click
from wbdutil.commands.parse import convert

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import handle_cli_exceptions
from osducli.commands.wbdutil.config_file import get_config_path


# click entry point
@click.command(cls=CustomClickCommand, help="Convert a LAS file to Wellbore and WellLog and write to JSON files")
@click.option("-id", "--id", "_id", help="Record id to retrieve", required=True)
@click.option("-i", "--input", "_file", help="Path to a file or folder containing one or more LAS file(s)", required=True)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, _id: str, _file: str):
    config_path = get_config_path(state.config)
    try:
        return convert(_file, _id, config_path)
    finally:
        os.remove(config_path)
