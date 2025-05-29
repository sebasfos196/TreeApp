# presentation/views/panels/tree_panel/tree_view.py
"""
Vista principal del explorador de árbol - refactorizada con responsabilidades separadas.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Callable, List
from domain.node.node_entity import Node, NodeType, NodeStatus
from application.commands.node.create_node_command import CreateNodeCommand
from application.commands.command_bus import get_command_bus


class FlatIcons:
    """Iconos flat modernos para el explorador - versión básica integrada."""
    
    FOLDER_CLOSED = "📁"
    FOLDER_OPEN = "📂" 
    FILE = "📄"
    
    FILE_TYPES = {
        '.py': '🐍', '.js': '📜', '.ts': '📜', '.html': '🌐', '.css': '🎨',
        '.md': '📝', '.json': '⚙️', '.txt': '📄', '.pdf': '📑', '.png': '🖼️',
        '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.zip': '📦', '.exe': '⚡',
        '.bat': '⚡', '.sh': '⚡', '.rs': '🦀', '.go': '🐹', '.java': '☕'
    }
    
    @classmethod
    def get_file_icon(cls, filename: str) -> str:
        """Obtener icono específico según extensión del archivo."""
        if not filename:
            return cls.FILE
        
        parts = filename.split('.')
        if len(parts) > 1:
            ext = '.' + parts[-1].lower()
            return cls.FILE_TYPES.get(ext, cls.FILE)
        
        return cls.FILE


class TreeView:
    """Vista principal del explorador de árbol - coordinadora de componentes."""
    
    def __init__(self, parent_frame, node_repository):
        self.parent_frame = parent_frame
        self.node_repository = node_repository
        self.command_bus = get_command_bus()
        
        # Estado básico
        self._selected_node_id: Optional[str] = None
        self._selection_callback: Optional[Callable] = None
        self._move_callback: Optional[Callable] = None
        
        # Variables para edición inline básica
        self.edit_entry = None
        self.editing_item = None
        self.editing_node = None
        
        # Configurar UI básica
        self._setup_ui()
        self._load_nodes()
    
    def _setup_ui(self):
        """Configurar interfaz básica del TreeView."""
        # Frame contenedor
        self.container = tk.Frame(self.parent_frame)
        self.container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Componentes UI
        self._setup_header()
        self._setup_toolbar()
        self._setup_treeview()
        self._setup_basic_events()
    
    def _setup_header(self):
        """Configurar encabezado moderno."""
        header_frame = tk.Frame(self.container, bg='#2c3e50', height=35)
        header_frame.pack(fill=tk.X, pady=(0, 8))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🌳 TreeCreator",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(expand=True)
    
    def _setup_toolbar(self):
        """Configurar barra de herramientas con iconos minimalistas."""
        toolbar_frame = tk.Frame(self.container, bg='#f8f9fa', height=35)
        toolbar_frame.pack(fill=tk.X, pady=(0, 8))
        toolbar_frame.pack_propagate(False)
        
        # Estilo de botones
        button_style = {
            'font': ('Arial', 16),
            'relief': tk.FLAT,
            'bd': 0,
            'width': 2,
            'height': 1,
            'cursor': 'hand2',
            'bg': '#f8f9fa',
            'activebackground': '#e9ecef'
        }
        
        # Botones principales
        self.btn_new_folder = self._create_toolbar_button(
            toolbar_frame, "📁", self._create_folder,
            fg='#3498db', tooltip="Nueva Carpeta (Ctrl+Shift+N)", side=tk.LEFT
        )
        
        self.btn_new_file = self._create_toolbar_button(
            toolbar_frame, "📄", self._create_file,
            fg='#27ae60', tooltip="Nuevo Archivo (Ctrl+N)", side=tk.LEFT
        )
        
        self.btn_refresh = self._create_toolbar_button(
            toolbar_frame, "🔄", self._load_nodes,
            fg='#f39c12', tooltip="Refrescar (F5)", side=tk.RIGHT
        )
        
        self.btn_delete = self._create_toolbar_button(
            toolbar_frame, "🗑️", self._delete_node,
            fg='#e74c3c', tooltip="Eliminar (Del)", side=tk.RIGHT
        )
    
    def _create_toolbar_button(self, parent, text, command, fg, tooltip, side):
        """Crear botón de toolbar con tooltip."""
        button = tk.Button(
            parent, text=text, command=command, fg=fg,
            font=('Arial', 16), relief=tk.FLAT, bd=0, width=2, height=1,
            cursor='hand2', bg='#f8f9fa', activebackground='#e9ecef'
        )
        button.pack(side=side, padx=2, pady=2)
        
        # Tooltip básico
        self._create_tooltip(button, tooltip)
        
        return button
    
    def _setup_treeview(self):
        """Configurar TreeView principal."""
        tree_frame = tk.Frame(self.container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # TreeView con columnas
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('status',),
            show='tree headings',
            height=15
        )
        
        # Configurar columnas y estilos
        self._configure_tree_columns_and_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _configure_tree_columns_and_styles(self):
        """Configurar columnas y estilos del TreeView."""
        # Encabezados
        self.tree.heading('#0', text='📁 Nombre', anchor='w')
        self.tree.heading('status', text='📊 Estado', anchor='center')
        
        # Columnas
        self.tree.column('#0', width=220, minwidth=150, anchor='w')
        self.tree.column('status', width=80, minwidth=60, anchor='center')
        
        # Estilos de filas
        self.tree.tag_configure('folder', foreground='#2c3e50', font=('Arial', 10, 'bold'))
        self.tree.tag_configure('file', foreground='#34495e', font=('Arial', 10))
        self.tree.tag_configure('completed', background='#d5f4e6')
        self.tree.tag_configure('pending', background='#fadbd8')
        self.tree.tag_configure('in_progress', background='#fdeaa7')
    
    def _setup_basic_events(self):
        """Configurar eventos básicos del TreeView."""
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
    
    def _create_tooltip(self, widget, text):
        """Crear tooltip con limpieza mejorada."""
        def on_enter(event):
            if hasattr(widget, 'tooltip') and widget.tooltip:
                try:
                    widget.tooltip.destroy()
                except:
                    pass
                widget.tooltip = None
            
            try:
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                label = tk.Label(tooltip, text=text, background="#333333", 
                               foreground="white", font=('Arial', 9), 
                               relief=tk.SOLID, borderwidth=1)
                label.pack()
                widget.tooltip = tooltip
            except Exception as e:
                print(f"❌ Error creando tooltip: {e}")
        
        def on_leave(event):
            if hasattr(widget, 'tooltip') and widget.tooltip:
                try:
                    widget.tooltip.destroy()
                except:
                    pass
                widget.tooltip = None
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    # ==================== CARGA Y DISPLAY DE NODOS ====================
    
    def _load_nodes(self):
        """Cargar nodos en el TreeView."""
        try:
            # Limpiar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener nodos raíz
            root_nodes = self.node_repository.find_roots()
            
            # Si no hay nodos, crear uno por defecto
            if not root_nodes:
                self._create_default_root()
                root_nodes = self.node_repository.find_roots()
            
            # Cargar nodos raíz
            for node in root_nodes:
                self._insert_node_recursive(node, '')
                
        except Exception as e:
            print(f"❌ Error cargando nodos: {e}")
            messagebox.showerror("Error", f"Error cargando proyecto:\n{str(e)}")
    
    def _create_default_root(self):
        """Crear nodo raíz por defecto."""
        try:
            command = CreateNodeCommand(
                name="Mi Proyecto",
                node_type=NodeType.FOLDER,
                markdown_short="# Mi Proyecto",
                explanation="Carpeta raíz del proyecto creada automáticamente",
                status=NodeStatus.IN_PROGRESS
            )
            self.command_bus.execute(command)
        except Exception as e:
            print(f"❌ Error creando nodo raíz por defecto: {e}")
    
    def _insert_node_recursive(self, node: Node, parent_id: str):
        """Insertar nodo y sus hijos recursivamente."""
        try:
            # Determinar icono y texto
            if node.is_folder():
                icon = FlatIcons.FOLDER_OPEN
            else:
                icon = FlatIcons.get_file_icon(node.name)
            
            display_name = f"{icon} {node.name}"
            
            # Determinar tags para estilo
            tags = self._get_node_tags(node)
            
            # Insertar nodo
            item_id = self.tree.insert(
                parent_id,
                'end',
                iid=node.node_id,
                text=display_name,
                values=(node.status.value,),
                open=node.is_folder(),
                tags=tags
            )
            
            # Insertar hijos si es carpeta
            if node.is_folder():
                children = self.node_repository.find_children(node.node_id)
                # Ordenar: carpetas primero, luego archivos
                children.sort(key=lambda x: (x.is_file(), x.name.lower()))
                
                for child in children:
                    self._insert_node_recursive(child, node.node_id)
                    
        except Exception as e:
            print(f"❌ Error insertando nodo {node.name}: {e}")
    
    def _get_node_tags(self, node: Node) -> List[str]:
        """Obtener tags de estilo para un nodo."""
        tags = []
        
        # Tag por tipo
        if node.is_folder():
            tags.append('folder')
        else:
            tags.append('file')
        
        # Tag por estado
        if node.status == NodeStatus.COMPLETED:
            tags.append('completed')
        elif node.status == NodeStatus.PENDING:
            tags.append('pending')
        elif node.status == NodeStatus.IN_PROGRESS:
            tags.append('in_progress')
        
        return tags
    
    # ==================== EVENTOS PRINCIPALES ====================
    
    def _on_select(self, event):
        """Manejar selección de nodo."""
        selection = self.tree.selection()
        if selection:
            self._selected_node_id = selection[0]
            print(f"🔍 Nodo seleccionado: {self._selected_node_id}")
            
            if self._selection_callback:
                self._selection_callback(self._selected_node_id)
        else:
            self._selected_node_id = None
            if self._selection_callback:
                self._selection_callback(None)
    
    def _on_double_click(self, event):
        """Manejar doble click - edición inline o expandir/contraer."""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        node = self.node_repository.find_by_id(item)
        if not node:
            return
        
        # Para carpetas: determinar si expandir o editar
        if node.is_folder():
            region = self.tree.identify_region(event.x, event.y)
            if region == "cell":
                # Edición inline básica
                self._start_inline_edit(item, node)
            else:
                # Expandir/contraer
                self._toggle_folder_state(item)
        else:
            # Para archivos: solo edición inline
            self._start_inline_edit(item, node)
    
    def _toggle_folder_state(self, item):
        """Alternar estado de apertura de una carpeta."""
        try:
            current_state = self.tree.item(item, 'open')
            self.tree.item(item, open=not current_state)
            
            # Actualizar icono
            node = self.node_repository.find_by_id(item)
            if node:
                new_icon = FlatIcons.FOLDER_OPEN if not current_state else FlatIcons.FOLDER_CLOSED
                current_text = self.tree.item(item, 'text')
                new_text = f"{new_icon}{current_text[1:]}"
                self.tree.item(item, text=new_text)
        except Exception as e:
            print(f"❌ Error alternando estado de carpeta: {e}")
    
    def _start_inline_edit(self, item, node):
        """Iniciar edición inline básica del nombre del nodo."""
        # Obtener posición del item
        bbox = self.tree.bbox(item, '#0')
        if not bbox:
            return
        
        try:
            # Crear Entry temporal para edición
            x, y, width, height = bbox
            
            # Ajustar para que no cubra el icono
            icon_width = 25
            x += icon_width
            width -= icon_width
            
            self.edit_entry = tk.Entry(
                self.tree,
                font=('Arial', 10),
                bg='#ffffff',
                fg='#2c3e50',
                relief=tk.SOLID,
                bd=1
            )
            
            # Posicionar Entry sobre el item
            self.edit_entry.place(x=x, y=y, width=width, height=height)
            
            # Configurar contenido inicial
            self.edit_entry.insert(0, node.name)
            self.edit_entry.select_range(0, tk.END)
            self.edit_entry.focus()
            
            # Guardar referencia al item y nodo
            self.editing_item = item
            self.editing_node = node
            
            # Eventos para finalizar edición
            self.edit_entry.bind('<Return>', self._finish_inline_edit)
            self.edit_entry.bind('<Escape>', self._cancel_inline_edit)
            self.edit_entry.bind('<FocusOut>', self._finish_inline_edit)
            
        except Exception as e:
            print(f"❌ Error iniciando edición inline: {e}")
    
    def _finish_inline_edit(self, event=None):
        """Finalizar edición inline y actualizar nodo."""
        if not hasattr(self, 'edit_entry') or not self.edit_entry:
            return
        
        try:
            new_name = self.edit_entry.get().strip()
            
            # Validar y actualizar si hay cambios
            if new_name and new_name != self.editing_node.name:
                if self._validate_inline_name(new_name):
                    # Actualizar nodo
                    old_name = self.editing_node.name
                    self.editing_node.name = new_name
                    self.editing_node.update_modified()
                    
                    # Guardar en repositorio
                    self.node_repository.save(self.editing_node)
                    
                    # Actualizar display en TreeView
                    self.update_node_display(self.editing_item, new_name)
                    
                    print(f"✏️ Renombrado inline: {old_name} → {new_name}")
            
            # Limpiar edición
            self._cleanup_inline_edit()
            
        except Exception as e:
            print(f"❌ Error finalizando edición inline: {e}")
            self._cleanup_inline_edit()
    
    def _cancel_inline_edit(self, event=None):
        """Cancelar edición inline."""
        self._cleanup_inline_edit()
    
    def _cleanup_inline_edit(self):
        """Limpiar componentes de edición inline."""
        try:
            if hasattr(self, 'edit_entry') and self.edit_entry:
                self.edit_entry.destroy()
                self.edit_entry = None
        except:
            pass
        
        if hasattr(self, 'editing_item'):
            self.editing_item = None
        
        if hasattr(self, 'editing_node'):
            self.editing_node = None
    
    def _validate_inline_name(self, name: str) -> bool:
        """Validar nombre para edición inline básica."""
        if not name:
            return False
        
        # Caracteres prohibidos básicos
        import re
        forbidden_chars = r'[<>:"/\\|?*]'
        if re.search(forbidden_chars, name):
            messagebox.showerror("Error", "El nombre contiene caracteres prohibidos")
            return False
        
        return True
    
    # ==================== OPERACIONES CRUD ====================
    
    def _create_folder(self):
        """Crear nueva carpeta."""
        parent_id = self._selected_node_id
        
        try:
            command = CreateNodeCommand(
                name="Nueva Carpeta",
                node_type=NodeType.FOLDER,
                parent_id=parent_id,
                markdown_short="# Nueva Carpeta",
                explanation="Carpeta creada desde TreeCreator"
            )
            
            result = self.command_bus.execute(command)
            if result.success:
                self._load_nodes()
                print(f"✅ Carpeta creada: {result.data.name}")
            else:
                messagebox.showerror("Error", f"Error creando carpeta:\n{result.error}")
                
        except Exception as e:
            print(f"❌ Error creando carpeta: {e}")
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")
    
    def _create_file(self):
        """Crear nuevo archivo."""
        parent_id = self._selected_node_id
        
        try:
            # Solicitar nombre del archivo
            name = simpledialog.askstring(
                "Nuevo Archivo",
                "Nombre del archivo (con extensión):",
                initialvalue="nuevo_archivo.txt"
            )
            
            if not name or not name.strip():
                return
            
            name = name.strip()
            
            # Generar código básico según extensión
            code_content = self._generate_basic_template(name)
            
            command = CreateNodeCommand(
                name=name,
                node_type=NodeType.FILE,
                parent_id=parent_id,
                markdown_short=f"# {name}",
                explanation=f"Archivo creado desde TreeCreator",
                code=code_content
            )
            
            result = self.command_bus.execute(command)
            if result.success:
                self._load_nodes()
                print(f"✅ Archivo creado: {result.data.name}")
            else:
                messagebox.showerror("Error", f"Error creando archivo:\n{result.error}")
                
        except Exception as e:
            print(f"❌ Error creando archivo: {e}")
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")
    
    def _generate_basic_template(self, filename: str) -> str:
        """Generar plantilla básica según extensión."""
        parts = filename.split('.')
        if len(parts) < 2:
            return f"# Contenido de {filename}\n"
        
        ext = parts[-1].lower()
        
        templates = {
            'py': f'#!/usr/bin/env python3\n"""{filename}"""\n\nprint("Hola desde {filename}")\n',
            'js': f'// {filename}\nconsole.log("Hola desde {filename}");\n',
            'html': f'<!DOCTYPE html>\n<html>\n<head><title>{filename}</title></head>\n<body>\n<h1>Hola desde {filename}</h1>\n</body>\n</html>\n',
            'md': f'# {filename.replace(".md", "").title()}\n\nContenido del documento.\n',
            'txt': f'Archivo: {filename}\n\nContenido del archivo de texto.\n'
        }
        
        return templates.get(ext, f"# Contenido de {filename}\n")
    
    def _delete_node(self):
        """Eliminar nodo seleccionado."""
        if not self._selected_node_id:
            messagebox.showwarning("Sin selección", "Selecciona un elemento para eliminar")
            return
        
        try:
            node = self.node_repository.find_by_id(self._selected_node_id)
            if not node:
                messagebox.showwarning("Error", "El elemento seleccionado ya no existe")
                return
            
            # Confirmar eliminación
            node_type = "carpeta" if node.is_folder() else "archivo"
            confirm = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Eliminar {node_type} '{node.name}'?\n\nEsta acción es permanente.",
                icon='warning'
            )
            
            if confirm:
                success = self.node_repository.delete(self._selected_node_id)
                if success:
                    self._load_nodes()
                    print(f"✅ Eliminado: {node.name}")
                else:
                    messagebox.showerror("Error", f"Error eliminando {node_type}")
                    
        except Exception as e:
            print(f"❌ Error eliminando nodo: {e}")
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")
    
    # ==================== MÉTODOS PÚBLICOS ====================
    
    def update_node_display(self, node_id: str, new_name: str) -> bool:
        """Actualizar display de un nodo específico."""
        try:
            if not self.tree.exists(node_id):
                print(f"❌ Nodo {node_id} no existe en TreeView")
                return False
            
            node = self.node_repository.find_by_id(node_id)
            if not node:
                print(f"❌ Nodo {node_id} no encontrado en repositorio")
                return False
            
            # Actualizar display
            if node.is_folder():
                is_open = self.tree.item(node_id, 'open')
                icon = FlatIcons.FOLDER_OPEN if is_open else FlatIcons.FOLDER_CLOSED
            else:
                icon = FlatIcons.get_file_icon(new_name)
            
            display_name = f"{icon} {new_name}"
            self.tree.item(node_id, text=display_name)
            
            print(f"🔄 TreeView actualizado: {new_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando display: {e}")
            return False
    
    def set_selection_callback(self, callback: Callable):
        """Establecer callback para selección de nodos."""
        self._selection_callback = callback
    
    def set_move_callback(self, callback: Callable):
        """Establecer callback para movimiento de nodos."""
        self._move_callback = callback
    
    def get_selected_node_id(self) -> Optional[str]:
        """Obtener ID del nodo seleccionado."""
        return self._selected_node_id
    
    def refresh(self):
        """Refrescar el árbol completo."""
        self._load_nodes()
    
    def get_tree_statistics(self) -> dict:
        """Obtener estadísticas básicas del árbol."""
        try:
            all_nodes = self.node_repository.find_all()
            stats = {
                'total_folders': 0,
                'total_files': 0,
                'completed': 0,
                'in_progress': 0,
                'pending': 0
            }
            
            for node in all_nodes:
                if node.is_folder():
                    stats['total_folders'] += 1
                else:
                    stats['total_files'] += 1
                
                if node.status == NodeStatus.COMPLETED:
                    stats['completed'] += 1
                elif node.status == NodeStatus.IN_PROGRESS:
                    stats['in_progress'] += 1
                elif node.status == NodeStatus.PENDING:
                    stats['pending'] += 1
            
            return stats
        except Exception as e:
            print(f"❌ Error calculando estadísticas: {e}")
            return {}