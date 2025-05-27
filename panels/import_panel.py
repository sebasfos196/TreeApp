import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

def setup_import_panel(app, parent_frame):
    """
    Panel para importar listas jerárquicas de archivos/carpetas y markdowns,
    agregándolos a la rama seleccionada del árbol.
    Incluye mejoras de UX: ayuda, ejemplo, botón de limpieza y feedback visual.
    """
    import_frame = ttk.LabelFrame(parent_frame, text="Importar estructura de archivos/carpetas")
    import_frame.pack(fill="x", padx=8, pady=8, anchor="n")

    # Ayuda/tooltip
    help_text = (
        "Pega una lista (usa tabuladores/espacios para indicar niveles):\n"
        "Ejemplo:\n"
        "  Carpeta1/ # Descripción de la carpeta\n"
        "    archivo1.txt # Markdown archivo1\n"
        "    Subcarpeta/\n"
        "      archivo2.txt # Otro archivo\n"
        "Carpeta2/\n"
        "  archivo3.txt\n"
        "\n"
        "• '#' separa nombre y markdown.\n"
        "• Las líneas que terminan en '/' serán carpetas."
    )
    help_label = ttk.Label(import_frame, text=help_text, justify="left", foreground="#555")
    help_label.pack(fill="x", padx=4, pady=(2, 4))

    # Caja de texto
    app.import_text = tk.Text(import_frame, height=9, font=("Segoe UI", 10), wrap="word")
    app.import_text.pack(fill="x", padx=4, pady=(0, 4))

    # Botones
    btn_frame = ttk.Frame(import_frame)
    btn_frame.pack(fill="x", padx=4, pady=(0, 4))

    import_btn = ttk.Button(
        btn_frame,
        text="Agregar a rama seleccionada",
        command=lambda: agregar_estructura_a_rama(app)
    )
    import_btn.pack(side="left", padx=(0, 4))

    clear_btn = ttk.Button(
        btn_frame,
        text="Limpiar",
        command=lambda: app.import_text.delete("1.0", "end")
    )
    clear_btn.pack(side="left", padx=(0, 4))

    example_btn = ttk.Button(
        btn_frame,
        text="Ejemplo",
        command=lambda: _insert_example(app)
    )
    example_btn.pack(side="left")

    # Feedback visual
    app.import_status = ttk.Label(import_frame, text="", foreground="#007700")
    app.import_status.pack(anchor="w", padx=4, pady=(2, 0))

def _insert_example(app):
    example = (
        "Documentacion/\n"
        "  Introduccion.md # Introducción general\n"
        "  Conceptos/\n"
        "    concepto1.md # Definición de concepto 1\n"
        "    concepto2.md # Definición de concepto 2\n"
        "Codigo/\n"
        "  main.py # Script principal\n"
        "  utils/\n"
        "    helper.py # Funciones auxiliares\n"
    )
    app.import_text.delete("1.0", "end")
    app.import_text.insert("1.0", example)

def parse_structure(texto):
    """
    Parsea una lista jerárquica de archivos/carpetas con markdown, usando indentación y '#'.
    Devuelve una lista de nodos con estructura de árbol.
    """
    lines = texto.splitlines()
    stack = []
    root = []
    for line in lines:
        if not line.strip():
            continue
        # Determinar nivel de indentación (tab o 2+ espacios)
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
        messagebox.showwarning("Selecciona rama", "Debes seleccionar primero una carpeta del árbol.")
        app.import_status.config(text="❌ Selecciona una carpeta antes de importar.", foreground="#cc0000")
        return
    estructura = parse_structure(texto)
    if not estructura:
        app.import_status.config(text="❌ No se detectó estructura válida.", foreground="#cc0000")
        return

    def agregar_recursivo(parent_id, nodos):
        for n in nodos:
            tipo = n["type"]
            # Evitar colisiones de ID
            base_id = f"{tipo}_{n['name'].replace(' ', '_')}"
            count = 1
            node_id = base_id
            while node_id in app.node_data:
                count += 1
                node_id = f"{base_id}_{count}"
            app.node_data[node_id] = n.copy()
            app.node_data[node_id].pop("children", None)
            icon = "📁" if tipo == "folder" else "📄"
            display_name = n['name'] + ("/" if tipo == "folder" else "")
            label = f"{icon} {display_name}"
            app.tree.insert(parent_id, "end", iid=node_id, text=label, values=[""])
            # Recursivo para hijos
            if n["children"]:
                agregar_recursivo(node_id, n["children"])
    agregar_recursivo(rama_padre, estructura)
    app.mark_unsaved()
    if hasattr(app, "update_preview"):
        app.update_preview()
    app.import_status.config(text="✅ Estructura agregada correctamente.", foreground="#007700")