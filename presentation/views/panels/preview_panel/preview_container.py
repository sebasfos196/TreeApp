# presentation/views/panels/preview_panel/preview_container.py
"""
Contenedor principal del panel de vista previa - refactorizado con renderers separados.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Optional
from datetime import datetime

# Imports de renderers especializados
from .renderers.classic_renderer import ClassicRenderer
from .renderers.ascii_renderer import AsciiRenderer
from .renderers.folders_renderer import FoldersRenderer
from .renderers.columns_renderer import ColumnsRenderer


class PreviewModes:
    """Constantes para los modos de vista previa."""
    CLASSIC = "Clásico"
    ASCII_FULL = "ASCII Completo"
    ASCII_FOLDERS = "ASCII Solo Carpetas"
    COLUMNS = "Columnas"


class PreviewContainer:
    """Contenedor principal del panel de vista previa con renderers especializados."""
    
    def __init__(self, parent_frame, node_repository):
        self.parent_frame = parent_frame
        self.node_repository = node_repository
        self.current_mode = PreviewModes.CLASSIC
        
        # Configuraciones por modo
        self.config = self._initialize_default_config()
        
        # Renderers especializados
        self.renderers = {
            PreviewModes.CLASSIC: ClassicRenderer(node_repository),
            PreviewModes.ASCII_FULL: AsciiRenderer(node_repository),
            PreviewModes.ASCII_FOLDERS: FoldersRenderer(node_repository),
            PreviewModes.COLUMNS: ColumnsRenderer(node_repository)
        }
        
        self._setup_ui()
        self._refresh_preview()
    
    def _initialize_default_config(self) -> Dict[str, Dict]:
        """Inicializar configuraciones por defecto para cada modo."""
        return {
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
                'markdown_max_length': 40,
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
    
    def _setup_ui(self):
        """Configurar interfaz del panel de vista previa."""
        # Frame principal
        self.main_frame = tk.Frame(self.parent_frame, bg='#f8f8f8')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Componentes UI
        self._setup_header()
        self._setup_preview_area()
        self._setup_config_panel()
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
        
        # Controles de modo
        self._setup_mode_controls(header_frame)
    
    def _setup_mode_controls(self, parent):
        """Configurar controles de selección de modo."""
        mode_frame = tk.Frame(parent, bg='#f8f8f8')
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
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.config_btn.pack(side=tk.LEFT)
    
    def _setup_preview_area(self):
        """Configurar área principal de vista previa."""
        preview_frame = tk.Frame(self.main_frame, bg='#ffffff', relief=tk.SUNKEN, bd=1)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Text widget para mostrar la vista previa - HABILITADO PARA COPIA
        text_frame = tk.Frame(preview_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(
            text_frame,
            font=('Consolas', 10),
            bg='#ffffff',
            fg='#2c3e50',
            wrap=tk.NONE,
            state=tk.NORMAL,  # Habilitado para selección
            relief=tk.FLAT,
            bd=5,
            padx=10,
            pady=10,
            selectbackground='#3498db',
            selectforeground='white',
            cursor='text'
        )
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.preview_text.yview)
        h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_text.xview)
        
        self.preview_text.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Layout
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Eventos y menú contextual
        self._setup_preview_events()
    
    def _setup_preview_events(self):
        """Configurar eventos de la vista previa."""
        # Ctrl+A para seleccionar todo
        self.preview_text.bind('<Control-a>', self._select_all_text)
        
        # Menú contextual
        self.preview_context_menu = tk.Menu(self.preview_text, tearoff=0)
        self.preview_context_menu.add_command(
            label="📋 Copiar", 
            command=self._copy_selected_text, 
            accelerator="Ctrl+C"
        )
        self.preview_context_menu.add_command(
            label="📋 Copiar Todo", 
            command=self._copy_all_text, 
            accelerator="Ctrl+A"
        )
        self.preview_context_menu.add_separator()
        self.preview_context_menu.add_command(
            label="🔄 Refrescar", 
            command=self._refresh_preview
        )
        
        def show_context_menu(event):
            try:
                self.preview_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.preview_context_menu.grab_release()
        
        self.preview_text.bind('<Button-3>', show_context_menu)
    
    def _setup_config_panel(self):
        """Configurar panel de configuración (inicialmente oculto)."""
        self.config_frame = tk.Frame(self.main_frame, bg='#ecf0f1', relief=tk.RAISED, bd=1)
        self.config_visible = False
        
        # Título del panel
        config_header = tk.Frame(self.config_frame, bg='#bdc3c7')
        config_header.pack(fill=tk.X)
        
        tk.Label(
            config_header,
            text="⚙️ Configuración",
            font=('Arial', 11, 'bold'),
            bg='#bdc3c7',
            fg='#2c3e50'
        ).pack(pady=5)
        
        # Contenido dinámico
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
            pady=5,
            cursor='hand2'
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
            pady=5,
            cursor='hand2'
        ).pack(side=tk.RIGHT)
    
    # ==================== EVENTOS PRINCIPALES ====================
    
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
            self.config_frame.pack(fill=tk.X, padx=5, pady=(0, 5), 
                                 before=self.preview_text.master.master)
            self.config_visible = True
            self.config_btn.config(text="❌")
            self._update_config_panel()
    
    def _update_config_panel(self):
        """Actualizar contenido del panel de configuración."""
        # Limpiar contenido anterior
        for widget in self.config_content.winfo_children():
            widget.destroy()
        
        current_config = self.config[self.current_mode]
        
        # Crear controles específicos por modo
        if self.current_mode == PreviewModes.CLASSIC:
            self._create_classic_config(current_config)
        elif self.current_mode == PreviewModes.ASCII_FULL:
            self._create_ascii_full_config(current_config)
        elif self.current_mode == PreviewModes.ASCII_FOLDERS:
            self._create_ascii_folders_config(current_config)
        elif self.current_mode == PreviewModes.COLUMNS:
            self._create_columns_config(current_config)
    
    # ==================== CONFIGURACIONES POR MODO ====================
    
    def _create_classic_config(self, config):
        """Crear configuración para modo Clásico."""
        self._create_spinbox_config(config, 'indent_spaces', "Espacios de indentación:", 1, 8)
        self._create_checkbox_config(config, 'show_icons', "Mostrar iconos")
        self._create_checkbox_config(config, 'show_status', "Mostrar estados")
        self._create_checkbox_config(config, 'show_markdown', "Mostrar markdown")
        
        if config.get('show_markdown'):
            self._create_spinbox_config(config, 'markdown_max_length', "Longitud máx. markdown:", 20, 100)
    
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
    
    def _create_columns_config(self, config):
        """Crear configuración para modo Columnas."""
        self._create_spinbox_config(config, 'col_path_width', "Ancho columna Ruta:", 50, 500)
        self._create_spinbox_config(config, 'col_status_width', "Ancho columna Estado:", 50, 200)
        self._create_spinbox_config(config, 'col_markdown_width', "Ancho columna Markdown:", 50, 500)
        self._create_checkbox_config(config, 'show_headers', "Mostrar encabezados")
    
    def _create_spinbox_config(self, config, key, label, min_val, max_val):
        """Crear control Spinbox para configuración."""
        frame = tk.Frame(self.config_content, bg='#ecf0f1')
        frame.pack(fill=tk.X, pady=2)
        
        tk.Label(frame, text=label, bg='#ecf0f1').pack(side=tk.LEFT)
        
        var = tk.IntVar(value=config[key])
        spinbox = tk.Spinbox(frame, from_=min_val, to=max_val, textvariable=var, width=5)
        spinbox.pack(side=tk.RIGHT)
        var.trace('w', lambda *args: self._update_config(key, var.get()))
    
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
    
    # ==================== RENDERIZADO ====================
    
    def _refresh_preview(self):
        """Refrescar la vista previa usando renderer apropiado."""
        try:
            # Obtener nodos del repositorio
            root_nodes = self.node_repository.find_roots()
            
            if not root_nodes:
                content = "📂 Proyecto vacío\n\n¡Crea tu primera carpeta o archivo!"
            else:
                # Usar renderer especializado
                renderer = self.renderers.get(self.current_mode)
                if renderer:
                    current_config = self.config[self.current_mode]
                    content = renderer.render(root_nodes, current_config)
                else:
                    content = "❌ Renderer no encontrado"
            
            # Actualizar texto (mantener seleccionable)
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', content)
            
        except Exception as e:
            error_msg = f"❌ Error generando vista previa:\n{str(e)}\n\nDetalle: {type(e).__name__}"
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', error_msg)
            print(f"❌ Error en vista previa: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== FUNCIONES DE COPIA ====================
    
    def _select_all_text(self, event=None):
        """Seleccionar todo el texto."""
        self.preview_text.tag_add(tk.SEL, "1.0", tk.END)
        return 'break'
    
    def _copy_selected_text(self):
        """Copiar texto seleccionado."""
        try:
            selected = self.preview_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected:
                self.preview_text.clipboard_clear()
                self.preview_text.clipboard_append(selected)
                print("📋 Texto seleccionado copiado")
        except tk.TclError:
            self._copy_all_text()
    
    def _copy_all_text(self):
        """Copiar todo el texto."""
        all_text = self.preview_text.get('1.0', tk.END).strip()
        if all_text:
            self.preview_text.clipboard_clear()
            self.preview_text.clipboard_append(all_text)
            print("📋 Todo el texto copiado")
    
    # ==================== EXPORTACIÓN ====================
    
    def _export_txt(self):
        """Exportar vista previa a archivo TXT."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Archivos de texto", "*.txt"),
                    ("Todos los archivos", "*.*")
                ],
                title="Exportar Vista Previa"
            )
            
            if filename:
                content = self.preview_text.get('1.0', tk.END).strip()
                header = self._generate_export_header()
                full_content = f"{header}\n\n{content}"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                
                messagebox.showinfo("Exportación exitosa", f"Vista previa exportada a:\n{filename}")
                print(f"✅ Exportado: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error de exportación", f"Error al exportar:\n{str(e)}")
            print(f"❌ Error exportando: {e}")
    
    def _generate_export_header(self) -> str:
        """Generar encabezado profesional para exportación."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config_summary = self._get_config_summary()
        
        return f"""// ===========================================================================================
// TreeCreator - Vista Previa del Proyecto
// ===========================================================================================
// 
// Fecha de exportación: {timestamp}
// Modo de visualización: {self.current_mode}
// 
// Configuración aplicada:
{config_summary}
// 
// ==========================================================================================="""
    
    def _get_config_summary(self) -> str:
        """Obtener resumen de configuración actual."""
        config = self.config[self.current_mode]
        lines = []
        
        for key, value in config.items():
            key_formatted = key.replace('_', ' ').title()
            lines.append(f"//   {key_formatted}: {value}")
        
        return '\n'.join(lines)
    
    # ==================== MÉTODO PÚBLICO ====================
    
    def refresh(self):
        """Método público para refrescar la vista previa."""
        self._refresh_preview()