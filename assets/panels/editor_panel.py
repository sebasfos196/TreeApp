# carpetatree/panels/editor_panel.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os

def setup_editor_panel(app):
    """
    Panel de edición avanzado unificado:
    - Campo de nombre
    - Campo markdown (3 líneas, editable, sincroniza en tiempo real)
    - Notas técnicas (con scrollbar)
    - Editor de código con números de línea y minimap visual
    - PanedWindow vertical para redimensionar áreas
    - Soporte para context menu y funciones legacy
    """
    # Header del editor
    editor_header = ttk.Frame(app.center_frame)
    editor_header.pack(fill="x", padx=5, pady=5)
    ttk.Label(editor_header, text="📝 EDITOR", font=("Segoe UI", 10, "bold")).pack(side="left")

    # Campo nombre
    name_frame = ttk.Frame(app.center_frame)
    name_frame.pack(fill="x", padx=5, pady=2)
    ttk.Label(name_frame, text="Nombre:").pack(side="left")
    app.name_entry = ttk.Entry(name_frame, font=("Segoe UI", 10))
    app.name_entry.pack(side="left", fill="x", expand=True, padx=5)
    app.name_entry.bind("<KeyRelease>", app.update_name)

    # Contenedor principal redimensionable
    main_paned = ttk.PanedWindow(app.center_frame, orient="vertical")
    main_paned.pack(fill="both", expand=True, padx=5, pady=5)

    # --- EDITOR 1: Markdown ---
    markdown_frame = ttk.LabelFrame(main_paned, text="📝 Markdown")
    main_paned.add(markdown_frame, weight=1)
    app.markdown_short = tk.Text(
        markdown_frame, height=3, wrap="word",
        font=("Segoe UI", 10),
        bg="#ffffff", fg="#333333",
        relief="flat", borderwidth=1
    )
    app.markdown_short.pack(fill="both", expand=True, padx=5, pady=5)
    app.markdown_short.bind("<KeyRelease>", lambda e: update_markdown_short(app))
    setup_text_context_menu(app, app.markdown_short)

    # --- EDITOR 2: Notas Técnicas ---
    notes_frame = ttk.LabelFrame(main_paned, text="📄 Notas Técnicas")
    main_paned.add(notes_frame, weight=2)
    notes_container = tk.Frame(notes_frame)
    notes_container.pack(fill="both", expand=True, padx=5, pady=5)
    app.explanation_text = tk.Text(
        notes_container, wrap="word",
        font=("Segoe UI", 10),
        bg="#ffffff", fg="#333333"
    )
    app.explanation_text.pack(side="left", fill="both", expand=True)
    notes_scrollbar = ttk.Scrollbar(notes_container, orient="vertical",
                                   command=app.explanation_text.yview)
    notes_scrollbar.pack(side="right", fill="y")
    app.explanation_text.config(yscrollcommand=notes_scrollbar.set)
    app.explanation_text.bind("<KeyRelease>", lambda e: update_explanation_text(app))
    setup_text_context_menu(app, app.explanation_text)

    # --- EDITOR 3: Código con números de línea y minimap ---
    code_frame = ttk.LabelFrame(main_paned, text="💻 Código")
    main_paned.add(code_frame, weight=2)
    code_container = tk.Frame(code_frame)
    code_container.pack(fill="both", expand=True, padx=5, pady=5)

    # Números de línea
    app.code_line_numbers = tk.Text(
        code_container, width=4, padx=3, pady=5,
        takefocus=0, border=0, state='disabled', wrap='none',
        font=("Consolas", app.config.get("font_size", 10)),
        bg="#f8f8f8", fg="#888888"
    )
    app.code_line_numbers.pack(side="left", fill="y")

    # Editor de código principal
    app.code_text = tk.Text(
        code_container, wrap="none",
        font=("Consolas", app.config.get("font_size", 10)),
        bg="#ffffff", fg="#333333",
        insertbackground="black",
        selectbackground="#264f78",
        selectforeground="white",
        relief="flat", borderwidth=1
    )
    app.code_text.pack(side="left", fill="both", expand=True)

    # Minimap a la derecha
    app.code_minimap = tk.Canvas(
        code_container, width=60, height=180, bg="#f4f4f4",
        highlightthickness=1, relief="ridge"
    )
    app.code_minimap.pack(side="left", fill="y", pady=(20, 0))

    # Scrollbars para código
    code_scrollbar_v = ttk.Scrollbar(code_container, orient="vertical",
                                     command=lambda *args: sync_scroll(app, *args))
    code_scrollbar_v.pack(side="right", fill="y")
    code_scrollbar_h = ttk.Scrollbar(code_frame, orient="horizontal",
                                     command=app.code_text.xview)
    code_scrollbar_h.pack(side="bottom", fill="x")
    app.code_text.config(
        yscrollcommand=lambda *args: scrollbar_set_with_lines(app, code_scrollbar_v, *args),
        xscrollcommand=code_scrollbar_h.set
    )

    # Eventos para código
    app.code_text.bind("<KeyRelease>", lambda e: update_code_text_with_lines(app, e))
    app.code_text.bind("<Button-1>", lambda e: update_code_line_numbers(app))
    app.code_text.bind("<MouseWheel>", lambda e: on_code_mousewheel(app, e))
    setup_text_context_menu(app, app.code_text)
    
    # Función para actualizar números de línea accesible desde app
    app.update_code_line_numbers = lambda: update_code_line_numbers(app)
    
    # COMPATIBILIDAD: Asegurar que text apunte a code_text
    app.text = app.code_text
    
    # Inicializar
    update_code_line_numbers(app)
    update_minimap(app)

