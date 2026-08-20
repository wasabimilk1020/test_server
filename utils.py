import json

def load_json(json_file):
  with open(json_file, "r", encoding="utf-8") as f:
    return json.load(f)
 
def write_json(json_file, data):
  with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

 