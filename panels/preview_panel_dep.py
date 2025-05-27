## carpetatree/panels/preview_panel.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def setup_preview_panel(app):
    """Configurar panel de vista previa CORREGIDO"""
    
    # Header de vista previa LIMPIO
    preview_header = ttk.Frame(app.right_frame)
    preview_header.pack(fill="x", padx=5, pady=5)
    
    ttk.Label(preview_header, text="🔍 Vista Previa", 
              font=("Segoe UI", 10, "bold")).pack(side="left")
    
    # Área de vista previa
    preview_frame = ttk.Frame(app.right_frame)
    preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Texto de vista previa SIN word wrap - línea infinita
    text_frame = tk.Frame(preview_frame)
    text_frame.pack(fill="both", expand=True)
    
    app.preview_text = tk.Text(text_frame, wrap="none", state="normal",
                              font=("Consolas", app.config["font_size"]))
    app.preview_text.pack(side="left", fill="both", expand=True)
    
    # Scrollbars vertical Y horizontal para navegación infinita
    preview_scrollbar_v = ttk.Scrollbar(text_frame, orient="vertical", 
                                       command=app.preview_text.yview)
    preview_scrollbar_v.pack(side="right", fill="y")
    
    preview_scrollbar_h = ttk.Scrollbar(preview_frame, orient="horizontal", 
                                       command=app.preview_text.xview)
    preview_scrollbar_h.pack(side="bottom", fill="x")
    
    app.preview_text.config(yscrollcommand=preview_scrollbar_v.set, 
                           xscrollcommand=preview_scrollbar_h.set)
    
    # Configurar colores para mejor legibilidad
    app.preview_text.config(
        bg="#f8f8f8",
        fg="#333333",
        selectbackground="#264f78",
        selectforeground="white"
    )
    
    # BOTONES por debajo del título
    button_frame = ttk.Frame(app.right_frame)
    button_frame.pack(fill="x", padx=5, pady=2)
    
    # Selector de modo - solo 3 opciones
    mode_frame = ttk.Frame(button_frame)
    mode_frame.pack(side="left")
    
    app.preview_mode = tk.StringVar(value="clasico")
    
    modes = [
        ("Clásico", "clasico"),
        ("ASCII", "ascii"), 
        ("Columnas", "columnas")
    ]
    
    for text, value in modes:
        ttk.Radiobutton(mode_frame, text=text, variable=app.preview_mode, 
                       value=value, command=app.update_preview).pack(side="left", padx=2)
    
    # Botones de acción a la derecha
    action_frame = ttk.Frame(button_frame)
    action_frame.pack(side="right")
    
    ttk.Button(action_frame, text="📄 Exportar TXT", 
              command=lambda: export_preview_txt(app)).pack(side="left", padx=2)
    
    ttk.Button(action_frame, text="📋 Seleccionar Todo", 
              command=lambda: select_all_preview(app)).pack(side="left", padx=2)
    
    # NUEVO: Botón de exportar documentación MOVIDO aquí
    ttk.Button(action_frame, text="📖 Exportar Documentación", 
              command=lambda: export_professional_docs(app)).pack(side="left", padx=2)
    
    # Configurar eventos de selección y copia - CORREGIDO
    app.preview_text.bind("<Control-a>", lambda e: select_all_preview(app))
    app.preview_text.bind("<Control-c>", lambda e: copy_preview_selection(app))
    app.preview_text.bind("<Button-3>", lambda e: show_preview_context_menu(app, e))

def copy_preview_selection(app):
    """Copiar selección de la vista previa - FUNCIONAL"""
    try:
        # Si hay selección, copiarla
        if app.preview_text.tag_ranges(tk.SEL):
            selected_text = app.preview_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            app.root.clipboard_clear()
            app.root.clipboard_append(selected_text)
        return "break"
    except:
        pass

def show_preview_context_menu(app, event):
    """Menú contextual para vista previa"""
    if not hasattr(app, 'preview_context_menu'):
        app.preview_context_menu = tk.Menu(app.root, tearoff=0)
        app.preview_context_menu.add_command(label="📋 Copiar", command=lambda: copy_preview_selection(app))
        app.preview_context_menu.add_command(label="🔍 Seleccionar Todo", command=lambda: select_all_preview(app))
        app.preview_context_menu.add_separator()
        app.preview_context_menu.add_command(label="📄 Exportar TXT", command=lambda: export_preview_txt(app))
    
    try:
        app.preview_context_menu.tk_popup(event.x_root, event.y_root)
    except:
        pass

