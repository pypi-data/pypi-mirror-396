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
"""Print a LAS file header"""

import click
from wbdutil.commands.parse import printlas

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import handle_cli_exceptions


# click entry point
@click.command(cls=CustomClickCommand, help="Print a LAS file header")
@click.option("-i", "--input", "_file", help="Path and filename of a LAS file, or folder containing LAS files", required=True)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, _file: str):
    return printlas(_file)
