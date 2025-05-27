# carpetatree/utils/file_helpers.py

import json

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
