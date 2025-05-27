import tkinter as tk
from tkinter import ttk
from datetime import datetime
from .tree_helpers import update_editors

def create_file_simple(app):
    """Crear archivo con input simple."""
    dialog = tk.Toplevel(app.root)
    dialog.title("Nuevo Archivo")
    dialog.geometry("300x100")
    dialog.transient(app.root)
    dialog.grab_set()
    dialog.resizable(False, False)

    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (150)
    y = (dialog.winfo_screenheight() // 2) - (50)
    dialog.geometry(f"300x100+{x}+{y}")

    name_entry = ttk.Entry(dialog, width=35, font=("Segoe UI", 10))
    name_entry.pack(pady=20)
    name_entry.insert(0, "documento.md")
    name_entry.select_range(0, len("documento"))
    name_entry.focus()

    def create_file():
        full_name = name_entry.get().strip()
        if full_name:
            parent = app.tree.focus() or ""
            if parent and parent in app.node_data:
                if app.node_data[parent]["type"] != "folder":
                    parent = app.tree.parent(parent) or ""
            new_id = f"file_{len(app.node_data)}_{full_name}_{datetime.now().strftime('%H%M%S')}"
            name_part = full_name.split('.')[0] if '.' in full_name else full_name
            initial_content = f"# {name_part}\n\nContenido del archivo..."
            app.node_data[new_id] = {
                "name": full_name,
                "type": "file",
                "status": "",
                "content": initial_content,
                "markdown_short": f"# {name_part}",
                "explanation": "",
                "code": "",
                "tags": [],
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }
            app.tree.insert(parent, "end", iid=new_id, text=f"📄 {full_name}", values=[""])
            if hasattr(app, "update_tree_display_realtime"):
                app.update_tree_display_realtime(new_id)
            app.mark_unsaved()
            dialog.destroy()

    create_btn = ttk.Button(dialog, text="Crear", command=create_file)
    create_btn.pack(pady=10)
    name_entry.bind("<Return>", lambda e: create_file())
    dialog.bind("<Escape>", lambda e: dialog.destroy())

def create_folder_simple(app):
    """Diálogo simple para crear carpetas."""
    dialog = tk.Toplevel(app.root)
    dialog.title("Nueva Carpeta")
    dialog.geometry("300x100")
    dialog.transient(app.root)
    dialog.grab_set()
    dialog.resizable(False, False)

    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (150)
    y = (dialog.winfo_screenheight() // 2) - (50)
    dialog.geometry(f"300x100+{x}+{y}")

    name_entry = ttk.Entry(dialog, width=35, font=("Segoe UI", 10))
    name_entry.pack(pady=20)
    name_entry.insert(0, "nueva_carpeta")
    name_entry.select_range(0, tk.END)
    name_entry.focus()

    def create_folder():
        name = name_entry.get().strip()
        if name:
            parent = app.tree.focus() or ""
            if parent and parent in app.node_data:
                if app.node_data[parent]["type"] != "folder":
                    parent = app.tree.parent(parent) or ""
            new_id = f"folder_{len(app.node_data)}_{name}_{datetime.now().strftime('%H%M%S')}"
            app.node_data[new_id] = {
                "name": name,
                "type": "folder",
                "status": "",
                "content": f"# {name}\n\nDescripción de la carpeta...",
                "markdown_short": f"# {name}",
                "explanation": "",
                "code": "",
                "tags": [],
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }
            app.tree.insert(parent, "end", iid=new_id, text=f"📁 {name}/", values=[""])
            if hasattr(app, "update_tree_display_realtime"):
                app.update_tree_display_realtime(new_id)
            app.mark_unsaved()
            dialog.destroy()

    create_btn = ttk.Button(dialog, text="Crear", command=create_folder)
    create_btn.pack(pady=10)
    name_entry.bind("<Return>", lambda e: create_folder())
    dialog.bind("<Escape>", lambda e: dialog.destroy())