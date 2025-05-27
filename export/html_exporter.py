# carpetatree/export/html_exporter.py

def generate_html_export(app):
    def render_node(node_id):
        node = app.node_data[node_id]
        html = [f"<h2>{node['name']}</h2>"]
        html.append(f"<p><strong>Estado:</strong> {node['status'] or '—'}<br>")
        html.append(f"<strong>Tags:</strong> {', '.join(node.get('tags', [])) or '—'}<br>")
        html.append(f"<strong>Modificado:</strong> {node.get('modified', '—')}</p>")
        html.append(f"<pre>{node['content']}</pre><hr>")
        for child_id in app.tree.get_children(node_id):
            html.append(render_node(child_id))
        return "\n".join(html)

    html = ["<html><head><meta charset='utf-8'><title>Exportación Proyecto</title></head><body>"]
    for top_id in app.tree.get_children():
        html.append(render_node(top_id))
    html.append("</body></html>")
    return "\n".join(html)