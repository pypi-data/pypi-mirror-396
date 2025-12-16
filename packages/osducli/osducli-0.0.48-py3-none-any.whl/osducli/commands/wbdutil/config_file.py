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
import json
import tempfile

from osducli.config import CLIConfig


def get_config_path(config: CLIConfig):
    """
    Takes a config object and writes a mapped config to a temporary JSON file.
    Returns the path to the temp file.
    """
    output = {
        "base_url": config.get('core', 'server'),
        "data_partition_id": config.get('core', 'data_partition_id'),
        "legal": {
            "legaltags": [config.get('core', 'legal_tag')],
            "otherRelevantDataCountries": [config.get('core', 'other_relevant_data_countries')],
            "status": "compliant"
        },
        "data": {
            "default": {
                "viewers": [config.get('core', 'acl_viewer')],
                "owners": [config.get('core', 'acl_owner')]
            }
        }
    }
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as tmp:
        json.dump(output, tmp, indent=4)
        return tmp.name
