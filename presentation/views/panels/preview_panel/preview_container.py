# presentation/views/panels/preview_panel/preview_container.py
"""
Panel de Vista Previa con 4 modos de visualización del árbol.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional
from datetime import datetime
from domain.node.node_entity import Node


class PreviewModes:
    """Constantes para los modos de vista previa."""
    CLASSIC = "Clásico"
    ASCII_FULL = "ASCII Completo"
    ASCII_FOLDERS = "ASCII Solo Carpetas"
    COLUMNS = "Columnas"


class PreviewContainer:
    """Contenedor principal del panel de vista previa."""
    
    def __init__(self, parent_frame, node_repository):
        self.parent_frame = parent_frame
        self.node_repository = node_repository
        self.current_mode = PreviewModes.CLASSIC
        
        # Configuraciones por modo
        self.config = {
            PreviewModes.CLASSIC: {
                'indent_spaces': 4,
                'show_icons': True,
                'show_status': True,
                'show_markdown': True,
                'markdown_max_length': 50,
                'max_depth': 10
            },
            PreviewModes.ASCII_FULL: {
                'show_icons': True,
                'show_status': True,
                'show_markdown': True,
                'markdown_max_length': 40,
                'use_unicode': True,
                'max_depth': 10
            },
            PreviewModes.ASCII_FOLDERS: {
                'show_icons': True,
                'show_file_count': True,
                'show_status_summary': True,
                'max_depth': 10
            },
            PreviewModes.COLUMNS: {
                'col_path_width': 200,
                'col_status_width': 80,
                'col_markdown_width': 300,
                'show_headers': True,
                'alternate_colors': True,
                'markdown_max_length': 60
            }
        }
        
        self._setup_ui()
        self._refresh_preview()
    
    def _setup_ui(self):
        """Configurar interfaz del panel de vista previa."""
        # Frame principal
        self.main_frame = tk.Frame(self.parent_frame, bg='#f8f8f8')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Header con título y controles
        self._setup_header()
        
        # Área de vista previa principal
        self._setup_preview_area()
        
        # Panel de configuración (inicialmente oculto)
        self._setup_config_panel()
        
        # Botones de exportación
        self._setup_export_buttons()
    
    def _setup_header(self):
        """Configurar encabezado con controles."""
        header_frame = tk.Frame(self.main_frame, bg='#f8f8f8')
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="🔍 Vista Previa",
            font=('Arial', 14, 'bold'),
            bg='#f8f8f8',
            fg='#2c3e50'
        )
        title_label.pack(side=tk.LEFT)
        
        # Selector de modo
        mode_frame = tk.Frame(header_frame, bg='#f8f8f8')
        mode_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            mode_frame,
            text="Modo:",
            font=('Arial', 10),
            bg='#f8f8f8'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.mode_combo = ttk.Combobox(
            mode_frame,
            values=[PreviewModes.CLASSIC, PreviewModes.ASCII_FULL, 
                   PreviewModes.ASCII_FOLDERS, PreviewModes.COLUMNS],
            state="readonly",
            width=15
        )
        self.mode_combo.set(self.current_mode)
        self.mode_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.mode_combo.bind('<<ComboboxSelected>>', self._on_mode_change)
        
        # Botón de configuración
        self.config_btn = tk.Button(
            mode_frame,
            text="⚙️",
            command=self._toggle_config,
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            width=3,
            relief=tk.FLAT
        )
        self.config_btn.pack(side=tk.LEFT)
    
    def _setup_preview_area(self):
        """Configurar área principal de vista previa."""
        # Frame para vista previa con scroll
        preview_frame = tk.Frame(self.main_frame, bg='#ffffff', relief=tk.SUNKEN, bd=1)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Text widget para mostrar la vista previa
        text_frame = tk.Frame(preview_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(
            text_frame,
            font=('Consolas', 10),
            bg='#ffffff',
            fg='#2c3e50',
            wrap=tk.NONE,
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=5,
            padx=10,
            pady=10
        )
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.preview_text.yview)
        h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_text.xview)
        
        self.preview_text.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Layout
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _setup_config_panel(self):
        """Configurar panel de configuración (colapsable)."""
        self.config_frame = tk.Frame(self.main_frame, bg='#ecf0f1', relief=tk.RAISED, bd=1)
        self.config_visible = False  # Inicialmente oculto
        
        # Título del panel de configuración
        config_header = tk.Frame(self.config_frame, bg='#bdc3c7')
        config_header.pack(fill=tk.X)
        
        tk.Label(
            config_header,
            text="⚙️ Configuración",
            font=('Arial', 11, 'bold'),
            bg='#bdc3c7',
            fg='#2c3e50'
        ).pack(pady=5)
        
        # Contenido de configuración (se llenará dinámicamente)
        self.config_content = tk.Frame(self.config_frame, bg='#ecf0f1')
        self.config_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _setup_export_buttons(self):
        """Configurar botones de exportación."""
        export_frame = tk.Frame(self.main_frame, bg='#f8f8f8')
        export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botón exportar TXT
        tk.Button(
            export_frame,
            text="📄 Exportar TXT",
            command=self._export_txt,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón refrescar
        tk.Button(
            export_frame,
            text="🔄 Refrescar",
            command=self._refresh_preview,
            bg='#f39c12',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT)
    
    def _on_mode_change(self, event=None):
        """Manejar cambio de modo."""
        self.current_mode = self.mode_combo.get()
        self._update_config_panel()
        self._refresh_preview()
        print(f"🔄 Modo cambiado a: {self.current_mode}")
    
    def _toggle_config(self):
        """Mostrar/ocultar panel de configuración."""
        if self.config_visible:
            self.config_frame.pack_forget()
            self.config_visible = False
            self.config_btn.config(text="⚙️")
        else:
            self.config_frame.pack(fill=tk.X, padx=5, pady=(0, 5), before=self.preview_text.master)
            self.config_visible = True
            self.config_btn.config(text="❌")
            self._update_config_panel()
    
    def _update_config_panel(self):
        """Actualizar contenido del panel de configuración según el modo."""
        # Limpiar contenido anterior
        for widget in self.config_content.winfo_children():
            widget.destroy()
        
        current_config = self.config[self.current_mode]
        
        if self.current_mode == PreviewModes.CLASSIC:
            self._create_classic_config(current_config)
        elif self.current_mode == PreviewModes.ASCII_FULL:
            self._create_ascii_full_config(current_config)
        elif self.current_mode == PreviewModes.ASCII_FOLDERS:
            self._create_ascii_folders_config(current_config)
        elif self.current_mode == PreviewModes.COLUMNS:
            self._create_columns_config(current_config)
    
    def _create_classic_config(self, config):
        """Crear configuración para modo Clásico."""
        # Espacios de indentación
        indent_frame = tk.Frame(self.config_content, bg='#ecf0f1')
        indent_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(indent_frame, text="Espacios de indentación:", bg='#ecf0f1').pack(side=tk.LEFT)
        indent_var = tk.IntVar(value=config['indent_spaces'])
        indent_spin = tk.Spinbox(indent_frame, from_=1, to=8, textvariable=indent_var, width=5)
        indent_spin.pack(side=tk.RIGHT)
        indent_var.trace('w', lambda *args: self._update_config('indent_spaces', indent_var.get()))
        
        # Checkboxes
        self._create_checkbox_config(config, 'show_icons', "Mostrar iconos (📁📄)")
        self._create_checkbox_config(config, 'show_status', "Mostrar estados (✅❌⬜)")
        self._create_checkbox_config(config, 'show_markdown', "Mostrar markdown")
        
        # Longitud máxima de markdown
        if config['show_markdown']:
            md_frame = tk.Frame(self.config_content, bg='#ecf0f1')
            md_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(md_frame, text="Longitud máx. markdown:", bg='#ecf0f1').pack(side=tk.LEFT)
            md_var = tk.IntVar(value=config['markdown_max_length'])
            md_spin = tk.Spinbox(md_frame, from_=20, to=100, textvariable=md_var, width=5)
            md_spin.pack(side=tk.RIGHT)
            md_var.trace('w', lambda *args: self._update_config('markdown_max_length', md_var.get()))
    
    def _create_ascii_full_config(self, config):
        """Crear configuración para modo ASCII Completo."""
        self._create_checkbox_config(config, 'show_icons', "Mostrar iconos")
        self._create_checkbox_config(config, 'show_status', "Mostrar estados")
        self._create_checkbox_config(config, 'show_markdown', "Mostrar markdown")
        self._create_checkbox_config(config, 'use_unicode', "Usar caracteres Unicode")
    
    def _create_ascii_folders_config(self, config):
        """Crear configuración para modo ASCII Solo Carpetas."""
        self._create_checkbox_config(config, 'show_icons', "Mostrar iconos")
        self._create_checkbox_config(config, 'show_file_count', "Mostrar contador de archivos")
        self._create_checkbox_config(config, 'show_status_summary', "Mostrar resumen de estados")
    
    def _create_columns_config(self, config):
        """Crear configuración para modo Columnas."""
        # Anchos de columnas
        for col_name, label in [('col_path_width', 'Ancho Ruta:'), 
                               ('col_status_width', 'Ancho Estado:'),
                               ('col_markdown_width', 'Ancho Markdown:')]:
            col_frame = tk.Frame(self.config_content, bg='#ecf0f1')
            col_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(col_frame, text=label, bg='#ecf0f1').pack(side=tk.LEFT)
            col_var = tk.IntVar(value=config[col_name])
            col_spin = tk.Spinbox(col_frame, from_=50, to=500, textvariable=col_var, width=5)
            col_spin.pack(side=tk.RIGHT)
            col_var.trace('w', lambda *args, name=col_name, var=col_var: self._update_config(name, var.get()))
        
        # Checkboxes
        self._create_checkbox_config(config, 'show_headers', "Mostrar encabezados")
        self._create_checkbox_config(config, 'alternate_colors', "Colores alternados")
    
    def _create_checkbox_config(self, config, key, label):
        """Crear checkbox de configuración."""
        var = tk.BooleanVar(value=config[key])
        cb = tk.Checkbutton(
            self.config_content,
            text=label,
            variable=var,
            bg='#ecf0f1',
            command=lambda: self._update_config(key, var.get())
        )
        cb.pack(anchor=tk.W, pady=2)
    
    def _update_config(self, key, value):
        """Actualizar configuración y refrescar vista previa."""
        self.config[self.current_mode][key] = value
        self._refresh_preview()
    
    def _refresh_preview(self):
        """Refrescar la vista previa."""
        try:
            # Obtener nodos del repositorio
            root_nodes = self.node_repository.find_roots()
            
            if not root_nodes:
                content = "📂 Proyecto vacío\n\n¡Crea tu primera carpeta o archivo!"
            else:
                # Generar contenido según el modo
                if self.current_mode == PreviewModes.CLASSIC:
                    content = self._generate_classic_view(root_nodes)
                elif self.current_mode == PreviewModes.ASCII_FULL:
                    content = self._generate_ascii_full_view(root_nodes)
                elif self.current_mode == PreviewModes.ASCII_FOLDERS:
                    content = self._generate_ascii_folders_view(root_nodes)
                elif self.current_mode == PreviewModes.COLUMNS:
                    content = self._generate_columns_view(root_nodes)
                else:
                    content = "❌ Modo no implementado"
            
            # Actualizar texto
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', content)
            self.preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', f"❌ Error generando vista previa:\n{str(e)}")
            self.preview_text.config(state=tk.DISABLED)
            print(f"❌ Error en vista previa: {e}")
    
    def _generate_classic_view(self, root_nodes):
        """Generar vista clásica."""
        config = self.config[PreviewModes.CLASSIC]
        lines = []
        
        for root in root_nodes:
            self._generate_classic_node(root, lines, 0, config)
        
        return '\n'.join(lines) if lines else "📂 Sin contenido"
    
    def _generate_classic_node(self, node, lines, depth, config):
        """Generar línea para un nodo en vista clásica."""
        if depth > config['max_depth']:
            return
        
        # Indentación
        indent = ' ' * (depth * config['indent_spaces'])
        
        # Icono
        icon = ""
        if config['show_icons']:
            icon = "📁 " if node.is_folder() else "📄 "
        
        # Estado
        status = ""
        if config['show_status'] and node.status.value:
            status = f" {node.status.value}"
        
        # Markdown
        markdown = ""
        if config['show_markdown'] and node.markdown_short:
            md_text = node.markdown_short.strip()
            if len(md_text) > config['markdown_max_length']:
                md_text = md_text[:config['markdown_max_length']] + "..."
            markdown = f" - {md_text}"
        
        # Línea completa
        line = f"{indent}{icon}{node.name}{status}{markdown}"
        lines.append(line)
        
        # Hijos recursivos
        if node.is_folder():
            children = self.node_repository.find_children(node.node_id)
            for child in children:
                self._generate_classic_node(child, lines, depth + 1, config)
    
    def _generate_ascii_full_view(self, root_nodes):
        """Generar vista ASCII completa."""
        config = self.config[PreviewModes.ASCII_FULL]
        lines = []
        
        for i, root in enumerate(root_nodes):
            is_last_root = (i == len(root_nodes) - 1)
            self._generate_ascii_node(root, lines, "", is_last_root, config)
        
        return '\n'.join(lines) if lines else "📂 Sin contenido"
    
    def _generate_ascii_node(self, node, lines, prefix, is_last, config):
        """Generar línea ASCII para un nodo."""
        # Caracteres ASCII
        if config['use_unicode']:
            branch = "├── " if not is_last else "└── "
            extend = "│   " if not is_last else "    "
        else:
            branch = "|-- " if not is_last else "`-- "
            extend = "|   " if not is_last else "    "
        
        # Icono
        icon = ""
        if config['show_icons']:
            icon = "📁 " if node.is_folder() else "📄 "
        
        # Estado
        status = ""
        if config['show_status'] and node.status.value:
            status = f" {node.status.value}"
        
        # Markdown
        markdown = ""
        if config['show_markdown'] and node.markdown_short:
            md_text = node.markdown_short.strip()
            if len(md_text) > config['markdown_max_length']:
                md_text = md_text[:config['markdown_max_length']] + "..."
            markdown = f" - {md_text}"
        
        # Línea
        line = f"{prefix}{branch}{icon}{node.name}{status}{markdown}"
        lines.append(line)
        
        # Hijos
        if node.is_folder():
            children = self.node_repository.find_children(node.node_id)
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                self._generate_ascii_node(child, lines, prefix + extend, is_last_child, config)
    
    def _generate_ascii_folders_view(self, root_nodes):
        """Generar vista ASCII solo carpetas."""
        config = self.config[PreviewModes.ASCII_FOLDERS]
        lines = []
        stats = {'total_files': 0, 'completed': 0, 'pending': 0, 'in_progress': 0}
        
        for i, root in enumerate(root_nodes):
            is_last_root = (i == len(root_nodes) - 1)
            self._generate_ascii_folders_node(root, lines, "", is_last_root, config, stats)
        
        # Estadísticas al final
        if config['show_status_summary']:
            lines.extend([
                "",
                "📊 ESTADÍSTICAS:",
                f"   Total archivos: {stats['total_files']}",
                f"   Completados: {stats['completed']} ✅",
                f"   En progreso: {stats['in_progress']} ⬜",
                f"   Pendientes: {stats['pending']} ❌"
            ])
        
        return '\n'.join(lines) if lines else "📂 Sin contenido"
    
    def _generate_ascii_folders_node(self, node, lines, prefix, is_last, config, stats):
        """Generar línea ASCII solo para carpetas."""
        if node.is_folder():
            # Contar archivos en esta carpeta
            children = self.node_repository.find_children(node.node_id)
            file_count = len([child for child in children if child.is_file()])
            
            # Actualizar estadísticas
            for child in children:
                if child.is_file():
                    stats['total_files'] += 1
                    if child.status.value == "✅":
                        stats['completed'] += 1
                    elif child.status.value == "⬜":
                        stats['in_progress'] += 1
                    elif child.status.value == "❌":
                        stats['pending'] += 1
            
            # Caracteres ASCII
            branch = "├── " if not is_last else "└── "
            extend = "│   " if not is_last else "    "
            
            # Icono
            icon = "📁 " if config['show_icons'] else ""
            
            # Contador de archivos
            count_info = ""
            if config['show_file_count'] and file_count > 0:
                count_info = f" ({file_count} archivos)"
            
            # Línea
            line = f"{prefix}{branch}{icon}{node.name}{count_info}"
            lines.append(line)
            
            # Hijos (solo carpetas)
            folders = [child for child in children if child.is_folder()]
            for i, child in enumerate(folders):
                is_last_child = (i == len(folders) - 1)
                self._generate_ascii_folders_node(child, lines, prefix + extend, is_last_child, config, stats)
    
    def _generate_columns_view(self, root_nodes):
        """Generar vista en columnas."""
        config = self.config[PreviewModes.COLUMNS]
        lines = []
        
        # Encabezados
        if config['show_headers']:
            path_header = "RUTA".ljust(config['col_path_width'])
            status_header = "ESTADO".ljust(config['col_status_width'])
            markdown_header = "DESCRIPCIÓN".ljust(config['col_markdown_width'])
            
            lines.append(f"{path_header} | {status_header} | {markdown_header}")
            lines.append("-" * (config['col_path_width'] + config['col_status_width'] + config['col_markdown_width'] + 6))
        
        # Nodos
        row_count = 0
        for root in root_nodes:
            self._generate_columns_node(root, lines, "", config, row_count)
            row_count += 1
        
        return '\n'.join(lines) if lines else "📂 Sin contenido"
    
    def _generate_columns_node(self, node, lines, path_prefix, config, row_count):
        """Generar línea en columnas para un nodo."""
        # Ruta completa
        full_path = f"{path_prefix}/{node.name}" if path_prefix else node.name
        icon = ("📁 " if node.is_folder() else "📄 ") if True else ""
        path_col = f"{icon}{full_path}"
        
        # Truncar si es muy largo
        if len(path_col) > config['col_path_width']:
            path_col = path_col[:config['col_path_width']-3] + "..."
        path_col = path_col.ljust(config['col_path_width'])
        
        # Estado
        status_col = node.status.value.ljust(config['col_status_width'])
        
        # Markdown
        markdown_text = node.markdown_short.strip() if node.markdown_short else ""
        if len(markdown_text) > config['markdown_max_length']:
            markdown_text = markdown_text[:config['markdown_max_length']] + "..."
        markdown_col = markdown_text.ljust(config['col_markdown_width'])
        
        # Línea
        line = f"{path_col} | {status_col} | {markdown_col}"
        lines.append(line)
        
        # Hijos
        if node.is_folder():
            children = self.node_repository.find_children(node.node_id)
            for child in children:
                self._generate_columns_node(child, lines, full_path, config, row_count + 1)
    
    def _export_txt(self):
        """Exportar vista previa a archivo TXT."""
        try:
            # Diálogo para guardar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Archivos de texto", "*.txt"),
                    ("Todos los archivos", "*.*")
                ],
                title="Exportar Vista Previa"
            )
            
            if filename:
                # Obtener contenido de la vista previa
                content = self.preview_text.get('1.0', tk.END).strip()
                
                # Crear encabezado profesional
                header = self._generate_export_header()
                
                # Contenido completo
                full_content = f"{header}\n\n{content}"
                
                # Guardar archivo
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                
                messagebox.showinfo("Exportación exitosa", f"Vista previa exportada a:\n{filename}")
                print(f"✅ Exportado: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error de exportación", f"Error al exportar:\n{str(e)}")
            print(f"❌ Error exportando: {e}")
    
    def _generate_export_header(self):
        """Generar encabezado profesional para exportación."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config_summary = self._get_config_summary()
        
        return f"""// ===========================================================================================
// TreeApp v4 Pro - Vista Previa del Proyecto
// ===========================================================================================
// 
// Fecha de exportación: {timestamp}
// Modo de visualización: {self.current_mode}
// 
// Configuración aplicada:
{config_summary}
// 
// ==========================================================================================="""
    
    def _get_config_summary(self):
        """Obtener resumen de configuración actual."""
        config = self.config[self.current_mode]
        lines = []
        
        for key, value in config.items():
            key_formatted = key.replace('_', ' ').title()
            lines.append(f"//   {key_formatted}: {value}")
        
        return '\n'.join(lines)
    
    def refresh(self):
        """Método público para refrescar la vista previa."""
        self._refresh_preview()