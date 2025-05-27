# carpetatree/config/config_manager.py

import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = "workspace_config.json"
        self.default_config = {
            "theme": "dark",
            "font_size": 10,
            "auto_save": True,
            "last_project": "",
            "window_geometry": "1400x800",
            "panel_weights": [300, 600, 500],
            "shortcuts": {
                "save": "<Control-s>",
                "new_file": "<Control-n>",
                "new_folder": "<Control-Shift-n>",
                "find": "<Control-f>",
                "export": "<Control-e>"
            }
        }
        self.config = self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
        except:
            pass
        return self.default_config.copy()

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")