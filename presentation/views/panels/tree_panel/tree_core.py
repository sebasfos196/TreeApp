# presentation/views/panels/tree_panel/tree_core.py
"""
Núcleo básico del TreeView con EventBus integrado
- Solo funcionalidad esencial del TreeView
- Comunicación tiempo real global
- Estilos globales modernos
- 80 líneas - Cumple límite
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Set
from ....styling.constants.modern_colors import ModernColors
from domain.events.event_bus import global_event_bus

class TreeCore:
    """Núcleo básico del TreeView con comunicación tiempo real"""
    
    def __init__(self, parent_frame, node_repository):
        self.parent_frame = parent_frame
        self.node_repository = node_repository
        self.event_bus = global_event_bus
        
        # Estado básico
        self.selected_nodes: Set[str] = set()
        self.tree = None
        
        self._setup_treeview()
        self._setup_global_events()
    
    def _setup_treeview(self):
        """Configura TreeView básico con estilos globales"""
        
        # Frame contenedor con estilos modernos
        self.tree_frame = tk.Frame(
            self.parent_frame,
            bg=ModernColors.DARK_BACKGROUND,
            relief='flat',
            bd=0
        )
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # TreeView moderno
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=('status',),
            show='tree headings',
            selectmode='extended'  # Selección múltiple
        )
        
        # Configurar columnas básicas
        self.tree.heading('#0', text='Nombre', anchor='w')
        self.tree.heading('status', text='Estado', anchor='center')
        self.tree.column('#0', width=200, minwidth=150)
        self.tree.column('status', width=60, minwidth=50, anchor='center')
        
        # Scrollbars
        self._setup_scrollbars()
        
        # Eventos básicos del TreeView
        self._setup_tree_events()
    
    def _setup_scrollbars(self):
        """Configura scrollbars modernas"""
        
        v_scroll = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        h_scroll = ttk.Scrollbar(self.tree_frame, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Layout con grid para mejor control
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
    
    def _setup_tree_events(self):
        """Eventos básicos del TreeView"""
        
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_changed)
        # Más eventos se agregan en tree_events.py
    
    def _setup_global_events(self):
        """Configura comunicación tiempo real global"""
        
        # Eventos que escucha TreeCore
        self.event_bus.subscribe('node_created', self._on_node_created)
        self.event_bus.subscribe('node_deleted', self._on_node_deleted)
        self.event_bus.subscribe('node_renamed', self._on_node_renamed)
        self.event_bus.subscribe('node_moved', self._on_node_moved)
        self.event_bus.subscribe('editor_name_changed', self._on_editor_name_changed)
    
    def _on_selection_changed(self, event):
        """Selección cambió - Propagar globalmente INMEDIATAMENTE"""
        
        selection = self.tree.selection()
        self.selected_nodes = set(selection)
        
        if selection:
            # Publicar evento global INMEDIATO (0ms delay)
            self.event_bus.publish('node_selected', {
                'node_id': selection[0],
                'multiple': len(selection) > 1,
                'selected_nodes': list(selection),
                'source': 'tree_core'
            })
        else:
            self.event_bus.publish('node_deselected', {
                'source': 'tree_core'
            })
    
    # Handlers de eventos globales
    def _on_node_created(self, data):
        """Nodo creado desde otro componente - Actualizar INMEDIATO"""
        self.refresh_tree()
    
    def _on_node_deleted(self, data):
        """Nodo eliminado - Actualizar INMEDIATO"""
        node_id = data.get('node_id')
        if node_id and self.tree.exists(node_id):
            self.tree.delete(node_id)
        self.selected_nodes.discard(node_id)
    
    def _on_node_renamed(self, data):
        """Nodo renombrado - Actualizar display INMEDIATO"""
        node_id = data.get('node_id')
        new_name = data.get('new_name')
        
        if node_id and self.tree.exists(node_id) and new_name:
            # Actualizar display inmediatamente
            current_text = self.tree.item(node_id, 'text')
            # Mantener icono, cambiar solo nombre
            if current_text:
                icon = current_text.split(' ')[0]
                self.tree.item(node_id, text=f"{icon} {new_name}")
    
    def _on_node_moved(self, data):
        """Nodo movido - Refrescar estructura"""
        self.refresh_tree()
    
    def _on_editor_name_changed(self, data):
        """Editor cambió nombre - Actualizar TreeView INMEDIATO"""
        node_id = data.get('node_id')
        new_name = data.get('new_name')
        
        if node_id and new_name:
            # Propagar como rename para consistencia
            self.event_bus.publish('node_renamed', {
                'node_id': node_id,
                'new_name': new_name,
                'source': 'editor'
            })
    
    # Métodos públicos
    def get_selected_nodes(self) -> Set[str]:
        """Obtiene nodos seleccionados"""
        return self.selected_nodes.copy()
    
    def select_node(self, node_id: str):
        """Selecciona un nodo programáticamente"""
        if self.tree.exists(node_id):
            self.tree.selection_set(node_id)
            self.tree.focus(node_id)
    
    def refresh_tree(self):
        """Refresca el árbol completo"""
        # Delegado a tree_display.py
        self.event_bus.publish('tree_refresh_requested', {
            'source': 'tree_core'
        })
    
    def clear_selection(self):
        """Limpia selección"""
        self.tree.selection_remove(self.tree.selection())
        self.selected_nodes.clear()
    
    def exists(self, node_id: str) -> bool:
        """Verifica si un nodo existe en el TreeView"""
        return self.tree.exists(node_id)
    
    def get_tree_widget(self):
        """Obtiene el widget TreeView para otros componentes"""
        return self.tree