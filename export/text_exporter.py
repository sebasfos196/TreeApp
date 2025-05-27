# carpetatree/export/text_exporter.py

def generate_text_export(app):
    def build_tree_text(node_id, indent=0):
        node = app.node_data[node_id]
        prefix = "📁" if node["type"] == "folder" else "📄"
        line = f"{'  ' * indent}{prefix} {node['name']} [{node['status'] or '-'}]"
        content = f"{line}\n"
        if node["type"] == "file":
            content += f"{'  ' * (indent + 1)}Tags: {', '.join(node.get('tags', []))}\n"
            content += f"{'  ' * (indent + 1)}Contenido:\n"
            for ln in node["content"].splitlines():
                content += f"{'  ' * (indent + 2)}{ln}\n"
        for child_id in app.tree.get_children(node_id):
            content += build_tree_text(child_id, indent + 1)
        return content

    export = ""
    for top_id in app.tree.get_children():
        export += build_tree_text(top_id)
    return export
