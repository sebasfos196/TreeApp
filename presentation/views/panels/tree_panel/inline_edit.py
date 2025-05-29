# presentation/views/panels/tree_panel/inline_edit.py
"""
Sistema de edición inline para TreeView - separado para mejor mantenabilidad.
"""
import tkinter as tk
from typing import Optional, Callable
from domain.node.node_entity import Node
from .tree_utils import FlatIcons, NodeValidator


class InlineEditor:
    """Maneja la edición inline de nombres de nodos en el TreeView."""
    
    def __init__(self, tree_widget, node_repository, update_callback: Optional[Callable] = None):
        self.tree = tree_widget
        self.node_repository = node_repository
        self.update_callback = update_callback
        
        # Estado de edición
        self.edit_entry: Optional[tk.Entry] = None
        self.editing_item: Optional[str] = None
        self.editing_node: Optional[Node] = None
        self.is_editing = False
    
    def start_edit(self, item_id: str, node: Node) -> bool:
        """
        Iniciar edición inline del nombre del nodo.
        
        Returns:
            bool: True si se inició la edición correctamente
        """
        if self.is_editing:
            self.cancel_edit()
        
        # Obtener posición del item
        bbox = self.tree.bbox(item_id, '#0')
        if not bbox:
            return False
        
        try:
            # Configurar estado de edición
            self.editing_item = item_id
            self.editing_node = node
            self.is_editing = True
            
            # Crear Entry temporal para edición
            x, y, width, height = bbox
            
            # Ajustar para que no cubra el icono
            icon_width = 25  # Ancho aproximado del icono
            x += icon_width
            width -= icon_width
            
            self.edit_entry = tk.Entry(
                self.tree,
                font=('Arial', 10),
                bg='#ffffff',
                fg='#2c3e50',
                relief=tk.SOLID,
                bd=1,
                highlightthickness=1,
                highlightcolor='#3498db'
            )
            
            # Posicionar Entry sobre el item
            self.edit_entry.place(x=x, y=y, width=width, height=height)
            
            # Configurar contenido inicial
            self.edit_entry.insert(0, node.name)
            self.edit_entry.select_range(0, tk.END)
            self.edit_entry.focus()
            
            # Eventos para finalizar edición
            self.edit_entry.bind('<Return>', self._finish_edit)
            self.edit_entry.bind('<Escape>', self._cancel_edit)
            self.edit_entry.bind('<FocusOut>', self._finish_edit)
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando edición inline: {e}")
            self._cleanup_edit()
            return False
    
    def _finish_edit(self, event=None) -> bool:
        """
        Finalizar edición inline y actualizar nodo.
        
        Returns:
            bool: True si se actualizó correctamente
        """
        if not self.is_editing or not self.edit_entry:
            return False
        
        try:
            new_name = self.edit_entry.get().strip()
            
            # Validar nombre
            if new_name and new_name != self.editing_node.name:
                is_valid, error_msg = NodeValidator.validate_name(
                    new_name, 
                    self.editing_node.parent_id,
                    self.editing_node.node_id,
                    self.node_repository
                )
                
                if is_valid:
                    # Actualizar nodo
                    old_name = self.editing_node.name
                    self.editing_node.name = new_name
                    self.editing_node.update_modified()
                    
                    # Guardar en repositorio
                    self.node_repository.save(self.editing_node)
                    
                    # Actualizar display en TreeView
                    self._update_tree_display(new_name)
                    
                    # Notificar callback si existe
                    if self.update_callback:
                        self.update_callback(self.editing_item, new_name)
                    
                    print(f"✏️ Renombrado inline: {old_name} → {new_name}")
                    self._cleanup_edit()
                    return True
                else:
                    # Mostrar error de validación
                    tk.messagebox.showerror("Error de validación", error_msg)
                    # Mantener edición activa para que usuario pueda corregir
                    self.edit_entry.focus()
                    return False
            
            # Sin cambios o nombre vacío
            self._cleanup_edit()
            return True
            
        except Exception as e:
            print(f"❌ Error finalizando edición inline: {e}")
            tk.messagebox.showerror("Error", f"Error al guardar cambios:\n{str(e)}")
            self._cleanup_edit()
            return False
    
    def _cancel_edit(self, event=None):
        """Cancelar edición inline sin guardar cambios."""
        self._cleanup_edit()
    
    def _update_tree_display(self, new_name: str):
        """Actualizar display del nodo en el TreeView."""
        try:
            if not self.editing_item or not self.editing_node:
                return
            
            # Determinar icono según el tipo y estado
            if self.editing_node.is_folder():
                is_open = self.tree.item(self.editing_item, 'open')
                icon = FlatIcons.FOLDER_OPEN if is_open else FlatIcons.FOLDER_CLOSED
            else:
                icon = FlatIcons.get_file_icon(new_name)
            
            display_name = f"{icon} {new_name}"
            
            # Actualizar el texto en el TreeView
            self.tree.item(self.editing_item, text=display_name)
            
        except Exception as e:
            print(f"❌ Error actualizando display del árbol: {e}")
    
    def _cleanup_edit(self):
        """Limpiar componentes de edición inline."""
        try:
            if self.edit_entry:
                self.edit_entry.destroy()
                self.edit_entry = None
        except:
            pass
        
        self.editing_item = None
        self.editing_node = None
        self.is_editing = False
    
    def cancel_edit(self):
        """Método público para cancelar edición actual."""
        if self.is_editing:
            self._cancel_edit()
    
    def is_currently_editing(self) -> bool:
        """Verificar si hay una edición en curso."""
        return self.is_editing
    
    def get_editing_item(self) -> Optional[str]:
        """Obtener el item que se está editando actualmente."""
        return self.editing_item if self.is_editing else None