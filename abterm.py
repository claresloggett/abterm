import argparse
from app import ABTerm

# the config file is currently Python-like; could technically import it instead
# TODO: should put it into user's home dir; this is reliant on relative path
CONFIG_FILE = "config.txt"

BASE_URL = "https://dev.azure.com"

parser = argparse.ArgumentParser()
parser.add_argument("--history", action="store_true", help="Retrieve history of each card to find its earliest active iteration. This can significantly increase the number of API calls.")

def read_config():
    expected_keys = ['ORGANISATION', 'PROJECT', 'TEAM', 'TOKEN']
    with open(CONFIG_FILE, "r") as f:
        config = {}
        for line in f:
            key, value = line.split("=")
            config[key.strip()] = value.strip(" \"'\n")
        for key in expected_keys:
            if key not in config:
                raise ValueError(f"Missing required key in config: {key}")
    return config

if __name__ == "__main__":
    config = read_config()
    args = parser.parse_args()
    app = ABTerm(BASE_URL, config['ORGANISATION'], config['PROJECT'], config['TEAM'], 
                 config['TOKEN'], args.history)
    app.run()
