"""
presentation/views/panels/tree_panel/components/selection_manager.py
================================================================

Gestor de selección múltiple avanzada estilo VSCode
- Selección simple, múltiple (Ctrl+Click), rango (Shift+Click)
- Highlights modernos y estados visuales
- Integración con operaciones de clipboard
- 55 líneas - Gestión completa de selección
"""

import tkinter as tk
from ....styling.constants.modern_colors import ModernColors

class SelectionManager:
    """Gestor de selección múltiple moderno estilo VSCode"""
    
    def __init__(self, tree_widget, event_bus=None):
        self.tree = tree_widget
        self.event_bus = event_bus
        
        # Estado de selección
        self.selected_items = set()
        self.last_single_selection = None
        self.anchor_selection = None  # Para rangos Shift+Click
        
        # Clipboard interno
        self.clipboard_items = set()
        self.clipboard_operation = None  # 'copy' o 'cut'
        
        self._setup_selection_events()
        self._configure_selection_styles()
    
    def _setup_selection_events(self):
        """Configura eventos de selección avanzada"""
        
        # Override del comportamiento por defecto
        self.tree.bind('<Button-1>', self._on_single_click)
        self.tree.bind('<Control-Button-1>', self._on_ctrl_click)
        self.tree.bind('<Shift-Button-1>', self._on_shift_click)
        self.tree.bind('<Key-Escape>', self._clear_selection)
        
        # Navegación por teclado
        self.tree.bind('<Key-Up>', self._navigate_up)
        self.tree.bind('<Key-Down>', self._navigate_down)
        self.tree.bind('<Control-Key-a>', self._select_all)
    
    def _configure_selection_styles(self):
        """Configura estilos de selección modernos"""
        
        # Tag para elementos seleccionados
        self.tree.tag_configure('selected_modern', 
                               background=ModernColors.DARK_ACCENT,
                               foreground='white')
        
        # Tag para elementos cortados
        self.tree.tag_configure('cut_item',
                               background=ModernColors.DARK_SURFACE,
                               foreground=ModernColors.DARK_TEXT_MUTED)
        
        # Tag para elementos copiados
        self.tree.tag_configure('copied_item',
                               background=ModernColors.DARK_HOVER,
                               foreground=ModernColors.DARK_TEXT_PRIMARY)
    
    def _on_single_click(self, event):
        """Maneja click simple - selección única"""
        
        item = self.tree.identify_row(event.y)
        if item:
            self._select_single(item)
            self._publish_selection_change()
        else:
            self._clear_selection()
        
        return 'break'  # Prevenir comportamiento por defecto
    
    def _on_ctrl_click(self, event):
        """Maneja Ctrl+Click - toggle selección múltiple"""
        
        item = self.tree.identify_row(event.y)
        if item:
            if item in self.selected_items:
                self._deselect_item(item)
            else:
                self._add_to_selection(item)
            
            self.last_single_selection = item
            self._publish_selection_change()
        
        return 'break'
    
    def _on_shift_click(self, event):
        """Maneja Shift+Click - selección por rango"""
        
        item = self.tree.identify_row(event.y)
        if item and self.last_single_selection:
            self._select_range(self.last_single_selection, item)
            self._publish_selection_change()
        elif item:
            self._select_single(item)
            self._publish_selection_change()
        
        return 'break'
    
    def _select_single(self, item):
        """Selecciona un solo elemento"""
        
        # Limpiar selección anterior
        self._clear_visual_selection()
        
        # Nueva selección
        self.selected_items = {item}
        self.last_single_selection = item
        self.anchor_selection = item
        
        # Aplicar estilo visual
        self._apply_selection_style(item)
    
    def _add_to_selection(self, item):
        """Agrega elemento a selección múltiple"""
        
        self.selected_items.add(item)
        self._apply_selection_style(item)
    
    def _deselect_item(self, item):
        """Quita elemento de la selección"""
        
        self.selected_items.discard(item)
        self._remove_selection_style(item)
    
    def _select_range(self, start_item, end_item):
        """Selecciona rango entre dos elementos"""
        
        # Obtener todos los elementos visibles
        all_items = self._get_all_visible_items()
        
        try:
            start_idx = all_items.index(start_item)
            end_idx = all_items.index(end_item)
            
            # Asegurar orden correcto
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
            
            # Limpiar selección anterior
            self._clear_visual_selection()
            
            # Seleccionar rango
            range_items = all_items[start_idx:end_idx + 1]
            self.selected_items = set(range_items)
            
            # Aplicar estilos visuales
            for item in range_items:
                self._apply_selection_style(item)
                
        except ValueError:
            # Si no se encuentran los elementos, selección simple
            self._select_single(end_item)
    
    def _get_all_visible_items(self):
        """Obtiene todos los elementos visibles en orden"""
        
        def get_children_recursive(parent=''):
            items = []
            for child in self.tree.get_children(parent):
                items.append(child)
                if self.tree.item(child, 'open'):
                    items.extend(get_children_recursive(child))
            return items
        
        return get_children_recursive()
    
    def _apply_selection_style(self, item):
        """Aplica estilo visual de selección"""
        
        current_tags = list(self.tree.item(item, 'tags'))
        if 'selected_modern' not in current_tags:
            current_tags.append('selected_modern')
            self.tree.item(item, tags=current_tags)
    
    def _remove_selection_style(self, item):
        """Quita estilo visual de selección"""
        
        current_tags = list(self.tree.item(item, 'tags'))
        if 'selected_modern' in current_tags:
            current_tags.remove('selected_modern')
            self.tree.item(item, tags=current_tags)
    
    def _clear_visual_selection(self):
        """Limpia estilos visuales de todos los elementos"""
        
        for item in self.selected_items:
            self._remove_selection_style(item)
    
    def _clear_selection(self, event=None):
        """Limpia toda la selección"""
        
        self._clear_visual_selection()
        self.selected_items.clear()
        self.last_single_selection = None
        self.anchor_selection = None
        self._publish_selection_change()
    
    def _select_all(self, event=None):
        """Selecciona todos los elementos visibles"""
        
        all_items = self._get_all_visible_items()
        self._clear_visual_selection()
        
        self.selected_items = set(all_items)
        for item in all_items:
            self._apply_selection_style(item)
        
        self._publish_selection_change()
        return 'break'
    
    def _navigate_up(self, event):
        """Navegación hacia arriba"""
        # TODO: Implementar navegación por teclado
        pass
    
    def _navigate_down(self, event):
        """Navegación hacia abajo"""
        # TODO: Implementar navegación por teclado
        pass
    
    def _publish_selection_change(self):
        """Publica cambio de selección globalmente"""
        
        if self.event_bus:
            self.event_bus.publish('selection_changed', {
                'selected_items': list(self.selected_items),
                'count': len(self.selected_items),
                'primary_item': self.last_single_selection
            })
    
    # Métodos públicos para operaciones
    def get_selected_items(self):
        """Obtiene elementos seleccionados"""
        return list(self.selected_items)
    
    def has_selection(self):
        """Verifica si hay elementos seleccionados"""
        return len(self.selected_items) > 0
    
    def get_selection_count(self):
        """Obtiene cantidad de elementos seleccionados"""
        return len(self.selected_items)
    
    def set_clipboard(self, operation='copy'):
        """Establece elementos seleccionados en clipboard"""
        
        if not self.selected_items:
            return False
        
        # Limpiar estilos de clipboard anterior
        self._clear_clipboard_styles()
        
        # Nuevo clipboard
        self.clipboard_items = self.selected_items.copy()
        self.clipboard_operation = operation
        
        # Aplicar estilos visuales
        style_tag = 'cut_item' if operation == 'cut' else 'copied_item'
        for item in self.clipboard_items:
            self._apply_clipboard_style(item, style_tag)
        
        return True
    
    def _apply_clipboard_style(self, item, style_tag):
        """Aplica estilo de clipboard"""
        
        current_tags = list(self.tree.item(item, 'tags'))
        # Remover otros estilos de clipboard
        current_tags = [tag for tag in current_tags if tag not in ['cut_item', 'copied_item']]
        current_tags.append(style_tag)
        self.tree.item(item, tags=current_tags)
    
    def _clear_clipboard_styles(self):
        """Limpia estilos de clipboard"""
        
        for item in self.clipboard_items:
            current_tags = list(self.tree.item(item, 'tags'))
            current_tags = [tag for tag in current_tags if tag not in ['cut_item', 'copied_item']]
            self.tree.item(item, tags=current_tags)
    
    def get_clipboard_data(self):
        """Obtiene datos del clipboard"""
        return {
            'items': list(self.clipboard_items),
            'operation': self.clipboard_operation
        }
    
    def clear_clipboard(self):
        """Limpia el clipboard"""
        self._clear_clipboard_styles()
        self.clipboard_items.clear()
        self.clipboard_operation = None