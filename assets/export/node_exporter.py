# carpetatree/export/node_exporter.py

from tkinter import filedialog, messagebox

def export_node(app):
    if not app.current_node or app.current_node not in app.node_data:
        messagebox.showwarning("Advertencia", "Selecciona un nodo para exportar")
        return

    node = app.node_data[app.current_node]
    file_path = filedialog.asksaveasfilename(
        title=f"Exportar '{node['name']}'",
        defaultextension=".md",
        filetypes=[("Markdown", "*.md"), ("Texto", "*.txt"), ("Todos", "*.*")]
    )

    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {node['name']}\n\n")
                f.write(f"**Estado:** {node['status'] or '-'}\n")
                f.write(f"**Tags:** {', '.join(node.get('tags', []))}\n")
                f.write(f"**Modificado:** {node.get('modified', '—')}\n\n")
                f.write("---\n\n")
                f.write(node['content'])
            messagebox.showinfo("Éxito", f"Nodo exportado:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el nodo:\n{str(e)}")