# --- FUNCIONES AUXILIARES ---

def setup_text_context_menu(app, text_widget):
    """Configurar menú contextual para cualquier widget de texto"""
    context_menu = tk.Menu(app.root, tearoff=0)
    
    context_menu.add_command(label="📋 Copiar", 
                           command=lambda: text_widget.event_generate("<<Copy>>"))
    context_menu.add_command(label="✂️ Cortar", 
                           command=lambda: text_widget.event_generate("<<Cut>>"))
    context_menu.add_command(label="📥 Pegar", 
                           command=lambda: text_widget.event_generate("<<Paste>>"))
    context_menu.add_separator()
    context_menu.add_command(label="🔄 Deshacer", 
                           command=lambda: safe_undo(text_widget))
    context_menu.add_command(label="↩️ Rehacer", 
                           command=lambda: safe_redo(text_widget))
    context_menu.add_separator()
    context_menu.add_command(label="🔍 Seleccionar Todo", 
                           command=lambda: text_widget.tag_add(tk.SEL, "1.0", tk.END))
    
    def show_context_menu(event):
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        except:
            pass
    
    text_widget.bind("<Button-3>", show_context_menu)

def safe_undo(text_widget):
    """Deshacer seguro que no causa errores"""
    try:
        text_widget.edit_undo()
    except tk.TclError:
        pass

def safe_redo(text_widget):
    """Rehacer seguro que no causa errores"""
    try:
        text_widget.edit_redo()
    except tk.TclError:
        pass

def update_markdown_short(app):
    """Actualizar markdown resumido"""
    if (app.current_node and app.current_node in app.node_data and 
        hasattr(app, 'markdown_short')):
        content = app.markdown_short.get("1.0", "end-1c")
        app.node_data[app.current_node]["markdown_short"] = content
        app.node_data[app.current_node]["modified"] = datetime.now().isoformat()
        app.mark_unsaved()
        
        # Actualizar vista previa inmediatamente
        if hasattr(app, 'update_preview'):
            app.root.after(100, app.update_preview)
        
        # Actualizar display del árbol en tiempo real
        if hasattr(app, 'update_tree_display_realtime'):
            app.update_tree_display_realtime(app.current_node)

def update_explanation_text(app):
    """Actualizar explicación extendida"""
    if (app.current_node and app.current_node in app.node_data and 
        hasattr(app, 'explanation_text')):
        content = app.explanation_text.get("1.0", "end-1c")
        app.node_data[app.current_node]["explanation"] = content
        app.node_data[app.current_node]["modified"] = datetime.now().isoformat()
        app.mark_unsaved()

def update_code_text(app, event=None):
    """Actualizar código y notas técnicas"""
    if (app.current_node and app.current_node in app.node_data and 
        hasattr(app, 'code_text')):
        content = app.code_text.get("1.0", "end-1c")
        app.node_data[app.current_node]["code"] = content
        app.node_data[app.current_node]["modified"] = datetime.now().isoformat()
        app.mark_unsaved()

def sync_scroll(app, *args):
    """Sincronizar scroll entre código y números de línea"""
    app.code_text.yview(*args)
    app.code_line_numbers.yview(*args)

def scrollbar_set_with_lines(app, scrollbar, first, last):
    """Configurar scrollbar y sincronizar líneas"""
    scrollbar.set(first, last)
    app.code_line_numbers.yview_moveto(first)

def update_code_line_numbers(app):
    """Actualizar números de línea del editor de código"""
    if not hasattr(app, 'code_line_numbers') or not hasattr(app, 'code_text'):
        return
        
    try:
        app.code_line_numbers.config(state='normal')
        app.code_line_numbers.delete("1.0", "end")
        
        # Contar líneas en el editor de código
        line_count = int(app.code_text.index('end').split('.')[0]) - 1
        line_numbers = "\n".join(str(i) for i in range(1, max(line_count + 1, 2)))
        
        app.code_line_numbers.insert("1.0", line_numbers)
        app.code_line_numbers.config(state='disabled')
    except Exception:
        pass

