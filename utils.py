import json

def load_json(json_file):
  with open(json_file, "r", encoding="utf-8") as f:
    return json.load(f)
 
 