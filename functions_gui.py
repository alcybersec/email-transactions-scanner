"""
Email Transaction Scanner - A desktop app for viewing banking transactions from emails
Copyright (C) 2024 alcybersec

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import json

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')

def create_default_settings():
    default_settings = {
        "username": "",
        "password": "",
        "imap_server": "",
        "imap_port": ""
    }
    with open(SETTINGS_PATH, 'w') as file:
        json.dump(default_settings, file, indent=4)

def ensure_settings_file():
    if not os.path.exists(SETTINGS_PATH):
        create_default_settings()

def load_settings():
    ensure_settings_file()
    with open(SETTINGS_PATH, 'r') as file:
        return json.load(file)