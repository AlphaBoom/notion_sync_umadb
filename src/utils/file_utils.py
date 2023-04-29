import json
import os

def read_json(file_path)->dict:
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_id_list(file_path)->list[str]:
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def write_id_list(file_path, data:list[str], append=False):
    if append:
        with open(file_path, "a", encoding="utf-8") as f:
           for id in data:
               f.write(f"{id}\n")
    else:
        with open(file_path, "w", encoding="utf-8") as f:
             for id in data:
               f.write(f"{id}\n")