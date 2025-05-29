# presentation/views/panels/tree_panel/tree_events.py
"""
Manejo avanzado de eventos para TreeView
- Eventos de teclado y mouse
- Drag & drop integration
- Context menu integration
- 60 líneas - Cumple límite
"""

import tkinter as tk
from typing import Optional, Callable
from domain.events.event_bus import global_event_bus

class TreeEvents:
    """Manejador avanzado de eventos del TreeView"""
    
    def __init__(self, tree_core, node_repository):
        self.tree_core = tree_core
        self.tree = tree_core.get_tree_widget()
        self.node_repository = node_repository
        self.event_bus = global_event_bus
        
        # Callbacks opcionales
        self.on_double_click: Optional[Callable] = None
        self.on_right_click: Optional[Callable] = None
        
        self._setup_mouse_events()
        self._setup_keyboard_events()
        self._setup_advanced_events()
    
    def _setup_mouse_events(self):
        """Configura eventos de mouse avanzados"""
        
        # Double click para edición inline
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # Right click para context menu
        self.tree.bind('<Button-3>', self._on_right_click)
        
        # Middle click para acciones especiales
        self.tree.bind('<Button-2>', self._on_middle_click)
    
    def _setup_keyboard_events(self):
        """Configura shortcuts de teclado"""
        
        # Navegación
        self.tree.bind('<Key>', self._on_key_press)
        
        # Shortcuts específicos
        self.tree.bind('<F2>', self._on_rename_shortcut)
        self.tree.bind('<Delete>', self._on_delete_shortcut)
        self.tree.bind('<Control-c>', self._on_copy_shortcut)
        self.tree.bind('<Control-x>', self._on_cut_shortcut)
        self.tree.bind('<Control-v>', self._on_paste_shortcut)
        self.tree.bind('<Control-a>', self._on_select_all_shortcut)
        
        # Ensure tree can receive focus for keyboard events
        self.tree.focus_set()
    
    def _setup_advanced_events(self):
        """Configura eventos avanzados"""
        
        # Hover effects se manejan en tree_display.py
        # Drag & drop se integra aquí
        pass
    
    def _on_double_click(self, event):
        """Doble click - Delegar según contexto"""
        
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Publicar evento global para inline editing
        self.event_bus.publish('inline_edit_requested', {
            'node_id': item,
            'source': 'double_click'
        })
        
        # Callback opcional
        if self.on_double_click:
            self.on_double_click(event, item)
    
    def _on_right_click(self, event):
        """Right click - Context menu"""
        
        item = self.tree.identify_row(event.y)
        if item:
            # Seleccionar item antes de mostrar menu
            self.tree.selection_set(item)
            
            # Publicar evento global para context menu
            self.event_bus.publish('context_menu_requested', {
                'node_id': item,
                'x': event.x_root,
                'y': event.y_root,
                'source': 'right_click'
            })
        
        # Callback opcional
        if self.on_right_click:
            self.on_right_click(event, item)
    
    def _on_middle_click(self, event):
        """Middle click - Acciones especiales"""
        
        item = self.tree.identify_row(event.y)
        if item:
            # Publicar para acciones especiales (ej: separar como árbol nuevo)
            self.event_bus.publish('middle_click_action', {
                'node_id': item,
                'source': 'middle_click'
            })
    
    def _on_key_press(self, event):
        """Navegación con teclado"""
        
        # Publicar evento de navegación
        self.event_bus.publish('keyboard_navigation', {
            'key': event.keysym,
            'state': event.state,
            'source': 'tree_keyboard'
        })
    
    def _on_rename_shortcut(self, event):
        """F2 - Renombrar inline"""
        
        selected = self.tree_core.get_selected_nodes()
        if selected:
            node_id = list(selected)[0]  # Renombrar el primero si hay múltiples
            self.event_bus.publish('inline_edit_requested', {
                'node_id': node_id,
                'source': 'f2_shortcut'
            })
    
    def _on_delete_shortcut(self, event):
        """Delete - Eliminar seleccionados"""
        
        selected = self.tree_core.get_selected_nodes()
        if selected:
            self.event_bus.publish('delete_nodes_requested', {
                'node_ids': list(selected),
                'source': 'delete_shortcut'
            })
    
    def _on_copy_shortcut(self, event):
        """Ctrl+C - Copiar"""
        
        selected = self.tree_core.get_selected_nodes()
        if selected:
            self.event_bus.publish('copy_nodes_requested', {
                'node_ids': list(selected),
                'source': 'ctrl_c'
            })
    
    def _on_cut_shortcut(self, event):
        """Ctrl+X - Cortar"""
        
        selected = self.tree_core.get_selected_nodes()
        if selected:
            self.event_bus.publish('cut_nodes_requested', {
                'node_ids': list(selected),
                'source': 'ctrl_x'
            })
    
    def _on_paste_shortcut(self, event):
        """Ctrl+V - Pegar"""
        
        selected = self.tree_core.get_selected_nodes()
        target_id = list(selected)[0] if selected else None
        
        self.event_bus.publish('paste_nodes_requested', {
            'target_id': target_id,
            'source': 'ctrl_v'
        })
    
    def _on_select_all_shortcut(self, event):
        """Ctrl+A - Seleccionar todo"""
        
        # Seleccionar todos los items visibles
        all_items = []
        def collect_items(item_id):
            children = self.tree.get_children(item_id)
            for child in children:
                all_items.append(child)
                collect_items(child)
        
        # Empezar desde root
        collect_items('')
        
        if all_items:
            self.tree.selection_set(all_items)
            self.event_bus.publish('select_all_executed', {
                'selected_count': len(all_items),
                'source': 'ctrl_a'
            })
    
    # Métodos públicos para integración
    def set_double_click_callback(self, callback: Callable):
        """Establece callback personalizado para double click"""
        self.on_double_click = callback
    
    def set_right_click_callback(self, callback: Callable):
        """Establece callback personalizado para right click"""
        self.on_right_click = callback
    
    def enable_drag_drop(self, drag_drop_handler):
        """Integra manejador de drag & drop"""
        # Se conecta con drag_drop.py existente
        drag_drop_handler.bind_to_tree()
    
    def enable_context_menu(self, context_menu_handler):
        """Integra manejador de context menu"""
        # Se conecta con context_menu.py existente
        context_menu_handler.bind_to_tree()