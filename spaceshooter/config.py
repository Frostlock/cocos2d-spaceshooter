import json

JSON_FILE = "./spaceshooter/config.json"

# Load current config
def load_config():
    """Function to load current configuration from file"""
    print("Loading config from " + JSON_FILE)
    with open(JSON_FILE) as jsonFile:
        config = json.load(jsonFile)
    jsonFile.close()
    return config

def save_config(config):
    """Function to save the current configuration to file."""
    try:
        # test dump to make sure current configuration can be serialized.
        json.dumps(config)
    except TypeError:
        print("ERROR: Unable to serialize the index, saving to index file failed.")
    else:
        # Save to file
        print("Saving config to " + JSON_FILE)
        with open(JSON_FILE, 'w') as jsonFile:
            json.dump(config, jsonFile, indent=4, sort_keys=True)
        jsonFile.close()

CONFIG = load_config()
