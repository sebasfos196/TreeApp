#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Models - Clipboard
Sistema de portapapeles avanzado para TreeApp v4 Pro

Responsabilidades:
- Gestionar copy/cut/paste de nodos individuales y múltiples
- Soportar duplicación de ramas completas
- Validar jerarquías y evitar loops
- Manejar auto-renombrado en conflictos
- Proporcionar feedback visual de elementos cortados
"""

import copy
import logging
from typing import List, Dict, Optional, Set, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class ClipboardOperation(Enum):
    """Tipos de operación en el portapapeles"""
    COPY = "copy"
    CUT = "cut"
    NONE = "none"


@dataclass
class ClipboardItem:
    """Elemento individual en el portapapeles"""
    node_id: str
    node_data: Dict[str, Any]
    original_parent_id: Optional[str] = None
    operation: ClipboardOperation = ClipboardOperation.COPY
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        # Crear copia profunda de los datos para evitar referencias
        self.node_data = copy.deepcopy(self.node_data)


class AdvancedClipboard:
    """
    Sistema avanzado de portapapeles para TreeApp v4 Pro
    
    Características:
    - Soporte para múltiples elementos
    - Validación de jerarquías
    - Auto-renombrado en conflictos
    - Preservación de estructura de árbol
    - Feedback visual para elementos cortados
    """
    
    def __init__(self, event_bus=None):
        """
        Inicializar el portapapeles
        
        Args:
            event_bus: Bus de eventos para notificaciones
        """
        self.event_bus = event_bus
        self._items: List[ClipboardItem] = []
        self._operation: ClipboardOperation = ClipboardOperation.NONE
        self._cut_items: Set[str] = set()  # IDs de nodos cortados para feedback visual
        
        # Configuración
        self.max_items = 100  # Límite de elementos en portapapeles
        self.auto_rename_duplicates = True
        self.preserve_hierarchy = True
    
    def copy(self, node_ids: List[str], nodes_registry: Dict[str, Any]) -> bool:
        """
        Copiar nodos al portapapeles
        
        Args:
            node_ids: Lista de IDs de nodos a copiar
            nodes_registry: Registro completo de nodos del proyecto
            
        Returns:
            True si la operación fue exitosa
        """
        try:
            # Limpiar portapapeles anterior
            self.clear()
            
            # Validar y filtrar nodos válidos
            valid_nodes = self._filter_valid_nodes(node_ids, nodes_registry)
            if not valid_nodes:
                logger.warning("No se encontraron nodos válidos para copiar")
                return False
            
            # Ordenar por jerarquía para preservar estructura
            ordered_nodes = self._order_by_hierarchy(valid_nodes, nodes_registry)
            
            # Crear elementos del portapapeles
            for node_id in ordered_nodes:
                node_data = nodes_registry[node_id]
                parent_id = self._get_parent_id(node_id, nodes_registry)
                
                item = ClipboardItem(
                    node_id=node_id,
                    node_data=node_data,
                    original_parent_id=parent_id,
                    operation=ClipboardOperation.COPY
                )
                self._items.append(item)
            
            self._operation = ClipboardOperation.COPY
            
            # Emitir evento
            if self.event_bus:
                self.event_bus.emit('clipboard_copy', {
                    'items_count': len(self._items),
                    'node_ids': node_ids
                })
            
            logger.info(f"Copiados {len(self._items)} elementos al portapapeles")
            return True
            
        except Exception as e:
            logger.error(f"Error copiando al portapapeles: {e}")
            return False
    
    def cut(self, node_ids: List[str], nodes_registry: Dict[str, Any]) -> bool:
        """
        Cortar nodos al portapapeles
        
        Args:
            node_ids: Lista de IDs de nodos a cortar
            nodes_registry: Registro completo de nodos del proyecto
            
        Returns:
            True si la operación fue exitosa
        """
        try:
            # Copiar primero
            if not self.copy(node_ids, nodes_registry):
                return False
            
            # Cambiar operación a CUT
            self._operation = ClipboardOperation.CUT
            for item in self._items:
                item.operation = ClipboardOperation.CUT
            
            # Marcar nodos como cortados para feedback visual
            self._cut_items = set(node_ids)
            
            # Emitir evento
            if self.event_bus:
                self.event_bus.emit('clipboard_cut', {
                    'items_count': len(self._items),
                    'node_ids': node_ids
                })
            
            logger.info(f"Cortados {len(self._items)} elementos al portapapeles")
            return True
            
        except Exception as e:
            logger.error(f"Error cortando al portapapeles: {e}")
            return False
    
    def paste(self, target_parent_id: Optional[str], 
              nodes_registry: Dict[str, Any],
              tree_structure) -> List[str]:
        """
        Pegar elementos del portapapeles
        
        Args:
            target_parent_id: ID del nodo padre donde pegar (None = raíz)
            nodes_registry: Registro de nodos del proyecto
            tree_structure: Estructura del árbol para validaciones
            
        Returns:
            Lista de IDs de los nuevos nodos creados
        """
        if not self.has_items():
            logger.warning("Portapapeles vacío, no hay nada que pegar")
            return []
        
        try:
            new_node_ids = []
            
            # Validar destino
            if not self._validate_paste_target(target_parent_id, nodes_registry, tree_structure):
                logger.warning("Destino de pegado no válido")
                return []
            
            # Procesar cada elemento
            for item in self._items:
                new_node_id = self._paste_item(item, target_parent_id, nodes_registry, tree_structure)
                if new_node_id:
                    new_node_ids.append(new_node_id)
            
            # Si era una operación CUT, limpiar nodos originales
            if self._operation == ClipboardOperation.CUT:
                self._remove_cut_nodes(nodes_registry, tree_structure)
                self._cut_items.clear()
                self.clear()  # Limpiar portapapeles después de cut
            
            # Emitir evento
            if self.event_bus:
                self.event_bus.emit('clipboard_paste', {
                    'new_nodes': new_node_ids,
                    'target_parent': target_parent_id,
                    'operation': self._operation.value
                })
            
            logger.info(f"Pegados {len(new_node_ids)} elementos")
            return new_node_ids
            
        except Exception as e:
            logger.error(f"Error pegando desde portapapeles: {e}")
            return []
    
    def duplicate(self, node_ids: List[str], 
                  nodes_registry: Dict[str, Any],
                  tree_structure) -> List[str]:
        """
        Duplicar nodos in-situ (sin usar portapapeles)
        
        Args:
            node_ids: IDs de nodos a duplicar
            nodes_registry: Registro de nodos
            tree_structure: Estructura del árbol
            
        Returns:
            Lista de IDs de nodos duplicados
        """
        try:
            duplicated_ids = []
            
            for node_id in node_ids:
                if node_id not in nodes_registry:
                    continue
                
                # Obtener padre del nodo original
                parent_id = self._get_parent_id(node_id, nodes_registry)
                
                # Crear copia temporal en portapapeles
                temp_clipboard = AdvancedClipboard()
                temp_clipboard.copy([node_id], nodes_registry)
                
                # Pegar junto al nodo original
                new_ids = temp_clipboard.paste(parent_id, nodes_registry, tree_structure)
                duplicated_ids.extend(new_ids)
            
            # Emitir evento
            if self.event_bus:
                self.event_bus.emit('nodes_duplicated', {
                    'original_ids': node_ids,
                    'duplicated_ids': duplicated_ids
                })
            
            logger.info(f"Duplicados {len(duplicated_ids)} nodos")
            return duplicated_ids
            
        except Exception as e:
            logger.error(f"Error duplicando nodos: {e}")
            return []
    
    def _paste_item(self, item: ClipboardItem, target_parent_id: Optional[str],
                   nodes_registry: Dict[str, Any], tree_structure) -> Optional[str]:
        """Pegar un elemento individual"""
        try:
            # Generar nuevo ID único
            new_id = self._generate_unique_id(item.node_data['name'], nodes_registry)
            
            # Crear copia de los datos
            new_node_data = copy.deepcopy(item.node_data)
            
            # Manejar auto-renombrado si hay conflicto
            if self.auto_rename_duplicates:
                new_node_data['name'] = self._resolve_name_conflict(
                    new_node_data['name'], target_parent_id, nodes_registry, tree_structure
                )
            
            # Actualizar timestamps
            new_node_data['created'] = datetime.now().isoformat()
            new_node_data['modified'] = datetime.now().isoformat()
            
            # Agregar al registro
            nodes_registry[new_id] = new_node_data
            
            # Si es una carpeta, duplicar recursivamente su contenido
            if new_node_data.get('type') == 'folder':
                self._duplicate_folder_contents(item.node_id, new_id, nodes_registry, tree_structure)
            
            return new_id
            
        except Exception as e:
            logger.error(f"Error pegando elemento {item.node_id}: {e}")
            return None
    
    def _duplicate_folder_contents(self, original_folder_id: str, new_folder_id: str,
                                 nodes_registry: Dict[str, Any], tree_structure):
        """Duplicar recursivamente el contenido de una carpeta"""
        # Obtener hijos del folder original
        children = tree_structure.get_children(original_folder_id)
        
        for child_id in children:
            if child_id in nodes_registry:
                # Crear elemento temporal para el hijo
                child_item = ClipboardItem(
                    node_id=child_id,
                    node_data=nodes_registry[child_id],
                    original_parent_id=original_folder_id
                )
                
                # Pegar hijo en el nuevo folder
                self._paste_item(child_item, new_folder_id, nodes_registry, tree_structure)
    
    def _resolve_name_conflict(self, name: str, parent_id: Optional[str],
                             nodes_registry: Dict[str, Any], tree_structure) -> str:
        """Resolver conflictos de nombres generando nombre único"""
        base_name = name
        counter = 1
        
        # Obtener hermanos del destino
        siblings = tree_structure.get_children(parent_id) if parent_id else tree_structure.get_roots()
        sibling_names = {nodes_registry[sid]['name'] for sid in siblings if sid in nodes_registry}
        
        # Generar nombre único
        while name in sibling_names:
            if counter == 1:
                # Primera iteración: agregar " (copia)"
                name = f"{base_name} (copia)"
            else:
                # Siguientes iteraciones: " (copia 2)", " (copia 3)", etc.
                name = f"{base_name} (copia {counter})"
            counter += 1
        
        return name
    
    def _filter_valid_nodes(self, node_ids: List[str], 
                           nodes_registry: Dict[str, Any]) -> List[str]:
        """Filtrar solo nodos válidos que existen en el registro"""
        return [nid for nid in node_ids if nid in nodes_registry]
    
    def _order_by_hierarchy(self, node_ids: List[str], 
                           nodes_registry: Dict[str, Any]) -> List[str]:
        """Ordenar nodos por jerarquía (padres antes que hijos)"""
        # Por simplicidad, mantener el orden original
        # TODO: Implementar ordenamiento jerárquico real si es necesario
        return node_ids
    
    def _get_parent_id(self, node_id: str, nodes_registry: Dict[str, Any]) -> Optional[str]:
        """Obtener ID del padre de un nodo"""
        # Esta función depende de cómo esté estructurada la información de padres
        # Puede ser un campo en node_data o manejado por tree_structure
        return nodes_registry[node_id].get('parent_id')
    
    def _generate_unique_id(self, base_name: str, nodes_registry: Dict[str, Any]) -> str:
        """Generar ID único para un nuevo nodo"""
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = str(uuid.uuid4())[:8]
        return f"node_{timestamp}_{unique_suffix}"
    
    def _validate_paste_target(self, target_parent_id: Optional[str],
                              nodes_registry: Dict[str, Any], tree_structure) -> bool:
        """Validar que el destino de pegado sea válido"""
        if target_parent_id is None:
            return True  # Pegar en raíz siempre válido
        
        if target_parent_id not in nodes_registry:
            return False  # Padre no existe
        
        # Solo se puede pegar dentro de carpetas
        if nodes_registry[target_parent_id].get('type') != 'folder':
            return False
        
        # Validar que no se cree un loop (para operaciones CUT)
        if self._operation == ClipboardOperation.CUT:
            for item in self._items:
                if self._would_create_loop(item.node_id, target_parent_id, tree_structure):
                    return False
        
        return True
    
    def _would_create_loop(self, node_id: str, target_parent_id: str, tree_structure) -> bool:
        """Verificar si mover un nodo crearía un loop en el árbol"""
        # Verificar si target_parent_id es descendiente de node_id
        current = target_parent_id
        while current:
            if current == node_id:
                return True
            current = tree_structure.get_parent(current)
        return False
    
    def _remove_cut_nodes(self, nodes_registry: Dict[str, Any], tree_structure):
        """Remover nodos que fueron cortados después de pegarlos"""
        for item in self._items:
            if item.operation == ClipboardOperation.CUT and item.node_id in nodes_registry:
                # Remover del registro
                del nodes_registry[item.node_id]
                # TODO: Actualizar tree_structure según su implementación
    
    # ==========================================================================
    # MÉTODOS DE CONSULTA Y UTILIDAD
    # ==========================================================================
    
    def has_items(self) -> bool:
        """Verificar si el portapapeles tiene elementos"""
        return len(self._items) > 0
    
    def get_items_count(self) -> int:
        """Obtener cantidad de elementos en el portapapeles"""
        return len(self._items)
    
    def get_operation(self) -> ClipboardOperation:
        """Obtener el tipo de operación actual"""
        return self._operation
    
    def is_cut_node(self, node_id: str) -> bool:
        """Verificar si un nodo está marcado como cortado"""
        return node_id in self._cut_items
    
    def get_cut_nodes(self) -> Set[str]:
        """Obtener conjunto de nodos cortados para feedback visual"""
        return self._cut_items.copy()
    
    def clear(self):
        """Limpiar completamente el portapapeles"""
        self._items.clear()
        self._cut_items.clear()
        self._operation = ClipboardOperation.NONE
        
        if self.event_bus:
            self.event_bus.emit('clipboard_cleared', {})
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen del estado del portapapeles"""
        return {
            'items_count': len(self._items),
            'operation': self._operation.value,
            'cut_nodes_count': len(self._cut_items),
            'has_folders': any(item.node_data.get('type') == 'folder' for item in self._items),
            'has_files': any(item.node_data.get('type') == 'file' for item in self._items)
        }


# ==========================================================================
# FUNCIONES DE UTILIDAD PARA INTEGRACIÓN CON UI
# ==========================================================================

def get_clipboard_status_text(clipboard: AdvancedClipboard) -> str:
    """Generar texto de estado para mostrar en UI"""
    if not clipboard.has_items():
        return "Portapapeles vacío"
    
    count = clipboard.get_items_count()
    operation = clipboard.get_operation()
    
    if operation == ClipboardOperation.COPY:
        return f"{count} elemento{'s' if count > 1 else ''} copiado{'s' if count > 1 else ''}"
    elif operation == ClipboardOperation.CUT:
        return f"{count} elemento{'s' if count > 1 else ''} cortado{'s' if count > 1 else ''}"
    else:
        return "Portapapeles vacío"


def apply_cut_visual_feedback(node_id: str, clipboard: AdvancedClipboard) -> Dict[str, Any]:
    """Obtener configuración visual para nodos cortados"""
    if clipboard.is_cut_node(node_id):
        return {
            'alpha': 0.5,  # Transparencia
            'style': 'dashed',  # Borde punteado
            'color': 'gray',  # Color atenuado
            'prefix': '✂️ '  # Prefijo visual
        }
    return {}