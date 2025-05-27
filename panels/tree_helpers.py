def update_editors(app, node):
    """Actualiza los distintos editores con los datos del nodo."""
    if hasattr(app, 'name_entry'):
        app.name_entry.delete(0, "end")
        app.name_entry.insert(0, node.get("name", ""))
    if hasattr(app, 'markdown_short'):
        app.markdown_short.delete("1.0", "end")
        app.markdown_short.insert("1.0", node.get("markdown_short", ""))
    if hasattr(app, 'explanation_text'):
        app.explanation_text.delete("1.0", "end")
        app.explanation_text.insert("1.0", node.get("explanation", ""))
    if hasattr(app, 'code_text'):
        app.code_text.delete("1.0", "end")
        app.code_text.insert("1.0", node.get("code", ""))