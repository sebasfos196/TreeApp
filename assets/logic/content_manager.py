# carpetatree/logic/content_manager.py

from datetime import datetime

def load_node_content(app, node_id):
    data = app.node_data[node_id]
    app.name_entry.delete(0, "end")
    app.name_entry.insert(0, data["name"])
    app.text.delete("1.0", "end")
    app.text.insert("1.0", data["content"])
    app.highlighter.highlight()
    app.update_line_numbers()
    app.update_preview()

def save_current_content(app):
    if app.current_node and app.current_node in app.node_data:
        content = app.text.get("1.0", "end").strip()
        if content != app.node_data[app.current_node]["content"]:
            app.node_data[app.current_node]["content"] = content
            app.node_data[app.current_node]["modified"] = datetime.now().isoformat()
            app.mark_unsaved()
