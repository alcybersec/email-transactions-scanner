
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