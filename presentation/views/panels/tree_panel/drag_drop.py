# presentation/views/panels/tree_panel/drag_drop.py
"""
Sistema de drag & drop avanzado para TreeView con efectos visuales.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Tuple


class DragDropEffect:
    """Efectos visuales para drag & drop."""
    
    # Colores y estilos - MÁS SUAVES
    DROP_LINE_COLOR = "#3498db"
    DROP_HIGHLIGHT_COLOR = "#e8f4fd" 
    DRAG_ITEM_COLOR = "#ffeaa7"
    
    # Caracteres para indicadores - MÁS FINOS
    DROP_INDICATOR = "▸"
    DROP_LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"  # Línea más larga y fina
    
    @staticmethod
    def create_drop_line() -> str:
        """Crear línea de inserción visual más fina."""
        return f"  ┃ {DragDropEffect.DROP_LINE}"
    
    @staticmethod 
    def create_drop_indicator(text: str) -> str:
        """Crear indicador de drop con texto."""
        return f"◦ {text}"  # Círculo más suave


class TreeDragDrop:
    """Manejo completo de drag & drop para TreeView."""
    
    def __init__(self, tree_widget: ttk.Treeview, node_repository, 
                 on_move_callback: Optional[Callable] = None):
        self.tree = tree_widget
        self.node_repository = node_repository
        self.on_move_callback = on_move_callback
        
        # Estado del drag & drop
        self.dragging = False
        self.drag_item = None
        self.drag_start_pos = None
        self.drop_target = None
        self.drop_position = None  # 'before', 'after', 'inside'
        self.drop_indicator_item = None
        
        # Configuración - MÁS RESPONSIVO
        self.drag_threshold = 3  # pixels para iniciar drag (más sensible)
        self.auto_expand_delay = 800  # ms para auto-expandir (más rápido)
        self.auto_expand_timer = None
        
        self._setup_bindings()
    
    def _setup_bindings(self):
        """Configurar eventos de drag & drop."""
        self.tree.bind('<Button-1>', self._on_button_press)
        self.tree.bind('<B1-Motion>', self._on_drag_motion)
        self.tree.bind('<ButtonRelease-1>', self._on_drop)
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        
        # Prevenir selección durante drag
        self.tree.bind('<B1-Leave>', self._on_leave)
        self.tree.bind('<B1-Enter>', self._on_enter)
    
    def _on_button_press(self, event):
        """Manejar inicio de posible drag."""
        item = self.tree.identify_row(event.y)
        
        if item:
            # Guardar posición inicial y item
            self.drag_start_pos = (event.x, event.y)
            self.drag_item = item
            self.dragging = False
            
            # Seleccionar item
            self.tree.selection_set(item)
    
    def _on_drag_motion(self, event):
        """Manejar movimiento durante drag."""
        if not self.drag_item or not self.drag_start_pos:
            return
        
        # Calcular distancia desde inicio
        dx = abs(event.x - self.drag_start_pos[0])
        dy = abs(event.y - self.drag_start_pos[1])
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Iniciar drag si se supera el threshold
        if not self.dragging and distance > self.drag_threshold:
            self._start_drag()
        
        if self.dragging:
            self._update_drag_visual(event)
    
    def _start_drag(self):
        """Iniciar operación de drag."""
        self.dragging = True
        
        # Cambiar cursor
        self.tree.config(cursor="hand2")
        
        # Resaltar item siendo arrastrado
        self._highlight_drag_item(True)
        
        print(f"🔄 Iniciando drag de: {self.drag_item}")
    
    def _update_drag_visual(self, event):
        """Actualizar efectos visuales durante drag."""
        # Identificar item bajo el cursor
        target_item = self.tree.identify_row(event.y)
        
        if target_item and target_item != self.drag_item:
            # Determinar posición de drop
            drop_pos = self._calculate_drop_position(event, target_item)
            
            if target_item != self.drop_target or drop_pos != self.drop_position:
                self._update_drop_indicator(target_item, drop_pos)
                
                # Auto-expandir carpetas después de delay
                if drop_pos == 'inside' and self._is_folder(target_item):
                    self._schedule_auto_expand(target_item)
        else:
            self._clear_drop_indicator()
    
    def _calculate_drop_position(self, event, target_item) -> str:
        """Calcular posición de drop: 'before', 'after', 'inside'."""
        bbox = self.tree.bbox(target_item)
        if not bbox:
            return 'inside'
        
        item_y = bbox[1]
        item_height = bbox[3]
        relative_y = event.y - item_y
        
        # Dividir en 3 zonas
        if relative_y < item_height * 0.25:
            return 'before'
        elif relative_y > item_height * 0.75:
            return 'after'
        else:
            return 'inside'
    
    def _update_drop_indicator(self, target_item, position):
        """Actualizar indicador visual de drop."""
        # Limpiar indicador anterior
        self._clear_drop_indicator()
        
        self.drop_target = target_item
        self.drop_position = position
        
        # Crear nuevo indicador según posición
        if position == 'before':
            self._create_line_indicator(target_item, before=True)
        elif position == 'after':
            self._create_line_indicator(target_item, before=False)
        elif position == 'inside':
            self._create_highlight_indicator(target_item)
    
    def _create_line_indicator(self, target_item, before=True):
        """Crear línea de inserción más fina y elegante."""
        try:
            parent = self.tree.parent(target_item)
            target_index = self.tree.index(target_item)
            
            # Crear item temporal para la línea
            insert_index = target_index if before else target_index + 1
            
            self.drop_indicator_item = self.tree.insert(
                parent, 
                insert_index,
                text=DragDropEffect.create_drop_line(),
                tags=('drop_indicator',)
            )
            
            # Configurar estilo del indicador - MÁS SUTIL
            self.tree.tag_configure('drop_indicator', 
                                  foreground=DragDropEffect.DROP_LINE_COLOR,
                                  font=('Arial', 9),  # Fuente más pequeña
                                  background='#f8f9fa')  # Fondo sutil
            
        except Exception as e:
            print(f"❌ Error creando línea indicadora: {e}")
    
    def _create_highlight_indicator(self, target_item):
        """Crear resaltado más suave para drop 'inside'."""
        try:
            # Cambiar color de fondo del item de forma más sutil
            self.tree.set(target_item, '#0', 
                         DragDropEffect.create_drop_indicator(
                             self.tree.item(target_item, 'text')
                         ))
            
            # Agregar tag de highlight
            current_tags = list(self.tree.item(target_item, 'tags'))
            current_tags.append('drop_highlight')
            self.tree.item(target_item, tags=current_tags)
            
            self.tree.tag_configure('drop_highlight',
                                  background=DragDropEffect.DROP_HIGHLIGHT_COLOR,
                                  relief='solid',
                                  borderwidth=1)
                                  
        except Exception as e:
            print(f"❌ Error creando highlight: {e}")
    
    def _clear_drop_indicator(self):
        """Limpiar indicadores visuales."""
        # Eliminar línea indicadora
        if self.drop_indicator_item:
            try:
                self.tree.delete(self.drop_indicator_item)
            except:
                pass
            self.drop_indicator_item = None
        
        # Limpiar highlight
        if self.drop_target:
            try:
                # Restaurar texto original
                original_text = self._get_original_text(self.drop_target)
                self.tree.item(self.drop_target, text=original_text)
                
                # Remover tag de highlight
                current_tags = list(self.tree.item(self.drop_target, 'tags'))
                if 'drop_highlight' in current_tags:
                    current_tags.remove('drop_highlight')
                    self.tree.item(self.drop_target, tags=current_tags)
            except:
                pass
        
        self.drop_target = None
        self.drop_position = None
    
    def _schedule_auto_expand(self, item):
        """Programar auto-expansión de carpeta."""
        if self.auto_expand_timer:
            self.tree.after_cancel(self.auto_expand_timer)
        
        self.auto_expand_timer = self.tree.after(
            self.auto_expand_delay,
            lambda: self._auto_expand(item)
        )
    
    def _auto_expand(self, item):
        """Auto-expandir carpeta durante hover."""
        try:
            if not self.tree.item(item, 'open'):
                self.tree.item(item, open=True)
                print(f"📂 Auto-expandido: {item}")
        except:
            pass
    
    def _on_drop(self, event):
        """Manejar finalización del drop."""
        if not self.dragging:
            return
        
        success = False
        
        if self.drop_target and self.drop_position:
            success = self._perform_move()
        
        # Limpiar estado de drag
        self._end_drag(success)
    
    def _perform_move(self) -> bool:
        """Realizar el movimiento del nodo."""
        try:
            # Validar movimiento
            if not self._validate_move():
                return False
            
            # Obtener nodos
            drag_node = self.node_repository.find_by_id(self.drag_item)
            target_node = self.node_repository.find_by_id(self.drop_target)
            
            if not drag_node or not target_node:
                print("❌ Nodos no encontrados para el movimiento")
                return False
            
            # Realizar movimiento según posición
            if self.drop_position == 'inside':
                success = self._move_inside(drag_node, target_node)
            else:
                success = self._move_sibling(drag_node, target_node, 
                                           self.drop_position == 'before')
            
            if success and self.on_move_callback:
                self.on_move_callback()
            
            return success
            
        except Exception as e:
            print(f"❌ Error en movimiento: {e}")
            return False
    
    def _move_inside(self, drag_node, target_node) -> bool:
        """Mover nodo dentro de una carpeta."""
        if not target_node.is_folder():
            print("❌ No se puede mover dentro de un archivo")
            return False
        
        # Actualizar padre
        old_parent_id = drag_node.parent_id
        drag_node.parent_id = target_node.node_id
        
        # Actualizar en repositorio
        self.node_repository.save(drag_node)
        
        print(f"✅ Movido '{drag_node.name}' dentro de '{target_node.name}'")
        return True
    
    def _move_sibling(self, drag_node, target_node, before=True) -> bool:
        """Mover nodo como hermano de otro."""
        # Mismo padre que el target
        drag_node.parent_id = target_node.parent_id
        
        # Actualizar en repositorio  
        self.node_repository.save(drag_node)
        
        position = "antes" if before else "después"
        print(f"✅ Movido '{drag_node.name}' {position} de '{target_node.name}'")
        return True
    
    def _validate_move(self) -> bool:
        """Validar si el movimiento es permitido."""
        if self.drag_item == self.drop_target:
            return False
        
        # Evitar mover un padre dentro de su hijo (ciclo)
        if self._would_create_cycle():
            print("❌ Movimiento crearía un ciclo")
            return False
        
        return True
    
    def _would_create_cycle(self) -> bool:
        """Verificar si el movimiento crearía un ciclo."""
        current = self.drop_target
        
        while current:
            if current == self.drag_item:
                return True
            current = self.tree.parent(current)
        
        return False
    
    def _end_drag(self, success=False):
        """Finalizar operación de drag."""
        # Restaurar cursor
        self.tree.config(cursor="")
        
        # Limpiar efectos visuales
        self._clear_drop_indicator()
        self._highlight_drag_item(False)
        
        # Cancelar timer de auto-expand
        if self.auto_expand_timer:
            self.tree.after_cancel(self.auto_expand_timer)
            self.auto_expand_timer = None
        
        # Limpiar estado
        self.dragging = False
        self.drag_item = None
        self.drag_start_pos = None
        self.drop_target = None
        self.drop_position = None
        
        if success:
            print("✅ Drag & Drop completado")
        else:
            print("❌ Drag & Drop cancelado")
    
    def _highlight_drag_item(self, highlight=True):
        """Resaltar item siendo arrastrado."""
        if not self.drag_item:
            return
        
        try:
            current_tags = list(self.tree.item(self.drag_item, 'tags'))
            
            if highlight:
                if 'dragging' not in current_tags:
                    current_tags.append('dragging')
                    
                self.tree.tag_configure('dragging',
                                      background=DragDropEffect.DRAG_ITEM_COLOR,
                                      foreground='white')
            else:
                if 'dragging' in current_tags:
                    current_tags.remove('dragging')
            
            self.tree.item(self.drag_item, tags=current_tags)
        except:
            pass
    
    def _is_folder(self, item) -> bool:
        """Verificar si un item es carpeta."""
        try:
            node = self.node_repository.find_by_id(item)
            return node and node.is_folder()
        except:
            return False
    
    def _get_original_text(self, item) -> str:
        """Obtener texto original de un item."""
        try:
            node = self.node_repository.find_by_id(item)
            if node:
                icon = "📁" if node.is_folder() else "📄"
                return f"{icon} {node.name}"
            return self.tree.item(item, 'text')
        except:
            return self.tree.item(item, 'text')
    
    def _on_double_click(self, event):
        """Manejar doble click (no hacer drag)."""
        self._end_drag()
    
    def _on_leave(self, event):
        """Manejar salida del widget."""
        if self.dragging:
            self._clear_drop_indicator()
    
    def _on_enter(self, event):
        """Manejar entrada al widget."""
        pass
    
    def enable(self):
        """Habilitar drag & drop."""
        self._setup_bindings()
    
    def disable(self):
        """Deshabilitar drag & drop."""
        events = ['<Button-1>', '<B1-Motion>', '<ButtonRelease-1>',
                 '<Double-Button-1>', '<B1-Leave>', '<B1-Enter>']
        
        for event in events:
            self.tree.unbind(event)