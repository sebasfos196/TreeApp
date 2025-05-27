# carpetatree/dialogs/insert_image.py

import os
import tkinter as tk
from tkinter import filedialog, simpledialog

def show_insert_image(app):
    file_path = filedialog.askopenfilename(
        title="Seleccionar Imagen",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        file_name = os.path.basename(file_path)
        alt_text = simpledialog.askstring("Texto alternativo", "Descripción de la imagen:", initialvalue=file_name)
        if alt_text:
            markdown = f"![{alt_text}]({file_path})"
            app.text.insert(tk.INSERT, markdown)
