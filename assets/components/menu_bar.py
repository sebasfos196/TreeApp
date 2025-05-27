# carpetatree/components/menu_bar.py

import tkinter as tk

def setup_menu_bar(app):
    menubar = tk.Menu(app.root)
    app.root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Archivo", menu=file_menu)
    file_menu.add_command(label="Nuevo Proyecto", command=app.new_project)
    file_menu.add_command(label="Abrir Proyecto...", command=app.open_project)
    file_menu.add_separator()
    file_menu.add_command(label="Guardar", command=app.save_project)
    file_menu.add_command(label="Guardar Como...", command=app.save_project_as)
    file_menu.add_separator()
    file_menu.add_command(label="Exportar HTML", command=app.export_html)
    file_menu.add_command(label="Exportar Texto", command=app.export_text)
    file_menu.add_separator()
    file_menu.add_command(label="Salir", command=app.on_closing)

    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Editar", menu=edit_menu)
    edit_menu.add_command(label="Deshacer", command=app.undo)
    edit_menu.add_command(label="Rehacer", command=app.redo)
    edit_menu.add_separator()
    edit_menu.add_command(label="Buscar y Reemplazar", command=app.show_search_dialog)
    edit_menu.add_separator()
    edit_menu.add_command(label="Insertar Tabla", command=app.insert_table)
    edit_menu.add_command(label="Insertar Link", command=app.insert_link)
    edit_menu.add_command(label="Insertar Imagen", command=app.insert_image)

    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Ver", menu=view_menu)

    theme_menu = tk.Menu(view_menu, tearoff=0)
    view_menu.add_cascade(label="Tema", menu=theme_menu)
    for theme in app.style.themes:
        theme_menu.add_command(label=theme.title(), command=lambda t=theme: app.change_theme(t))

    font_menu = tk.Menu(view_menu, tearoff=0)
    view_menu.add_cascade(label="Tamaño de Fuente", menu=font_menu)
    for size in [8, 9, 10, 11, 12, 14, 16]:
        font_menu.add_command(label=f"{size}pt", command=lambda s=size: app.change_font_size(s))

    view_menu.add_separator()
    view_menu.add_command(label="Modo Zen", command=app.toggle_zen_mode)
    view_menu.add_command(label="Panel de Estado", command=app.toggle_status_bar)

    tools_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Herramientas", menu=tools_menu)
    tools_menu.add_command(label="Estadísticas del Proyecto", command=app.show_project_stats)
    tools_menu.add_command(label="Validar Enlaces", command=app.validate_links)
    tools_menu.add_separator()
    tools_menu.add_command(label="Configuración", command=app.show_preferences)

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Ayuda", menu=help_menu)
    help_menu.add_command(label="Atajos de Teclado", command=app.show_shortcuts)
    help_menu.add_command(label="Guía Markdown", command=app.show_markdown_guide)
    help_menu.add_separator()
    help_menu.add_command(label="Acerca de", command=app.show_about)
