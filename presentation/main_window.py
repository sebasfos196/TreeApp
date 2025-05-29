# presentation/main_window.py
"""
Ventana principal de TreeApp v4 Pro.
Configura el layout de 3 paneles y coordina la UI.
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Agregar paths para imports absolutos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from application.commands.command_bus import get_command_bus
from infrastructure.persistence.json_repository import NodeRepository
from application.commands.node.create_node_command import CreateNodeCommandHandler, CreateNodeCommand


class MainWindow:
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TreeApp v4 Pro - Organizador Visual de Proyectos")
        self.root.geometry("1400x800")
        
        # Inicializar componentes
        self._setup_infrastructure()
        self._setup_layout()
        self._setup_panels()
        self._setup_events()
    
    def _setup_infrastructure(self):
        """Configurar infraestructura de la aplicación."""
        # Repositorio
        self.node_repository = NodeRepository()
        
        # Command bus y handlers
        self.command_bus = get_command_bus()
        self.command_bus.register_handler(
            CreateNodeCommand, 
            CreateNodeCommandHandler(self.node_repository)
        )
    
    def _setup_layout(self):
        """Configurar layout principal de 3 paneles."""
        # Panel principal con 3 columnas
        self.main_paned = tk.PanedWindow(
            self.root, 
            orient=tk.HORIZONTAL,
            sashwidth=4,
            relief=tk.RAISED
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame izquierdo - Explorador de árbol
        self.left_frame = tk.Frame(self.main_paned, bg='#f0f0f0', relief=tk.SUNKEN, bd=1)
        self.main_paned.add(self.left_frame, minsize=250)
        
        # Frame central - Editor (4 campos)
        self.center_frame = tk.Frame(self.main_paned, bg='#ffffff', relief=tk.SUNKEN, bd=1)
        self.main_paned.add(self.center_frame, minsize=400)
        
        # Frame derecho - Vista previa
        self.right_frame = tk.Frame(self.main_paned, bg='#f8f8f8', relief=tk.SUNKEN, bd=1)
        self.main_paned.add(self.right_frame, minsize=300)
    
    def _setup_panels(self):
        """Configurar los 3 paneles principales."""
        # Panel del árbol (izquierda)
        self._setup_tree_panel()
        
        # Panel del editor (centro)
        self._setup_editor_panel()
        
        # Panel de vista previa (derecha)
        self._setup_preview_panel()
    
    def _setup_tree_panel(self):
        """Configurar panel del explorador de árbol."""
        # Importar y crear TreeView
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        from presentation.views.panels.tree_panel.tree_view import TreeView
        
        # Crear TreeView real
        self.tree_view = TreeView(self.left_frame, self.node_repository)
    
    def _setup_editor_panel(self):
        """Configurar panel del editor (4 campos)."""
        # Importar y crear EditorContainer
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        from presentation.views.panels.editor_panel.editor_container import EditorContainer
        
        # Crear editor de documentación
        self.editor_container = EditorContainer(self.center_frame, self.node_repository)
        
        # Conectar selección del árbol con el editor
        self._connect_tree_to_editor()
    
    def _setup_preview_panel(self):
        """Configurar panel de vista previa."""
        # Título  
        title_label = tk.Label(
            self.right_frame,
            text="🔍 Vista Previa",
            font=('Arial', 12, 'bold'),
            bg='#f8f8f8'
        )
        title_label.pack(pady=5)
        
        # Placeholder para vista previa
        preview_label = tk.Label(
            self.right_frame,
            text="Vista Previa del Árbol\n4 Modos:\n- Clásico\n- ASCII\n- Solo Carpetas\n- Columnas\n(próximamente)",
            bg='#f8f8f8',
            justify=tk.LEFT
        )
        preview_label.pack(expand=True)
    
    def _setup_events(self):
        """Configurar eventos y bindings."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _connect_tree_to_editor(self):
        """Conectar selección del árbol con el editor."""
        def on_tree_select(selected_id):
            if selected_id:
                node = self.node_repository.find_by_id(selected_id)
                if node:
                    self.editor_container.load_node(node)
                else:
                    self.editor_container.clear_editor()
            else:
                self.editor_container.clear_editor()
        
        def on_name_update(node_id, new_name):
            """Callback para actualizar TreeView cuando cambie el nombre en el editor."""
            self.tree_view.update_node_display(node_id, new_name)
        
        # Establecer callbacks bidireccionales
        self.tree_view.set_selection_callback(on_tree_select)
        self.editor_container.set_tree_update_callback(on_name_update)
    
    def _on_closing(self):
        """Manejar cierre de la aplicación."""
        self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación."""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()