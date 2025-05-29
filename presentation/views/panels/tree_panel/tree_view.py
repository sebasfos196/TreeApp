# presentation/views/panels/tree_panel/tree_view.py
"""
Vista del explorador de árbol con TreeView y funcionalidad básica.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List
from domain.node.node_entity import Node, NodeType, NodeStatus
from application.commands.node.create_node_command import CreateNodeCommand
from application.commands.command_bus import get_command_bus


class TreeView:
    """Vista del explorador de árbol con TreeView."""
    
    def __init__(self, parent_frame, node_repository):
        self.parent_frame = parent_frame
        self.node_repository = node_repository
        self.command_bus = get_command_bus()
        self._selected_node_id: Optional[str] = None
        self._setup_ui()
        self._load_nodes()
    
    def _setup_ui(self):
        """Configurar interfaz del TreeView."""
        # Frame contenedor
        self.container = tk.Frame(self.parent_frame)
        self.container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título
        title_label = tk.Label(
            self.container,
            text="📁 Explorador de Proyecto",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Botones de acción
        self._setup_buttons()
        
        # TreeView con scrollbar
        self._setup_treeview()
        
        # Eventos
        self._setup_events()
    
    def _setup_buttons(self):
        """Configurar botones de acción."""
        button_frame = tk.Frame(self.container)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón crear carpeta
        self.btn_new_folder = tk.Button(
            button_frame,
            text="📁 Nueva Carpeta",
            command=self._create_folder,
            bg='#2196F3',
            fg='white',
            font=('Arial', 9, 'bold')
        )
        self.btn_new_folder.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón crear archivo
        self.btn_new_file = tk.Button(
            button_frame,
            text="📄 Nuevo Archivo",
            command=self._create_file,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 9, 'bold')
        )
        self.btn_new_file.pack(side=tk.LEFT, padx=5)
        
        # Botón eliminar
        self.btn_delete = tk.Button(
            button_frame,
            text="🗑️ Eliminar",
            command=self._delete_node,
            bg='#F44336',
            fg='white',
            font=('Arial', 9, 'bold')
        )
        self.btn_delete.pack(side=tk.RIGHT)
    
    def _setup_treeview(self):
        """Configurar TreeView principal."""
        # Frame para TreeView y scrollbar
        tree_frame = tk.Frame(self.container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # TreeView
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('status',),
            show='tree headings',
            height=15
        )
        
        # Configurar columnas
        self.tree.heading('#0', text='Nombre')
        self.tree.heading('status', text='Estado')
        self.tree.column('#0', width=200, minwidth=150)
        self.tree.column('status', width=80, minwidth=60, anchor='center')
        
        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _setup_events(self):
        """Configurar eventos del TreeView."""
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)
    
    def _load_nodes(self):
        """Cargar nodos en el TreeView."""
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
    
    def _create_default_root(self):
        """Crear nodo raíz por defecto."""
        command = CreateNodeCommand(
            name="Mi Proyecto",
            node_type=NodeType.FOLDER,
            markdown_short="# Mi Proyecto",
            explanation="Carpeta raíz del proyecto",
            status=NodeStatus.IN_PROGRESS
        )
        self.command_bus.execute(command)
    
    def _insert_node_recursive(self, node: Node, parent_id: str):
        """Insertar nodo y sus hijos recursivamente."""
        # Determinar icono y texto
        icon = "📁" if node.is_folder() else "📄"
        display_name = f"{icon} {node.name}"
        
        # Insertar nodo
        item_id = self.tree.insert(
            parent_id,
            'end',
            iid=node.node_id,
            text=display_name,
            values=(node.status.value,),
            open=node.is_folder()  # Abrir carpetas por defecto
        )
        
        # Insertar hijos
        if node.is_folder():
            children = self.node_repository.find_children(node.node_id)
            for child in children:
                self._insert_node_recursive(child, node.node_id)
    
    def _on_select(self, event):
        """Manejar selección de nodo."""
        selection = self.tree.selection()
        if selection:
            self._selected_node_id = selection[0]
            print(f"🔍 Nodo seleccionado: {self._selected_node_id}")
            
            # Notificar callback externo si existe
            if hasattr(self, '_selection_callback') and self._selection_callback:
                self._selection_callback(self._selected_node_id)
        else:
            self._selected_node_id = None
            if hasattr(self, '_selection_callback') and self._selection_callback:
                self._selection_callback(None)
    
    def set_selection_callback(self, callback):
        """Establecer callback para cuando se selecciona un nodo."""
        self._selection_callback = callback
    
    def _on_double_click(self, event):
        """Manejar doble click."""
        item = self.tree.identify_row(event.y)
        if item:
            # Expandir/contraer si es carpeta
            if self.tree.item(item, 'open'):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)
    
    def _on_right_click(self, event):
        """Manejar click derecho (menú contextual)."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self._selected_node_id = item
            print(f"🖱️ Click derecho en: {item}")
            # TODO: Mostrar menú contextual
    
    def _create_folder(self):
        """Crear nueva carpeta."""
        parent_id = self._selected_node_id
        
        command = CreateNodeCommand(
            name="Nueva Carpeta",
            node_type=NodeType.FOLDER,
            parent_id=parent_id,
            markdown_short="# Nueva Carpeta",
            explanation="Carpeta creada desde el explorador"
        )
        
        result = self.command_bus.execute(command)
        if result.success:
            self._load_nodes()  # Recargar árbol
            print(f"✅ Carpeta creada: {result.data.name}")
        else:
            print(f"❌ Error creando carpeta: {result.error}")
    
    def _create_file(self):
        """Crear nuevo archivo."""
        parent_id = self._selected_node_id
        
        command = CreateNodeCommand(
            name="nuevo_archivo.md",
            node_type=NodeType.FILE,
            parent_id=parent_id,
            markdown_short="# Nuevo Archivo",
            explanation="Archivo creado desde el explorador",
            code="# Contenido del archivo\nprint('Hola TreeApp!')"
        )
        
        result = self.command_bus.execute(command)
        if result.success:
            self._load_nodes()  # Recargar árbol
            print(f"✅ Archivo creado: {result.data.name}")
        else:
            print(f"❌ Error creando archivo: {result.error}")
    
    def _delete_node(self):
        """Eliminar nodo seleccionado."""
        if self._selected_node_id:
            # Confirmar eliminación
            node = self.node_repository.find_by_id(self._selected_node_id)
            if node:
                confirm = tk.messagebox.askyesno(
                    "Confirmar eliminación",
                    f"¿Eliminar '{node.name}'?"
                )
                if confirm:
                    success = self.node_repository.delete(self._selected_node_id)
                    if success:
                        self._load_nodes()  # Recargar árbol
                        print(f"✅ Eliminado: {node.name}")
                    else:
                        print(f"❌ Error eliminando: {node.name}")
        else:
            print("❌ No hay nodo seleccionado para eliminar")
    
    # ==================== MÉTODO FALTANTE: ACTUALIZACIÓN EN TIEMPO REAL ====================
    
    def update_node_display(self, node_id: str, new_name: str):
        """Actualizar el nombre del nodo en el TreeView sin recargar todo."""
        try:
            # Verificar que el nodo existe en el TreeView
            if self.tree.exists(node_id):
                # Obtener el nodo del repositorio para obtener su tipo
                node = self.node_repository.find_by_id(node_id)
                if node:
                    # Determinar icono según el tipo
                    icon = "📁" if node.is_folder() else "📄"
                    display_name = f"{icon} {new_name}"
                    
                    # Actualizar el texto en el TreeView
                    self.tree.item(node_id, text=display_name)
                    
                    print(f"🔄 TreeView actualizado: {node.name} → {new_name}")
                else:
                    print(f"❌ Nodo {node_id} no encontrado en repositorio")
            else:
                print(f"❌ Nodo {node_id} no existe en TreeView")
        except Exception as e:
            print(f"❌ Error actualizando TreeView: {e}")
    
    def get_selected_node_id(self) -> Optional[str]:
        """Obtener ID del nodo seleccionado."""
        return self._selected_node_id
    
    def refresh(self):
        """Refrescar el árbol."""
        self._load_nodes()