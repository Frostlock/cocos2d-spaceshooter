import json

JSON_FILE = "./spaceshooter/config.json"

CONFIG = None

# Load current config
def load_config():
    """Function to load current configuration from file"""
    global CONFIG
    with open(JSON_FILE) as jsonFile:
        CONFIG = json.load(jsonFile)
    jsonFile.close()

def save_config():
    """Function to save the current configuration to file."""
    global CONFIG
    try:
        # test dump to make sure current configuration can be serialized.
        json.dumps(CONFIG)
    except TypeError:
        print("ERROR: Unable to serialize the index, saving to index file failed.")
    else:
        # Save to file
        with open(JSON_FILE, 'w') as jsonFile:
            json.dump(CONFIG, jsonFile, indent=2, sort_keys=True)
        jsonFile.close()

load_config()