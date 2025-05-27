# carpetatree/utils/validators.py

import re
from tkinter import messagebox

def validate_name(name):
    if not name.strip():
        messagebox.showerror("Error", "El nombre no puede estar vacío")
        return False
    if re.search(r'[<>:"/\\|?*]', name):
        messagebox.showerror("Error", "El nombre contiene caracteres no válidos")
        return False
    return True