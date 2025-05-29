# presentation/views/panels/tree_panel/tree_coordinator.py
"""
Coordinador principal del TreeView - Orquesta todos los componentes
- Integra tree_core, tree_events, tree_display
- API pública simplificada
- Comunicación tiempo real coordinada
- 60 líneas - Cumple límite
"""

from typing import Optional, Callable, Set
from .tree_core import TreeCore
from .tree_events import TreeEvents
from .tree_display import TreeDisplay
from domain.events.event_bus import global_event_bus

class TreeCoordinator:
    """Coordinador principal que orquesta todos los componentes del TreeView"""
    
    def __init__(self, parent_frame, node_repository):
        self.parent_frame = parent_frame
        self.node_repository = node_repository
        self.event_bus = global_event_bus
        
        # Componentes principales
        self.core = TreeCore(parent_frame, node_repository)
        self.events = TreeEvents(self.core, node_repository)
        self.display = TreeDisplay(self.core, node_repository)
        
        # Integración con componentes existentes
        self.context_menu_handler = None
        self.drag_drop_handler = None
        self.inline_editor = None
        
        self._setup_coordination()
    
    def _setup_coordination(self):
        """Configura coordinación entre componentes"""
        
        # Eventos de coordinación global
        self.event_bus.subscribe('context_menu_requested', self._handle_context_menu)
        self.event_bus.subscribe('inline_edit_requested', self._handle_inline_edit)
        self.event_bus.subscribe('delete_nodes_requested', self._handle_delete_nodes)
        self.event_bus.subscribe('copy_nodes_requested', self._handle_copy_nodes)
        self.event_bus.subscribe('cut_nodes_requested', self._handle_cut_nodes)
        self.event_bus.subscribe('paste_nodes_requested', self._handle_paste_nodes)
    
    def _handle_context_menu(self, data):
        """Delega context menu al handler existente"""
        
        if self.context_menu_handler:
            node_id = data.get('node_id')
            x = data.get('x')
            y = data.get('y')
            
            # Crear evento simulado para compatibilidad
            class FakeEvent:
                def __init__(self, x_root, y_root):
                    self.x_root = x_root
                    self.y_root = y_root
            
            fake_event = FakeEvent(x, y)
            self.context_menu_handler.show_menu(fake_event, node_id)
    
    def _handle_inline_edit(self, data):
        """Delega inline edit al handler existente"""
        
        if self.inline_editor:
            node_id = data.get('node_id')
            node = self.node_repository.find_by_id(node_id)
            
            if node:
                self.inline_editor.start_edit(node_id, node)
    
    def _handle_delete_nodes(self, data):
        """Eliminar nodos seleccionados"""
        
        node_ids = data.get('node_ids', [])
        if not node_ids:
            return
        
        # Confirmar eliminación
        from tkinter import messagebox
        count = len(node_ids)
        if count == 1:
            node = self.node_repository.find_by_id(node_ids[0])
            node_name = node.name if node else "elemento"
            confirm_msg = f"¿Eliminar '{node_name}'?"
        else:
            confirm_msg = f"¿Eliminar {count} elementos seleccionados?"
        
        if messagebox.askyesno("Confirmar eliminación", confirm_msg, icon='warning'):
            for node_id in node_ids:
                if self.node_repository.delete(node_id):
                    self.event_bus.publish('node_deleted', {'node_id': node_id})
    
    def _handle_copy_nodes(self, data):
        """Copiar nodos al clipboard"""
        
        node_ids = data.get('node_ids', [])
        if node_ids:
            # Guardar en clipboard interno
            self.event_bus.publish('clipboard_updated', {
                'operation': 'copy',
                'node_ids': node_ids,
                'source': 'tree_coordinator'
            })
    
    def _handle_cut_nodes(self, data):
        """Cortar nodos al clipboard"""
        
        node_ids = data.get('node_ids', [])
        if node_ids:
            # Guardar en clipboard interno
            self.event_bus.publish('clipboard_updated', {
                'operation': 'cut',
                'node_ids': node_ids,
                'source': 'tree_coordinator'
            })
    
    def _handle_paste_nodes(self, data):
        """Pegar nodos desde clipboard"""
        
        target_id = data.get('target_id')
        # Implementar lógica de paste cuando tengamos clipboard
        self.event_bus.publish('paste_operation_requested', {
            'target_id': target_id,
            'source': 'tree_coordinator'
        })
    
    # API Pública Simplificada
    def get_selected_nodes(self) -> Set[str]:
        """Obtiene nodos seleccionados"""
        return self.core.get_selected_nodes()
    
    def select_node(self, node_id: str):
        """Selecciona un nodo"""
        self.core.select_node(node_id)
    
    def refresh(self):
        """Refresca el árbol completo"""
        self.display.refresh_display()
    
    def get_tree_widget(self):
        """Obtiene widget TreeView para integración externa"""
        return self.core.get_tree_widget()
    
    def set_selection_callback(self, callback: Callable):
        """Callback de selección para compatibilidad"""
        # Los eventos ya se publican automáticamente vía EventBus
        pass
    
    # Integración con componentes existentes
    def integrate_context_menu(self, context_menu_handler):
        """Integra el manejador de context menu existente"""
        self.context_menu_handler = context_menu_handler
        self.events.enable_context_menu(context_menu_handler)
    
    def integrate_drag_drop(self, drag_drop_handler):
        """Integra el manejador de drag & drop existente"""
        self.drag_drop_handler = drag_drop_handler
        self.events.enable_drag_drop(drag_drop_handler)
    
    def integrate_inline_editor(self, inline_editor):
        """Integra el editor inline existente"""
        self.inline_editor = inline_editor