import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def setup_preview_panel(app):
    """Configurar panel de vista previa CORREGIDO"""

    # Header de vista previa LIMPIO
    preview_header = ttk.Frame(app.right_frame)
    preview_header.pack(fill="x", padx=5, pady=5)

    ttk.Label(preview_header, text="🔍 Vista Previa", font=("Segoe UI", 10, "bold")).pack(side="left")

    # Área de vista previa
    preview_frame = ttk.Frame(app.right_frame)
    preview_frame.pack(fill="both", expand=True, padx=5, pady=5)

    text_frame = tk.Frame(preview_frame)
    text_frame.pack(fill="both", expand=True)

    app.preview_text = tk.Text(text_frame, wrap="none", state="normal",
                              font=("Consolas", app.config["font_size"]))
    app.preview_text.pack(side="left", fill="both", expand=True)

    preview_scrollbar_v = ttk.Scrollbar(text_frame, orient="vertical", 
                                       command=app.preview_text.yview)
    preview_scrollbar_v.pack(side="right", fill="y")

    preview_scrollbar_h = ttk.Scrollbar(preview_frame, orient="horizontal", 
                                       command=app.preview_text.xview)
    preview_scrollbar_h.pack(side="bottom", fill="x")

    app.preview_text.config(yscrollcommand=preview_scrollbar_v.set, 
                           xscrollcommand=preview_scrollbar_h.set)

    app.preview_text.config(
        bg="#f8f8f8",
        fg="#333333",
        selectbackground="#264f78",
        selectforeground="white"
    )

    # BOTONES por debajo del título
    button_frame = ttk.Frame(app.right_frame)
    button_frame.pack(fill="x", padx=5, pady=2)

    mode_frame = ttk.Frame(button_frame)
    mode_frame.pack(side="left")

    app.preview_mode = tk.StringVar(value="clasico")

    modes = [
        ("Clásico", "clasico"),
        ("ASCII", "ascii"), 
        ("Columnas", "columnas"),
        ("Carpetas", "folders")
    ]

    for text, value in modes:
        ttk.Radiobutton(mode_frame, text=text, variable=app.preview_mode, 
                       value=value, command=app.update_preview).pack(side="left", padx=2)

    action_frame = ttk.Frame(button_frame)
    action_frame.pack(side="right")

    ttk.Button(action_frame, text="📄", width=3,
              command=lambda: export_preview_txt(app)).pack(side="left", padx=2)

    ttk.Button(action_frame, text="📖 Exportar Documentación", 
              command=lambda: export_professional_docs(app)).pack(side="left", padx=2)

    app.preview_text.bind("<Control-a>", lambda e: select_all_preview(app))
    app.preview_text.bind("<Control-c", lambda e: copy_preview_selection(app))
    app.preview_text.bind("<Button-3", lambda e: show_preview_context_menu(app, e))

def update_preview_improved(app):
    if not hasattr(app, "preview_mode") or not hasattr(app, "preview_text"):
        return

    mode = app.preview_mode.get()
    app.preview_text.config(state="normal", wrap="none")
    app.preview_text.delete("1.0", "end")

    app.line_map = {}
    current_line = 1

    def get_markdown_single_line(node):
        content = node.get("content", "")
        for line in content.splitlines():
            if line.strip().startswith("#"):
                return line.strip()
        return ""

    def render_folders_only(nid, indent=0):
        nonlocal current_line
        node = app.node_data.get(nid)
        if not node or node["type"] != "folder":
            return

        icon = "📁"
        name = node.get("name", "") + "/"
        status = node.get("status", "")
        md = node.get("markdown_short", "") or get_markdown_single_line(node)

        indent_str = "  " * indent
        line = f"{indent_str}{icon} {name}".ljust(55)
        line += "        "
        line += f"{status}   " if status else "    "
        line += md

        app.preview_text.insert("end", line + "\n")
        app.line_map[str(current_line)] = nid
        current_line += 1

        for child in app.tree.get_children(nid):
            render_folders_only(child, indent + 1)

    def render_classic(nid, indent=0):
        nonlocal current_line
        node = app.node_data.get(nid)
        if not node:
            return
        icon = "📁" if node["type"] == "folder" else "📄"
        name = node.get("name", "") + ("/" if node["type"] == "folder" else "")
        status = node.get("status", "")
        md = node.get("markdown_short", "") or get_markdown_single_line(node)
        indent_str = "  " * indent
        line = f"{indent_str}{icon} {name}".ljust(55)
        line += "        "
        line += f"{status}   " if status else "    "
        line += md
        app.preview_text.insert("end", line + "\n")
        app.line_map[str(current_line)] = nid
        current_line += 1
        for child in app.tree.get_children(nid):
            render_classic(child, indent + 1)

    def render_ascii(nid, prefix="", is_last=True):
        nonlocal current_line
        node = app.node_data.get(nid)
        if not node:
            return
        name = node.get("name", "") + ("/" if node["type"] == "folder" else "")
        status = node.get("status", "")
        connector = "└── " if is_last else "├── "
        line = f"{prefix}{connector}{name}".ljust(60)
        line += "        "
        line += f"{status}   " if status else "    "
        md = node.get("markdown_short", "") or get_markdown_single_line(node)
        line += md
        app.preview_text.insert("end", line + "\n")
        app.line_map[str(current_line)] = nid
        current_line += 1
        children = list(app.tree.get_children(nid))
        for i, child in enumerate(children):
            new_prefix = prefix + ("    " if is_last else "│   ")
            render_ascii(child, new_prefix, i == len(children) - 1)

    def render_columns(nid, indent=0):
        nonlocal current_line
        node = app.node_data.get(nid)
        if not node:
            return
        name = "  " * indent + node.get("name", "") + ("/" if node["type"] == "folder" else "")
        status = node.get("status", "")
        md = node.get("markdown_short", "") or get_markdown_single_line(node)
        line = name.ljust(30) + status.ljust(15) + md
        app.preview_text.insert("end", line + "\n")
        app.line_map[str(current_line)] = nid
        current_line += 1
        for child in app.tree.get_children(nid):
            render_columns(child, indent + 1)

    if mode == "folders":
        for top in app.tree.get_children(""):
            render_folders_only(top)
    elif mode == "clasico":
        for top in app.tree.get_children(""):
            render_classic(top)
    elif mode == "ascii":
        for i, top in enumerate(app.tree.get_children("")):
            render_ascii(top, "", i == len(app.tree.get_children("")) - 1)
    elif mode == "columnas":
        header = "Nombre".ljust(30) + "Estado".ljust(15) + "Markdown"
        app.preview_text.insert("end", header + "\n")
        app.preview_text.insert("end", "-" * 70 + "\n")
        current_line += 2
        for top in app.tree.get_children(""):
            render_columns(top)

    app.preview_text.config(state="disabled")
