#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Selección Múltiple para TreeApp v4 Pro
Gestión de selecciones de nodos individuales, múltiples y por rango
"""

from typing import Set, Optional, List, Dict, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class NodeSelection:
    """Información de selección para operaciones múltiples"""
    selected_ids: Set[str] = field(default_factory=set)
    primary_selection: Optional[str] = None  # Nodo principal en la selección
    selection_type: str = "single"  # "single", "multiple", "range"
    
    def add_node(self, node_id: str, is_primary: bool = False):
        """Agregar nodo a la selección"""
        self.selected_ids.add(node_id)
        if is_primary or not self.primary_selection:
            self.primary_selection = node_id
        self.selection_type = "multiple" if len(self.selected_ids) > 1 else "single"
    
    def remove_node(self, node_id: str):
        """Remover nodo de la selección"""
        self.selected_ids.discard(node_id)
        if self.primary_selection == node_id:
            self.primary_selection = next(iter(self.selected_ids), None)
        self.selection_type = "multiple" if len(self.selected_ids) > 1 else "single"
    
    def clear(self):
        """Limpiar selección"""
        self.selected_ids.clear()
        self.primary_selection = None
        self.selection_type = "single"
    
    def is_selected(self, node_id: str) -> bool:
        """Verificar si un nodo está seleccionado"""
        return node_id in self.selected_ids
    
    def get_selected_list(self) -> List[str]:
        """Obtener lista de IDs seleccionados"""
        return list(self.selected_ids)
    
    def get_count(self) -> int:
        """Obtener cantidad de nodos seleccionados"""
        return len(self.selected_ids)
    
    def has_selection(self) -> bool:
        """Verificar si hay alguna selección"""
        return len(self.selected_ids) > 0

class MultiNodeSelector:
    """
    Gestor para selección múltiple de nodos
    """
    
    def __init__(self):
        self.selection = NodeSelection()
    
    def select_single_node(self, node_id: str):
        """Seleccionar un solo nodo"""
        self.selection.clear()
        self.selection.add_node(node_id, is_primary=True)
        logger.debug(f"Seleccionado nodo único: {node_id}")
    
    def add_to_selection(self, node_id: str, is_primary: bool = False):
        """Agregar nodo a selección múltiple"""
        self.selection.add_node(node_id, is_primary)
        logger.debug(f"Agregado a selección: {node_id}")
    
    def remove_from_selection(self, node_id: str):
        """Remover nodo de la selección"""
        self.selection.remove_node(node_id)
        logger.debug(f"Removido de selección: {node_id}")
    
    def toggle_selection(self, node_id: str):
        """Alternar selección de un nodo"""
        if self.selection.is_selected(node_id):
            self.remove_from_selection(node_id)
        else:
            self.add_to_selection(node_id)
    
    def select_range(self, start_node_id: str, end_node_id: str, 
                    nodes_registry: Dict[str, Any]):
        """
        Seleccionar rango de nodos entre dos nodos hermanos
        
        Args:
            start_node_id: ID del nodo inicial
            end_node_id: ID del nodo final
            nodes_registry: Registro de nodos
        """
        if start_node_id not in nodes_registry or end_node_id not in nodes_registry:
            logger.warning("Nodos no encontrados para selección de rango")
            return
        
        start_node = nodes_registry[start_node_id]
        end_node = nodes_registry[end_node_id]
        
        # Verificar que son hermanos
        if start_node.parent_id != end_node.parent_id:
            logger.warning("Los nodos no son hermanos, no se puede seleccionar rango")
            return
        
        # Obtener lista de hermanos
        if start_node.parent_id and start_node.parent_id in nodes_registry:
            parent = nodes_registry[start_node.parent_id]
            siblings_ids = parent.children_ids
        else:
            # Nodos raíz
            siblings_ids = [node_id for node_id, node in nodes_registry.items() 
                          if node.parent_id is None]
        
        # Encontrar índices de inicio y fin
        try:
            start_idx = siblings_ids.index(start_node_id)
            end_idx = siblings_ids.index(end_node_id)
        except ValueError:
            logger.error("No se encontraron los nodos en la lista de hermanos")
            return
        
        # Asegurar orden correcto
        min_idx, max_idx = min(start_idx, end_idx), max(start_idx, end_idx)
        
        # Seleccionar rango
        self.selection.clear()
        self.selection.selection_type = "range"
        for i in range(min_idx, max_idx + 1):
            node_id = siblings_ids[i]
            self.selection.add_node(node_id, is_primary=(i == start_idx))
        
        logger.info(f"Seleccionado rango: {max_idx - min_idx + 1} nodos")
    
    def select_branch(self, root_node_id: str, nodes_registry: Dict[str, Any]):
        """
        Seleccionar rama completa (nodo y todos sus descendientes)
        
        Args:
            root_node_id: ID del nodo raíz de la rama
            nodes_registry: Registro de nodos
        """
        if root_node_id not in nodes_registry:
            logger.warning(f"Nodo raíz {root_node_id} no encontrado")
            return
        
        self.selection.clear()
        self.selection.add_node(root_node_id, is_primary=True)
        
        # Agregar todos los descendientes
        def add_descendants(node_id: str):
            if node_id in nodes_registry:
                node = nodes_registry[node_id]
                for child_id in node.children_ids:
                    if child_id in nodes_registry:
                        self.selection.add_node(child_id)
                        add_descendants(child_id)
        
        add_descendants(root_node_id)
        logger.info(f"Seleccionada rama con {len(self.selection.selected_ids)} nodos")
    
    def select_all_children(self, parent_node_id: str, nodes_registry: Dict[str, Any]):
        """
        Seleccionar todos los hijos directos de un nodo
        
        Args:
            parent_node_id: ID del nodo padre
            nodes_registry: Registro de nodos
        """
        if parent_node_id not in nodes_registry:
            logger.warning(f"Nodo padre {parent_node_id} no encontrado")
            return
        
        parent_node = nodes_registry[parent_node_id]
        
        self.selection.clear()
        for child_id in parent_node.children_ids:
            if child_id in nodes_registry:
                self.selection.add_node(child_id)
        
        logger.info(f"Seleccionados {len(self.selection.selected_ids)} hijos de {parent_node_id}")
    
    def select_by_type(self, node_type: str, nodes_registry: Dict[str, Any], 
                      parent_id: Optional[str] = None):
        """
        Seleccionar nodos por tipo (archivos o carpetas)
        
        Args:
            node_type: Tipo de nodo ("file" o "folder")
            nodes_registry: Registro de nodos
            parent_id: ID del padre (None para todo el árbol)
        """
        self.selection.clear()
        
        nodes_to_check = []
        
        if parent_id:
            # Solo verificar descendientes del padre especificado
            if parent_id in nodes_registry:
                parent_node = nodes_registry[parent_id]
                
                def collect_descendants(node_id: str):
                    if node_id in nodes_registry:
                        nodes_to_check.append(nodes_registry[node_id])
                        node = nodes_registry[node_id]
                        for child_id in node.children_ids:
                            collect_descendants(child_id)
                
                collect_descendants(parent_id)
        else:
            # Verificar todos los nodos
            nodes_to_check = list(nodes_registry.values())
        
        # Seleccionar nodos del tipo especificado
        count = 0
        for node in nodes_to_check:
            if node.type.value == node_type:
                self.selection.add_node(node.id)
                count += 1
        
        logger.info(f"Seleccionados {count} nodos de tipo {node_type}")
    
    def select_by_status(self, status: str, nodes_registry: Dict[str, Any]):
        """
        Seleccionar nodos por estado
        
        Args:
            status: Estado a seleccionar (✅, ⬜, ❌, "")
            nodes_registry: Registro de nodos
        """
        self.selection.clear()
        
        count = 0
        for node in nodes_registry.values():
            if node.status.value == status:
                self.selection.add_node(node.id)
                count += 1
        
        logger.info(f"Seleccionados {count} nodos con estado {status}")
    
    def invert_selection(self, nodes_registry: Dict[str, Any]):
        """
        Invertir selección actual
        
        Args:
            nodes_registry: Registro de nodos
        """
        current_selection = self.selection.selected_ids.copy()
        self.selection.clear()
        
        for node_id in nodes_registry.keys():
            if node_id not in current_selection:
                self.selection.add_node(node_id)
        
        logger.info(f"Selección invertida: {len(self.selection.selected_ids)} nodos")
    
    def get_selection(self) -> NodeSelection:
        """Obtener selección actual"""
        return self.selection
    
    def clear_selection(self):
        """Limpiar selección"""
        self.selection.clear()
        logger.debug("Selección limpiada")
    
    def is_node_selected(self, node_id: str) -> bool:
        """Verificar si un nodo está seleccionado"""
        return self.selection.is_selected(node_id)
    
    def get_selected_nodes(self, nodes_registry: Dict[str, Any]) -> List[Any]:
        """
        Obtener lista de nodos seleccionados
        
        Args:
            nodes_registry: Registro de nodos
            
        Returns:
            Lista de nodos seleccionados
        """
        return [nodes_registry[node_id] for node_id in self.selection.selected_ids 
                if node_id in nodes_registry]
    
    def get_primary_selected_node(self, nodes_registry: Dict[str, Any]) -> Optional[Any]:
        """
        Obtener nodo principal seleccionado
        
        Args:
            nodes_registry: Registro de nodos
            
        Returns:
            Nodo principal seleccionado o None
        """
        if self.selection.primary_selection and self.selection.primary_selection in nodes_registry:
            return nodes_registry[self.selection.primary_selection]
        return None
    
    def get_selection_statistics(self, nodes_registry: Dict[str, Any]) -> Dict[str, int]:
        """
        Obtener estadísticas de la selección actual
        
        Args:
            nodes_registry: Registro de nodos
            
        Returns:
            Diccionario con estadísticas
        """
        stats = {
            "total": 0,
            "files": 0,
            "folders": 0,
            "completed": 0,
            "in_progress": 0,
            "pending": 0
        }
        
        for node_id in self.selection.selected_ids:
            if node_id in nodes_registry:
                node = nodes_registry[node_id]
                stats["total"] += 1
                
                if node.type.value == "file":
                    stats["files"] += 1
                else:
                    stats["folders"] += 1
                
                if node.status.value == "✅":
                    stats["completed"] += 1
                elif node.status.value == "⬜":
                    stats["in_progress"] += 1
                elif node.status.value == "❌":
                    stats["pending"] += 1
        
        return stats
    
    def filter_selection_by_predicate(self, predicate_func: callable, 
                                    nodes_registry: Dict[str, Any]):
        """
        Filtrar selección actual usando un predicado
        
        Args:
            predicate_func: Función que retorna True para nodos que deben mantenerse
            nodes_registry: Registro de nodos
        """
        filtered_ids = set()
        
        for node_id in self.selection.selected_ids:
            if node_id in nodes_registry:
                node = nodes_registry[node_id]
                if predicate_func(node):
                    filtered_ids.add(node_id)
        
        # Actualizar selección
        original_count = len(self.selection.selected_ids)
        self.selection.selected_ids = filtered_ids
        
        # Verificar si el nodo principal sigue seleccionado
        if (self.selection.primary_selection and 
            self.selection.primary_selection not in filtered_ids):
            self.selection.primary_selection = next(iter(filtered_ids), None)
        
        # Actualizar tipo de selección
        self.selection.selection_type = "multiple" if len(filtered_ids) > 1 else "single"
        
        filtered_count = len(filtered_ids)
        logger.info(f"Selección filtrada: {original_count} -> {filtered_count} nodos")
    
    def __str__(self) -> str:
        """Representación string de la selección"""
        count = self.selection.get_count()
        return f"MultiNodeSelector(selected={count}, type={self.selection.selection_type})"