#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Portapapeles para TreeApp v4 Pro
Gestión avanzada de copy/paste para nodos individuales y múltiples
"""

from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ClipboardMode(Enum):
    """Modos de operación del portapapeles"""
    CUT = "cut"
    COPY = "copy"
    NONE = "none"

@dataclass
class ClipboardData:
    """Datos almacenados en el portapapeles"""
    node_ids: List[str] = field(default_factory=list)
    mode: ClipboardMode = ClipboardMode.NONE
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source_parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_empty(self) -> bool:
        """Verificar si el portapapeles está vacío"""
        return len(self.node_ids) == 0 or self.mode == ClipboardMode.NONE
    
    def is_cut_operation(self) -> bool:
        """Verificar si es una operación de corte"""
        return self.mode == ClipboardMode.CUT
    
    def is_copy_operation(self) -> bool:
        """Verificar si es una operación de copia"""
        return self.mode == ClipboardMode.COPY
    
    def get_count(self) -> int:
        """Obtener cantidad de nodos en el portapapeles"""
        return len(self.node_ids)
    
    def has_node(self, node_id: str) -> bool:
        """Verificar si un nodo específico está en el portapapeles"""
        return node_id in self.node_ids
    
    def clear(self):
        """Limpiar el portapapeles"""
        self.node_ids.clear()
        self.mode = ClipboardMode.NONE
        self.source_parent_id = None
        self.metadata.clear()
        self.timestamp = datetime.now().isoformat()

class NodeClipboard:
    """
    Gestor del portapapeles para operaciones de nodos
    """
    
    def __init__(self):
        self.data = ClipboardData()
        self._listeners: List[callable] = []
    
    def copy_nodes(self, node_ids: List[str], source_parent_id: Optional[str] = None):
        """
        Copiar nodos al portapapeles
        
        Args:
            node_ids: Lista de IDs de nodos a copiar
            source_parent_id: ID del padre de origen
        """
        self.data.clear()
        self.data.node_ids = node_ids.copy()
        self.data.mode = ClipboardMode.COPY
        self.data.source_parent_id = source_parent_id
        self.data.metadata['operation'] = 'copy'
        
        logger.info(f"Copiados {len(node_ids)} nodos al portapapeles")
        self._notify_listeners('copy', node_ids)
    
    def cut_nodes(self, node_ids: List[str], source_parent_id: Optional[str] = None):
        """
        Cortar nodos al portapapeles
        
        Args:
            node_ids: Lista de IDs de nodos a cortar
            source_parent_id: ID del padre de origen
        """
        self.data.clear()
        self.data.node_ids = node_ids.copy()
        self.data.mode = ClipboardMode.CUT
        self.data.source_parent_id = source_parent_id
        self.data.metadata['operation'] = 'cut'
        
        logger.info(f"Cortados {len(node_ids)} nodos al portapapeles")
        self._notify_listeners('cut', node_ids)
    
    def paste_nodes(self, target_parent_id: str, 
                   nodes_registry: Dict[str, Any]) -> List[str]:
        """
        Pegar nodos desde el portapapeles
        
        Args:
            target_parent_id: ID del padre de destino
            nodes_registry: Registro de nodos
            
        Returns:
            Lista de IDs de nodos pegados/movidos
        """
        if self.data.is_empty():
            logger.warning("Intento de pegar con portapapeles vacío")
            return []
        
        if target_parent_id not in nodes_registry:
            logger.error(f"Padre de destino {target_parent_id} no existe")
            return []
        
        # Validar que el destino no sea descendiente de los nodos a pegar
        if not self._validate_paste_target(target_parent_id, nodes_registry):
            logger.error("No se puede pegar: el destino es descendiente de los nodos a pegar")
            return []
        
        pasted_ids = []
        
        if self.data.is_copy_operation():
            # Operación de copia: duplicar nodos
            pasted_ids = self._duplicate_nodes(target_parent_id, nodes_registry)
        elif self.data.is_cut_operation():
            # Operación de corte: mover nodos
            pasted_ids = self._move_nodes(target_parent_id, nodes_registry)
            # Limpiar portapapeles después de mover
            self.clear()
        
        logger.info(f"Pegados {len(pasted_ids)} nodos en {target_parent_id}")
        self._notify_listeners('paste', pasted_ids)
        
        return pasted_ids
    
    def _duplicate_nodes(self, target_parent_id: str, 
                        nodes_registry: Dict[str, Any]) -> List[str]:
        """
        Duplicar nodos para operación de copia
        
        Args:
            target_parent_id: ID del padre de destino
            nodes_registry: Registro de nodos
            
        Returns:
            Lista de IDs de nodos duplicados
        """
        # Esta función será implementada cuando tengamos NodeDuplicator
        # Por ahora, placeholder
        logger.info("Duplicación de nodos - placeholder")
        return []
    
    def _move_nodes(self, target_parent_id: str, 
                   nodes_registry: Dict[str, Any]) -> List[str]:
        """
        Mover nodos para operación de corte
        
        Args:
            target_parent_id: ID del padre de destino
            nodes_registry: Registro de nodos
            
        Returns:
            Lista de IDs de nodos movidos
        """
        moved_ids = []
        
        for node_id in self.data.node_ids:
            if node_id in nodes_registry:
                node = nodes_registry[node_id]
                
                # Remover del padre actual
                if node.parent_id and node.parent_id in nodes_registry:
                    current_parent = nodes_registry[node.parent_id]
                    current_parent.remove_child(node_id)
                
                # Agregar al nuevo padre
                node.parent_id = target_parent_id
                target_parent = nodes_registry[target_parent_id]
                target_parent.add_child(node_id)
                
                moved_ids.append(node_id)
                
                logger.debug(f"Movido nodo {node_id} a {target_parent_id}")
        
        return moved_ids
    
    def _validate_paste_target(self, target_parent_id: str, 
                              nodes_registry: Dict[str, Any]) -> bool:
        """
        Validar que el destino no sea descendiente de los nodos a pegar
        
        Args:
            target_parent_id: ID del padre de destino
            nodes_registry: Registro de nodos
            
        Returns:
            True si es válido, False si no
        """
        # Verificar que el destino no sea descendiente de ningún nodo a pegar
        for node_id in self.data.node_ids:
            if self._is_descendant(target_parent_id, node_id, nodes_registry):
                return False
        
        # Verificar que el destino no sea uno de los nodos a pegar
        if target_parent_id in self.data.node_ids:
            return False
        
        return True
    
    def _is_descendant(self, potential_descendant: str, 
                      ancestor: str, 
                      nodes_registry: Dict[str, Any]) -> bool:
        """
        Verificar si un nodo es descendiente de otro
        
        Args:
            potential_descendant: ID del posible descendiente
            ancestor: ID del ancestro
            nodes_registry: Registro de nodos
            
        Returns:
            True si es descendiente, False si no
        """
        current_id = potential_descendant
        
        while current_id and current_id in nodes_registry:
            if current_id == ancestor:
                return True
            current_id = nodes_registry[current_id].parent_id
        
        return False
    
    def can_paste_to(self, target_parent_id: str, 
                    nodes_registry: Dict[str, Any]) -> bool:
        """
        Verificar si se puede pegar en un destino específico
        
        Args:
            target_parent_id: ID del padre de destino
            nodes_registry: Registro de nodos
            
        Returns:
            True si se puede pegar, False si no
        """
        if self.data.is_empty():
            return False
        
        if target_parent_id not in nodes_registry:
            return False
        
        target_parent = nodes_registry[target_parent_id]
        if not target_parent.is_folder:
            return False
        
        return self._validate_paste_target(target_parent_id, nodes_registry)
    
    def get_preview_text(self, nodes_registry: Dict[str, Any]) -> str:
        """
        Obtener texto descriptivo del contenido del portapapeles
        
        Args:
            nodes_registry: Registro de nodos
            
        Returns:
            Descripción del contenido
        """
        if self.data.is_empty():
            return "Portapapeles vacío"
        
        count = self.data.get_count()
        operation = "Copiar" if self.data.is_copy_operation() else "Mover"
        
        if count == 1:
            node_id = self.data.node_ids[0]
            if node_id in nodes_registry:
                node_name = nodes_registry[node_id].name
                return f"{operation}: {node_name}"
            else:
                return f"{operation}: 1 elemento"
        else:
            return f"{operation}: {count} elementos"
    
    def get_node_names(self, nodes_registry: Dict[str, Any]) -> List[str]:
        """
        Obtener nombres de los nodos en el portapapeles
        
        Args:
            nodes_registry: Registro de nodos
            
        Returns:
            Lista de nombres de nodos
        """
        names = []
        for node_id in self.data.node_ids:
            if node_id in nodes_registry:
                names.append(nodes_registry[node_id].name)
        return names
    
    def clear(self):
        """Limpiar el portapapeles"""
        old_count = self.data.get_count()
        self.data.clear()
        
        if old_count > 0:
            logger.info("Portapapeles limpiado")
            self._notify_listeners('clear', [])
    
    def is_empty(self) -> bool:
        """Verificar si el portapapeles está vacío"""
        return self.data.is_empty()
    
    def get_mode(self) -> ClipboardMode:
        """Obtener modo actual del portapapeles"""
        return self.data.mode
    
    def get_node_ids(self) -> List[str]:
        """Obtener lista de IDs de nodos en el portapapeles"""
        return self.data.node_ids.copy()
    
    def get_count(self) -> int:
        """Obtener cantidad de nodos en el portapapeles"""
        return self.data.get_count()
    
    def add_listener(self, listener: callable):
        """
        Agregar listener para eventos del portapapeles
        
        Args:
            listener: Función que recibe (evento, node_ids)
        """
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener: callable):
        """
        Remover listener de eventos del portapapeles
        
        Args:
            listener: Función a remover
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _notify_listeners(self, event: str, node_ids: List[str]):
        """
        Notificar a listeners sobre eventos del portapapeles
        
        Args:
            event: Tipo de evento ('copy', 'cut', 'paste', 'clear')
            node_ids: Lista de IDs de nodos involucrados
        """
        for listener in self._listeners:
            try:
                listener(event, node_ids)
            except Exception as e:
                logger.error(f"Error en listener del portapapeles: {e}")
    
    def get_statistics(self, nodes_registry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtener estadísticas del contenido del portapapeles
        
        Args:
            nodes_registry: Registro de nodos
            
        Returns:
            Diccionario con estadísticas
        """
        if self.data.is_empty():
            return {
                "total": 0,
                "files": 0,
                "folders": 0,
                "mode": "none"
            }
        
        stats = {
            "total": 0,
            "files": 0,
            "folders": 0,
            "mode": self.data.mode.value,
            "timestamp": self.data.timestamp
        }
        
        for node_id in self.data.node_ids:
            if node_id in nodes_registry:
                node = nodes_registry[node_id]
                stats["total"] += 1
                
                if node.is_file:
                    stats["files"] += 1
                else:
                    stats["folders"] += 1
        
        return stats
    
    def __str__(self) -> str:
        """Representación string del portapapeles"""
        if self.data.is_empty():
            return "NodeClipboard(empty)"
        
        mode = self.data.mode.value
        count = self.data.get_count()
        return f"NodeClipboard(mode={mode}, count={count})"