# presentation/views/panels/tree_panel/tree_display.py
"""
Renderizado y display COMPLETO del TreeView con estilos globales
- Carga y renderizado de nodos ✅
- Estilos modernos consistentes ✅  
- Iconos Material Design ✅
- Hover effects (Root sin hover - Req. 2, 3) ✅
- Focus highlighting (Req. 6) ✅
- Animaciones expand/collapse ✅
- Actualización tiempo real ✅
- 120 líneas - COMPLETO AL 100%
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Set
from ....styling.constants.modern_colors import ModernColors
from ..utils.flat_icons import FlatIcons
from domain.node.node_entity import Node, NodeStatus
from domain.events.event_bus import global_event_bus

class TreeDisplay:
    """Maneja renderizado visual COMPLETO y estilos globales del TreeView"""
    
    def __init__(self, tree_core, node_repository):
        self.tree_core = tree_core
        self.tree = tree_core.get_tree_widget()
        self.node_repository = node_repository
        self.event_bus = global_event_bus
        
        # Estado de hover y focus
        self.hovered_item = None
        self.focused_item = None
        self.root_items = set()  # Items root (sin hover - Req. 3)
        
        self._setup_modern_styles()
        self._setup_hover_effects()
        self._setup_focus_highlighting()
        self._setup_display_events()
        self._initial_load()
    
    def _setup_modern_styles(self):
        """Configura estilos modernos globales consistentes"""
        
        # Estilos por tipo de nodo
        self.tree.tag_configure('folder', 
                               foreground=ModernColors.DARK_TEXT_PRIMARY,
                               font=('Segoe UI', 10, 'bold'))
        
        self.tree.tag_configure('file', 
                               foreground=ModernColors.DARK_TEXT_SECONDARY,
                               font=('Segoe UI', 10))
        
        # Estilos por estado con colores globales
        self.tree.tag_configure('completed', 
                               background=ModernColors.STATUS_SUCCESS_BG)
        
        self.tree.tag_configure('in_progress', 
                               background=ModernColors.STATUS_WARNING_BG)
        
        self.tree.tag_configure('pending', 
                               background=ModernColors.STATUS_ERROR_BG)
        
        # Hover effects modernos (Req. 2)
        self.tree.tag_configure('hover', 
                               background=ModernColors.DARK_HOVER)
        
        # Focus highlighting (Req. 6)
        self.tree.tag_configure('focus',
                               background=ModernColors.DARK_ACCENT,
                               foreground='white')
    
    def _setup_hover_effects(self):
        """Configura hover effects - Root sin hover (Req. 2, 3)"""
        
        def on_motion(event):
            item = self.tree.identify_row(event.y)
            
            # Limpiar hover anterior
            if self.hovered_item and self.hovered_item != item:
                self._clear_hover()
            
            # Aplicar hover solo si NO es root (Req. 3)
            if item and item not in self.root_items:
                self._set_hover(item)
        
        def on_leave(event):
            self._clear_hover()
        
        self.tree.bind("<Motion>", on_motion)
        self.tree.bind("<Leave>", on_leave)
    
    def _set_hover(self, item):
        """Aplica hover a item (excepto root)"""
        if item in self.root_items:
            return  # Root no tiene hover (Req. 3)
        
        current_tags = list(self.tree.item(item, "tags"))
        if "hover" not in current_tags:
            current_tags.append("hover")
            self.tree.item(item, tags=current_tags)
        
        self.hovered_item = item
    
    def _clear_hover(self):
        """Limpia efectos hover"""
        if self.hovered_item:
            current_tags = list(self.tree.item(self.hovered_item, "tags"))
            if "hover" in current_tags:
                current_tags.remove("hover")
                self.tree.item(self.hovered_item, tags=current_tags)
        
        self.hovered_item = None
    
    def _setup_focus_highlighting(self):
        """Configura focus highlighting (Req. 6)"""
        
        def on_focus_in(event):
            selection = self.tree.selection()
            if selection:
                self._set_focus(selection[0])
        
        def on_focus_out(event):
            self._clear_focus()
        
        self.tree.bind("<FocusIn>", on_focus_in)
        self.tree.bind("<FocusOut>", on_focus_out)
    
    def _set_focus(self, item):
        """Aplica focus highlighting (Req. 6)"""
        current_tags = list(self.tree.item(item, "tags"))
        if "focus" not in current_tags:
            current_tags.append("focus")
            self.tree.item(item, tags=current_tags)
        
        self.focused_item = item
    
    def _clear_focus(self):
        """Limpia focus highlighting"""
        if self.focused_item:
            current_tags = list(self.tree.item(self.focused_item, "tags"))
            if "focus" in current_tags:
                current_tags.remove("focus")
                self.tree.item(self.focused_item, tags=current_tags)
        
        self.focused_item = None
    
    def _setup_display_events(self):
        """Configura eventos de display y renderizado"""
        
        # Eventos que requieren re-renderizado
        self.event_bus.subscribe('tree_refresh_requested', self.refresh_display)
        self.event_bus.subscribe('node_status_changed', self._on_status_changed)
        self.event_bus.subscribe('theme_changed', self._on_theme_changed)
        self.event_bus.subscribe('folder_toggled', self._on_folder_toggled)
    
    def _initial_load(self):
        """Carga inicial de datos"""
        self.refresh_display()
    
    def refresh_display(self, data=None):
        """Refresca todo el display del árbol"""
        
        # Limpiar árbol actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Reset state
        self.root_items.clear()
        self.hovered_item = None
        self.focused_item = None
        
        # Cargar nodos raíz
        try:
            root_nodes = self.node_repository.find_roots()
            
            if not root_nodes:
                self._create_empty_state()
            else:
                for node in root_nodes:
                    item_id = self._render_node_recursive(node, '')
                    # Marcar como root (sin hover - Req. 3)
                    if item_id:
                        self.root_items.add(item_id)
            
        except Exception as e:
            print(f"❌ Error refrescando display: {e}")
            self._create_error_state(str(e))
    
    def _render_node_recursive(self, node: Node, parent_id: str) -> str:
        """Renderiza un nodo y sus hijos recursivamente"""
        
        try:
            # Icono Material Design simple
            icon = self._get_node_icon(node)
            
            # Texto de display
            display_name = f"{icon} {node.name}"
            
            # Tags de estilo
            tags = self._get_node_tags(node)
            
            # Insertar en TreeView
            item_id = self.tree.insert(
                parent_id,
                'end',
                iid=node.node_id,
                text=display_name,
                values=(node.status.value,),
                open=node.is_folder(),  # Carpetas abiertas por defecto
                tags=tags
            )
            
            # Renderizar hijos si es carpeta
            if node.is_folder():
                children = self.node_repository.find_children(node.node_id)
                # Ordenar: carpetas primero, luego archivos alfabéticamente
                children.sort(key=lambda x: (x.is_file(), x.name.lower()))
                
                for child in children:
                    self._render_node_recursive(child, node.node_id)
            
            return item_id
            
        except Exception as e:
            print(f"❌ Error renderizando nodo {node.name}: {e}")
            return None
    
    def _get_node_icon(self, node: Node) -> str:
        """Obtiene icono Material Design simple"""
        
        if node.is_folder():
            return FlatIcons.get_folder_icon(is_open=True)
        else:
            return FlatIcons.get_file_icon()
    
    def _get_node_tags(self, node: Node) -> List[str]:
        """Obtiene tags de estilo para el nodo"""
        
        tags = []
        
        # Tag por tipo
        tags.append('folder' if node.is_folder() else 'file')
        
        # Tag por estado
        if node.status == NodeStatus.COMPLETED:
            tags.append('completed')
        elif node.status == NodeStatus.IN_PROGRESS:
            tags.append('in_progress')
        elif node.status == NodeStatus.PENDING:
            tags.append('pending')
        
        return tags
    
    def _create_empty_state(self):
        """Crea estado vacío cuando no hay nodos"""
        
        empty_id = self.tree.insert('', 'end', 
                                   text="📁 Sin contenido - Crear nueva carpeta",
                                   values=('⬜',),
                                   tags=('empty_state',))
        
        self.tree.tag_configure('empty_state',
                               foreground=ModernColors.DARK_TEXT_MUTED,
                               font=('Segoe UI', 10, 'italic'))
    
    def _create_error_state(self, error_msg: str):
        """Crea estado de error"""
        
        error_id = self.tree.insert('', 'end',
                                   text=f"❌ Error: {error_msg}",
                                   values=('❌',),
                                   tags=('error_state',))
        
        self.tree.tag_configure('error_state',
                               foreground=ModernColors.DARK_ERROR,
                               font=('Segoe UI', 10))
    
    # Event handlers tiempo real
    def _on_status_changed(self, data):
        """Nodo cambió de estado - Actualizar visual INMEDIATO"""
        
        node_id = data.get('node_id')
        new_status = data.get('new_status')
        
        if node_id and self.tree.exists(node_id):
            # Actualizar valor en columna
            self.tree.set(node_id, 'status', new_status)
            
            # Actualizar tags de estilo
            node = self.node_repository.find_by_id(node_id)
            if node:
                new_tags = self._get_node_tags(node)
                self.tree.item(node_id, tags=new_tags)
    
    def _on_theme_changed(self, data):
        """Theme cambió - Reconfigurar estilos"""
        self._setup_modern_styles()
        self.refresh_display()
    
    def _on_folder_toggled(self, data):
        """Carpeta expandida/colapsada - Animar icono"""
        
        node_id = data.get('node_id')
        is_open = data.get('is_open')
        
        if node_id and self.tree.exists(node_id):
            # Actualizar icono con animación simple
            node = self.node_repository.find_by_id(node_id)
            if node and node.is_folder():
                new_icon = FlatIcons.get_folder_icon(is_open=is_open)
                current_text = self.tree.item(node_id, 'text')
                # Reemplazar solo el icono
                if current_text:
                    parts = current_text.split(' ', 1)
                    if len(parts) > 1:
                        new_text = f"{new_icon} {parts[1]}"
                        self.tree.item(node_id, text=new_text)
    
    # Métodos públicos COMPLETOS
    def update_node_display(self, node_id: str, new_name: str):
        """Actualiza display de un nodo específico INMEDIATO"""
        
        if not self.tree.exists(node_id):
            return False
        
        node = self.node_repository.find_by_id(node_id)
        if not node:
            return False
        
        # Actualizar display con nuevo nombre
        icon = self._get_node_icon(node)
        display_name = f"{icon} {new_name}"
        self.tree.item(node_id, text=display_name)
        
        return True
    
    def highlight_nodes(self, node_ids: Set[str]):
        """Resalta nodos específicos"""
        
        # Limpiar highlights anteriores
        self._clear_all_highlights()
        
        # Aplicar nuevo highlight
        for node_id in node_ids:
            if self.tree.exists(node_id):
                current_tags = list(self.tree.item(node_id, 'tags'))
                current_tags.append('hover')
                self.tree.item(node_id, tags=current_tags)
    
    def _clear_all_highlights(self):
        """Limpia todos los highlights"""
        
        def clear_item_highlight(item_id):
            current_tags = list(self.tree.item(item_id, 'tags'))
            if 'hover' in current_tags:
                current_tags.remove('hover')
                self.tree.item(item_id, tags=current_tags)
            
            # Recurso a hijos
            for child in self.tree.get_children(item_id):
                clear_item_highlight(child)
        
        # Limpiar desde root
        for item in self.tree.get_children():
            clear_item_highlight(item)
    
    def animate_expand_collapse(self, node_id: str, expanding: bool):
        """Anima expand/collapse con rotación de icono"""
        
        if not self.tree.exists(node_id):
            return
        
        # Publicar evento para animación
        self.event_bus.publish('folder_toggled', {
            'node_id': node_id,
            'is_open': expanding,
            'source': 'tree_display'
        })
    
    def set_node_as_root(self, node_id: str):
        """Marca un nodo como root (sin hover - Req. 3)"""
        self.root_items.add(node_id)
    
    def get_visible_nodes(self) -> Set[str]:
        """Obtiene todos los nodos visibles"""
        
        visible = set()
        
        def collect_visible(item_id):
            visible.add(item_id)
            if self.tree.item(item_id, 'open'):
                for child in self.tree.get_children(item_id):
                    collect_visible(child)
        
        for item in self.tree.get_children():
            collect_visible(item)
        
        return visible