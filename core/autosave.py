# carpetatree/core/autosave.py

def setup_autosave(app):
    if app.config["auto_save"]:
        app.root.after(30000, lambda: autosave(app))

def autosave(app):
    if app.unsaved_changes and app.project_file:
        app._save_to_file(app.project_file)
    if app.config["auto_save"]:
        app.root.after(30000, lambda: autosave(app))