def on_code_mousewheel(app, event):
    """Manejar scroll del mouse en editor de código"""
    try:
        app.code_line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"
    except Exception:
        pass

def update_code_text_with_lines(app, event):
    """Actualizar código y números de línea"""
    update_code_text(app, event)
    update_minimap(app)
    app.root.after_idle(lambda: update_code_line_numbers(app))

def update_minimap(app):
    """Actualizar minimap visual del código"""
    if not hasattr(app, 'code_minimap') or not hasattr(app, 'code_text'):
        return
        
    try:
        code = app.code_text.get("1.0", "end-1c")
        lines = code.splitlines()
        canvas = app.code_minimap
        canvas.delete("all")
        
        h = int(canvas['height'])
        w = int(canvas['width'])
        n = max(1, len(lines))
        line_h = h / n
        
        for i, line in enumerate(lines):
            y0 = i * line_h
            y1 = (i + 1) * line_h
            length = min(len(line) / 70, 1.0)  # Escala el largo de la línea
            x1 = 8 + int(length * (w - 20))
            color = "#bbb" if i % 2 == 0 else "#999"
            canvas.create_rectangle(8, y0, x1, y1, fill=color, outline="")
    except Exception:
        pass

def export_professional_docs(app):
    """Exportar documentación profesional en múltiples formatos"""
    if not app.node_data:
        messagebox.showwarning("Exportar", "No hay contenido para exportar")
        return
    
    # Diálogo de opciones de exportación
    export_dialog = tk.Toplevel(app.root)
    export_dialog.title("Exportar Documentación Profesional")
    export_dialog.geometry("400x300")
    export_dialog.transient(app.root)
    export_dialog.grab_set()
    
    # Centrar diálogo
    export_dialog.update_idletasks()
    x = (export_dialog.winfo_screenwidth() // 2) - (200)
    y = (export_dialog.winfo_screenheight() // 2) - (150)
    export_dialog.geometry(f"400x300+{x}+{y}")
    
    ttk.Label(export_dialog, text="Selecciona los tipos de exportación:", 
             font=("Segoe UI", 10, "bold")).pack(pady=10)
    
    # Variables para checkboxes
    export_tree_markdown = tk.BooleanVar(value=True)
    export_tree_explanation = tk.BooleanVar(value=True)
    export_code_files = tk.BooleanVar(value=True)
    
    # Checkboxes
    ttk.Checkbutton(export_dialog, text="📄 Árbol con Markdown Resumido", 
                   variable=export_tree_markdown).pack(anchor="w", padx=20, pady=5)
    ttk.Checkbutton(export_dialog, text="📖 Documentación con Explicaciones", 
                   variable=export_tree_explanation).pack(anchor="w", padx=20, pady=5)
    ttk.Checkbutton(export_dialog, text="💻 Archivos de Código Separados", 
                   variable=export_code_files).pack(anchor="w", padx=20, pady=5)
    
    def do_export():
        folder = filedialog.askdirectory(title="Selecciona carpeta de destino")
        if not folder:
            return
            
        try:
            if export_tree_markdown.get():
                export_tree_with_markdown(app, folder)
            if export_tree_explanation.get():
                export_documentation_with_explanations(app, folder)
            if export_code_files.get():
                export_code_files_separately(app, folder)
            
            messagebox.showinfo("Éxito", f"Documentación exportada en:\n{folder}")
            export_dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")
    
    # Botones
    button_frame = ttk.Frame(export_dialog)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="✅ Exportar", command=do_export).pack(side="left", padx=10)
    ttk.Button(button_frame, text="❌ Cancelar", command=export_dialog.destroy).pack(side="left", padx=10)

def export_tree_with_markdown(app, folder):
    """Exportar árbol con markdown resumido"""
    content = "# Estructura del Proyecto\n\n"
    
    def build_tree(node_id, indent=0):
        if node_id not in app.node_data:
            return ""
        
        node = app.node_data[node_id]
        icon = "📁" if node["type"] == "folder" else "📄"
        name = node.get('name', 'Sin nombre')
        
        if node["type"] == "folder":
            name += "/"
        
        # Obtener markdown resumido del NUEVO campo
        markdown = node.get('markdown_short', '')
        if not markdown.strip():
            markdown = f"# {name.rstrip('/')}"
        
        line = "  " * indent + f"{icon} {name}"
        if markdown.strip():
            line += f" - {markdown.strip()}"
        
        result = line + "\n"
        
        # Procesar hijos
        for child in app.tree.get_children(node_id):
            result += build_tree(child, indent + 1)
        
        return result
    
    for top in app.tree.get_children(""):
        content += build_tree(top)
    
    with open(f"{folder}/estructura_proyecto.md", 'w', encoding='utf-8') as f:
        f.write(content)

def export_documentation_with_explanations(app, folder):
    """Exportar documentación profesional con explicaciones"""
    content = f"""# Documentación del Proyecto

## Estructura y Descripción Detallada

**Generado:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**Total de elementos:** {len(app.node_data)}

---

"""
    
    def build_documentation(node_id, level=1):
        if node_id not in app.node_data:
            return ""
        
        node = app.node_data[node_id]
        name = node.get('name', 'Sin nombre')
        node_type = "Carpeta" if node["type"] == "folder" else "Archivo"
        
        # Header con nivel apropiado
        header_prefix = "#" * (level + 1)
        result = f"{header_prefix} {name}\n\n"
        result += f"**Tipo:** {node_type}\n"
        result += f"**Ruta:** `{get_node_path(app, node_id)}`\n\n"
        
        # Markdown resumido del NUEVO campo
        markdown_short = node.get('markdown_short', '').strip()
        if markdown_short:
            result += f"**Resumen:** {markdown_short}\n\n"
        
        # Explicación extendida del NUEVO campo
        explanation = node.get('explanation', '').strip()
        if explanation:
            result += "**Descripción Detallada:**\n\n"
            result += explanation + "\n\n"
        
        # Código del NUEVO campo (solo mencionarlo, no incluirlo)
        code = node.get('code', '').strip()
        if code:
            result += f"**Notas Técnicas:** Este elemento contiene {len(code.splitlines())} líneas de código/notas técnicas.\n\n"
        
        result += "---\n\n"
        
        # Procesar hijos
        for child in app.tree.get_children(node_id):
            result += build_documentation(child, level + 1)
        
        return result
    
    for top in app.tree.get_children(""):
        content += build_documentation(top)
    
    # Footer profesional
    content += f"""

## Información del Documento

**Herramienta:** Workspace Jumper v4 Pro  
**Campos exportados:** Markdown resumido, explicaciones detalladas, código técnico

---

© {datetime.now().year} - Documentación generada automáticamente
"""
    
    with open(f"{folder}/documentacion_completa.md", 'w', encoding='utf-8') as f:
        f.write(content)

def export_code_files_separately(app, folder):
    """Exportar archivos de código por separado con sus extensiones"""
    code_folder = os.path.join(folder, "codigo_extraido")
    os.makedirs(code_folder, exist_ok=True)
    
    file_count = 0
    
    for node_id, node_data in app.node_data.items():
        # Usar el NUEVO campo 'code' en lugar de 'content'
        code_content = node_data.get('code', '').strip()
        if not code_content:
            continue
        
        # Determinar extensión basada en el nombre del archivo
        name = node_data.get('name', f'archivo_{file_count}')
        
        # Si no tiene extensión, agregar .txt
        if '.' not in name:
            if node_data['type'] == 'folder':
                filename = f"{name}_notes.md"
            else:
                filename = f"{name}.txt"
        else:
            filename = name
        
        # Crear contenido del archivo con header
        file_content = f"""/*
 * Archivo: {filename}
 * Origen: {get_node_path(app, node_id)}
 * Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
 * Tipo: {node_data['type'].title()}
 */

{code_content}
"""
        
        # Escribir archivo
        file_path = os.path.join(code_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        file_count += 1
    
    # Crear índice de archivos generados
    index_content = f"""# Índice de Archivos de Código

**Total de archivos generados:** {file_count}
**Fecha de generación:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## Archivos:

"""
    
    for node_id, node_data in app.node_data.items():
        if node_data.get('code', '').strip():
            name = node_data.get('name', 'archivo')
            if '.' not in name:
                filename = f"{name}_notes.md" if node_data['type'] == 'folder' else f"{name}.txt"
            else:
                filename = name
            
            index_content += f"- `{filename}` - {get_node_path(app, node_id)}\n"
    
    with open(os.path.join(code_folder, "INDICE.md"), 'w', encoding='utf-8') as f:
        f.write(index_content)

def get_node_path(app, node_id):
    """Obtener ruta completa de un nodo"""
    if node_id not in app.node_data:
        return ""
    
    path_parts = []
    current = node_id
    
    # Reconstruir path desde el árbol
    def find_parent(child_id):
        for item_id in app.node_data:
            if child_id in app.tree.get_children(item_id):
                return item_id
        return None
    
    while current and current in app.node_data:
        node_name = app.node_data[current]['name']
        if app.node_data[current]['type'] == 'folder':
            node_name += "/"
        path_parts.append(node_name)
        
        # Buscar padre
        current = find_parent(current)
    
    path_parts.reverse()
    return "/".join(path_parts) if path_parts else app.node_data[node_id]['name']