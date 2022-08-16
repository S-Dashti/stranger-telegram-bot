import json

def read_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return []
    except FileNotFoundError:
        return []

def write_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
