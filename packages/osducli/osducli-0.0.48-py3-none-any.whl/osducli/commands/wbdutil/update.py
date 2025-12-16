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
"""Update an existing WellLog record"""
import os

import click
from wbdutil.commands.update import welllog

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wbdutil.config_file import get_config_path


# click entry point
@click.command(cls=CustomClickCommand, help="Update an existing WellLog record")
@click.option("-id", "--id", "_id", help="Record id to update", required=True)
@click.option("--curvefam", "_curvefam", help="If true, recognize and update the curve families", is_flag=True, required=False)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, _id: str, _curvefam: bool = False):
    client = CliOsduClient(state.config)
    client.token_refresher.authorize()
    token = client.token_refresher.access_token
    config_path = get_config_path(state.config)
    try:
        return welllog(_id, token, config_path, _curvefam)
    finally:
        os.remove(config_path)
