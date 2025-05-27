# carpetatree/dialogs/insert_link.py

import tkinter as tk

def show_insert_link(app):
    dialog = tk.Toplevel(app.root)
    dialog.title("Insertar Enlace")
    dialog.geometry("400x120")
    dialog.transient(app.root)
    dialog.grab_set()

    tk.Label(dialog, text="Texto:").pack(anchor="w", padx=10, pady=5)
    text_entry = tk.Entry(dialog, width=50)
    text_entry.pack(padx=10, pady=5)

    tk.Label(dialog, text="URL:").pack(anchor="w", padx=10, pady=5)
    url_entry = tk.Entry(dialog, width=50)
    url_entry.pack(padx=10, pady=5)

    def insert():
        text = text_entry.get()
        url = url_entry.get()
        if text and url:
            app.text.insert(tk.INSERT, f"[{text}]({url})")
            dialog.destroy()

    tk.Button(dialog, text="Insertar", command=insert).pack(pady=10)
    text_entry.focus()
