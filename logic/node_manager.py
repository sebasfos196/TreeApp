# carpetatree/logic/node_manager.py

from utils.validators import validate_name
from tkinter import simpledialog, messagebox
from datetime import datetime
import re
from utils.validators import validate_name

def add_folder(app):
    parent = app.tree.focus() or ""
    name = simpledialog.askstring("Nueva Carpeta", "Nombre de la carpeta:")
    if name and validate_name(name):
        new_id = f"folder_{len(app.node_data)}_{name}"
        timestamp = datetime.now().strftime("%H:%M")
        app.tree.insert(parent, "end", iid=new_id, text=f"📁 {name}", values=["", timestamp])
        app.node_data[new_id] = {
            "name": name, "type": "folder", "status": "", "content": "",
            "tags": [], "created": datetime.now().isoformat(), "modified": datetime.now().isoformat()
        }
        app.mark_unsaved()
        app.update_preview()

def add_file(app):
    parent = app.tree.focus() or ""
    name = simpledialog.askstring("Nuevo Archivo", "Nombre del archivo:")
    if name and validate_name(name):
        new_id = f"file_{len(app.node_data)}_{name}"
        timestamp = datetime.now().strftime("%H:%M")
        app.tree.insert(parent, "end", iid=new_id, text=f"📄 {name}", values=["❌", timestamp])
        app.node_data[new_id] = {
            "name": name, "type": "file", "status": "❌",
            "content": f"# {name}\n\nContenido del archivo...",
            "tags": [], "created": datetime.now().isoformat(), "modified": datetime.now().isoformat()
        }
        app.mark_unsaved()
        app.update_preview()

def rename_node(app):
    node_id = app.tree.focus()
    if node_id and node_id in app.node_data:
        current_name = app.node_data[node_id]["name"]
        new_name = simpledialog.askstring("Renombrar", "Nuevo nombre:", initialvalue=current_name)
        if new_name and validate_name(new_name):
            app.node_data[node_id]["name"] = new_name
            app.node_data[node_id]["modified"] = datetime.now().isoformat()
            node_type = app.node_data[node_id]["type"]
            icon = "📁" if node_type == "folder" else "📄"
            status = app.node_data[node_id].get("status", "")
            label = f"{icon} {new_name}"
            if status:
                label += f" {status}"
            app.tree.item(node_id, text=label)
            if node_id == app.current_node:
                app.name_entry.delete(0, "end")
                app.name_entry.insert(0, new_name)
            app.mark_unsaved()
            app.update_preview()

def delete_node(app):
    node_id = app.tree.focus()
    if node_id:
        name = app.node_data.get(node_id, {}).get("name", "elemento")
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{name}' y su contenido?"):
            def delete_recursive(nid):
                for child in app.tree.get_children(nid):
                    delete_recursive(child)
                app.node_data.pop(nid, None)
            delete_recursive(node_id)
            app.tree.delete(node_id)
            if app.current_node == node_id:
                app.current_node = None
                app.clear_editor()
            app.mark_unsaved()
            app.update_preview()

def duplicate_node(app):
    node_id = app.tree.focus()
    if node_id and node_id in app.node_data:
        original = app.node_data[node_id].copy()
        new_name = f"{original['name']} (copia)"
        new_id = f"{original['type']}_{len(app.node_data)}_{new_name}"
        parent = app.tree.parent(node_id)
        icon = "📁" if original["type"] == "folder" else "📄"
        status = original["status"]
        timestamp = datetime.now().strftime("%H:%M")
        app.tree.insert(parent, "end", iid=new_id,
                        text=f"{icon} {new_name}", values=[status, timestamp])
        original["name"] = new_name
        original["created"] = datetime.now().isoformat()
        original["modified"] = da

def set_node_status(app, status):
    if app.current_node and app.current_node in app.node_data:
        node = app.node_data[app.current_node]
        node["status"] = status
        node["modified"] = datetime.now().isoformat()
        icon = "📁" if node["type"] == "folder" else "📄"
        display_text = f"{icon} {node['name']}"
        if status:
            display_text += f" {status}"

        app.tree.item(app.current_node, text=display_text, values=[status, ""])
        app.mark_unsaved()
        app.update_preview()
        app.update_status()