def select_all_preview(app):
    """Seleccionar todo el contenido de la vista previa"""
    try:
        app.preview_text.tag_add(tk.SEL, "1.0", tk.END)
        app.preview_text.mark_set(tk.INSERT, "1.0")
        app.preview_text.see(tk.INSERT)
        app.preview_text.focus_set()
        return "break"
    except:
        pass

def export_preview_txt(app):
    """Exportar contenido de vista previa a archivo TXT"""
    try:
        content = app.preview_text.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showwarning("Exportar", "No hay contenido en la vista previa para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Vista Previa",
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Éxito", f"Vista previa exportada a:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

def get_markdown_single_line(content):
    """Extraer contenido markdown resumido - CORREGIDO para usar nuevo campo"""
    # Primero verificar si hay markdown resumido específico
    if isinstance(content, dict) and content.get('markdown_short'):
        return content['markdown_short'].strip()
    
    # Si content es un nodo completo, extraer markdown_short
    if hasattr(content, 'get') and content.get('markdown_short'):
        return content['markdown_short'].strip()
    
    # Si es string, procesarlo como antes pero sin límites
    if not content or not isinstance(content, str):
        return ""
    
    # Buscar primer header markdown
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line  # Retornar COMPLETO sin límite de caracteres
    
    # Si no hay header, tomar todas las líneas y convertir a una sola línea
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if lines:
        # Unir TODAS las líneas en una sola - SIN LÍMITE de caracteres
        single_line = " ".join(lines)
        return single_line  # Retornar TODO el contenido en una línea infinita
    
    return ""

def update_preview_improved(app):
    """Vista previa mejorada con alineación perfecta CORREGIDA"""
    if not hasattr(app, "preview_mode") or not hasattr(app, "preview_text"):
        return

    mode = app.preview_mode.get()
    
    # Configurar SIN word wrap - línea infinita
    app.preview_text.config(state="normal", wrap="none")
    app.preview_text.delete("1.0", "end")

    # Mapeo de líneas para navegación
    app.line_map = {}
    current_line = 1

    # MODO 1: CLÁSICO - Formato tabla CORREGIDO
    if mode == "clasico":
        def print_clasico(nid, indent=0):
            nonlocal current_line
            if nid not in app.node_data:
                return
                
            node = app.node_data[nid]
            icon = "📁" if node["type"] == "folder" else "📄"
            name = node.get('name', 'Sin nombre')
            
            # Mostrar carpetas con "/" al final
            if node["type"] == "folder":
                name += "/"
            
            # Obtener estado
            status = node.get('status', '')
            if status == "🕓":
                status = "⬜"
            
            # ALINEACIÓN PERFECTA - 55 caracteres base + espaciado fijo para estado
            indent_str = "  " * indent
            name_with_icon = f"{indent_str}{icon} {name}"
            
            # Espaciado FIJO: 55 caracteres para nombre + icono
            line = name_with_icon.ljust(55)
            
            # Estado SIEMPRE en la MISMA posición - 8 espacios antes del estado
            line += "        "  # 8 espacios fijos
            if status:
                line += f"{status}   "  # Estado + 3 espacios después
            else:
                line += "    "  # 4 espacios cuando no hay estado
            
            # Markdown SIEMPRE empieza en la MISMA columna (posición 67)
            md_content = node.get('markdown_short', '').strip()
            if not md_content:
                md_content = get_markdown_single_line(node.get("content", ""))
            if md_content:
                line += md_content
            
            app.preview_text.insert("end", line + "\n")
            app.line_map[str(current_line)] = nid
            current_line += 1
            
            # Procesar hijos manteniendo jerarquía
            for child in app.tree.get_children(nid):
                print_clasico(child, indent + 1)
        
        # Mostrar todos los nodos raíz
        for top in app.tree.get_children(""):
            print_clasico(top)

    # MODO 2: ASCII - CORREGIDO
    elif mode == "ascii":
        def print_ascii(nid, prefix="", is_last=True):
            nonlocal current_line
            if nid not in app.node_data:
                return
            
            node = app.node_data[nid]
            name = node.get('name', 'Sin nombre')
            status = node.get('status', '')
            
            # Mostrar carpetas con "/" al final
            if node["type"] == "folder":
                name += "/"
            
            # Cambiar 🕓 por ⬜
            if status == "🕓":
                status = "⬜"
            
            # Determinar conector
            if prefix == "":  # Nodo raíz
                connector = "└── "
                base_line = f"{connector}{name}"
            else:
                connector = "└── " if is_last else "├── "
                base_line = f"{prefix}{connector}{name}"
            
            # ALINEACIÓN ASCII PERFECTA - 60 caracteres base + 8 espacios fijos para estado
            line = base_line.ljust(60)
            
            # Estado SIEMPRE en la MISMA posición independiente del contenido
            line += "        "  # 8 espacios fijos ANTES del estado
            if status:
                line += f"{status}   "  # Estado + 3 espacios
            else:
                line += "    "  # 4 espacios cuando no hay estado
            
            # Markdown SIEMPRE empieza en la MISMA columna (posición 72)
            md_content = node.get('markdown_short', '').strip()
            if not md_content:
                md_content = get_markdown_single_line(node.get("content", ""))
            if md_content:
                line += md_content
            
            app.preview_text.insert("end", line + "\n")
            app.line_map[str(current_line)] = nid
            current_line += 1
            
            # Procesar hijos
            children = list(app.tree.get_children(nid))
            for i, child in enumerate(children):
                is_child_last = (i == len(children) - 1)
                new_prefix = prefix + ("    " if is_last else "│   ")
                print_ascii(child, new_prefix, is_child_last)
        
        # Procesar nodos raíz
        root_children = list(app.tree.get_children(""))
        for i, top in enumerate(root_children):
            is_top_last = (i == len(root_children) - 1)
            print_ascii(top, "", is_top_last)

    # MODO 3: COLUMNAS - ALINEACIÓN PERFECTA CORREGIDA
    elif mode == "columnas":
        # Header con espaciado FIJO y SEPARACIÓN CORRECTA
        header = "Nombre".ljust(30) + "Estado".ljust(15) + "Markdown"
        app.preview_text.insert("end", header + "\n")
        separator = "-" * 70
        app.preview_text.insert("end", separator + "\n")
        current_line += 2
        
        def print_columnas(nid, indent=0):
            nonlocal current_line
            if nid not in app.node_data:
                return
            
            node = app.node_data[nid]
            name = "  " * indent + node.get('name', 'Sin nombre')
            status = node.get('status', '')
            
            # Mostrar carpetas con "/" al final
            if node["type"] == "folder":
                name += "/"
            
            # Cambiar 🕓 por ⬜
            if status == "🕓":
                status = "⬜"
            
            # Obtener markdown resumido en una línea
            md_content = node.get('markdown_short', '').strip()
            if not md_content:
                md_content = get_markdown_single_line(node.get("content", ""))
            
            # FORMATEAR CON ESPACIADO FIJO CORREGIDO
            name_part = name.ljust(30)  # 50 caracteres fijos para nombre
            status_part = status.ljust(15)  # 10 caracteres fijos para estado CON SEPARACIÓN
            line = name_part + status_part + md_content
            
            app.preview_text.insert("end", line + "\n")
            app.line_map[str(current_line)] = nid
            current_line += 1
            
            # Procesar hijos
            for child in app.tree.get_children(nid):
                print_columnas(child, indent + 1)
        
        for top in app.tree.get_children(""):
            print_columnas(top)

    # Configurar eventos de navegación y copia CORREGIDOS
    def on_click(event):
        try:
            index = app.preview_text.index(f"@{event.x},{event.y}")
            line = index.split(".")[0]
            nid = app.line_map.get(line)
            if nid and nid in app.node_data:
                app.tree.selection_set(nid)
                app.current_node = nid
                if hasattr(app, 'on_select'):
                    event_obj = type('Event', (), {})()
                    app.on_select(event_obj)
        except:
            pass

    # Bindear eventos CORREGIDOS
    app.preview_text.bind("<Button-1>", on_click)
    app.preview_text.bind("<Control-c>", lambda e: copy_preview_selection(app))
    app.preview_text.bind("<Control-a>", lambda e: select_all_preview(app))