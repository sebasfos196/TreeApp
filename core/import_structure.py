import re
from datetime import datetime

def parse_structure(texto):
    """
    Parsea una lista jerárquica de archivos/carpetas con sus markdowns, usando indentación.
    Devuelve una lista de nodos con estructura de árbol.
    """
    lines = texto.splitlines()
    stack = []
    root = []
    for line in lines:
        if not line.strip():
            continue
        # Determinar nivel de indentación
        indent = len(line) - len(line.lstrip(' \t'))
        content = line.strip()
        # Separar nombre y markdown ('#' es separador)
        if '#' in content:
            nombre, markdown = map(str.strip, content.split('#', 1))
        else:
            nombre, markdown = content, ""
        is_folder = nombre.endswith('/')
        node = {
            "name": nombre.rstrip('/').strip(),
            "type": "folder" if is_folder else "file",
            "markdown_short": markdown,
            "children": [],
            "status": "",
            "content": "",
            "explanation": "",
            "code": "",
            "tags": [],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        # Reubicar en el árbol según la indentación
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if stack:
            stack[-1][1]["children"].append(node)
        else:
            root.append(node)
        stack.append((indent, node))
    return root

def agregar_estructura_a_rama(app):
    texto = app.import_text.get("1.0", "end-1c")
    rama_padre = app.tree.focus()
    if not rama_padre:
        messagebox.showwarning("Selecciona rama", "Debes seleccionar una rama del árbol.")
        return
    estructura = parse_structure(texto)
    def agregar_recursivo(parent_id, nodos):
        for n in nodos:
            tipo = n["type"]
            node_id = f"{tipo}_{len(app.node_data)}_{n['name']}"
            app.node_data[node_id] = n.copy()
            app.node_data[node_id].pop("children", None)  # No guardar 'children' en node_data
            icon = "📁" if tipo == "folder" else "📄"
            display_name = n['name'] + ("/" if tipo == "folder" else "")
            label = f"{icon} {display_name}"
            app.tree.insert(parent_id, "end", iid=node_id, text=label, values=[""])
            # Recursivo para hijos
            if n["children"]:
                agregar_recursivo(node_id, n["children"])
    agregar_recursivo(rama_padre, estructura)
    app.mark_unsaved()
    app.update_preview()