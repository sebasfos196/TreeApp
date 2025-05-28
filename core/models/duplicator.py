#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Duplicación para TreeApp v4 Pro
Gestión de duplicación de nodos individuales, ramas completas y operaciones múltiples
"""

import uuid
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class NodeDuplicator:
    """
    Gestor para duplicación avanzada de nodos y ramas
    """
    
    @staticmethod
    def duplicate_single_node(node: Any, 
                            new_name: Optional[str] = None,
                            generate_new_ids: bool = True) -> Any:
        """
        Duplicar un solo nodo
        
        Args:
            node: Nodo a duplicar
            new_name: Nuevo nombre (opcional)
            generate_new_ids: Si generar nuevos IDs
            
        Returns:
            Nodo duplicado
        """
        duplicated = node.clone(new_name, include_children=False)
        
        if generate_new_ids:
            duplicated.id = str(uuid.uuid4())
        
        logger.debug(f"Duplicado nodo individual: {node.id} -> {duplicated.id}")
        return duplicated
    
    @staticmethod
    def duplicate_branch_recursive(node: Any, 
                                 nodes_registry: Dict[str, Any],
                                 new_name: Optional[str] = None,
                                 id_mapping: Optional[Dict[str, str]] = None) -> Tuple[Any, Dict[str, str]]:
        """
        Duplicar rama completa recursivamente
        
        Args:
            node: Nodo raíz de la rama a duplicar
            nodes_registry: Registro de todos los nodos
            new_name: Nuevo nombre para el nodo raíz
            id_mapping: Mapeo de IDs antiguos a nuevos (para tracking)
            
        Returns:
            Tupla con (nodo_duplicado, mapeo_ids)
        """
        if id_mapping is None:
            id_mapping = {}
        
        # Duplicar el nodo actual
        duplicated_node = NodeDuplicator.duplicate_single_node(node, new_name)
        id_mapping[node.id] = duplicated_node.id
        
        # Duplicar hijos recursivamente
        new_children_ids = []
        for child_id in node.children_ids:
            if child_id in nodes_registry:
                child_node = nodes_registry[child_id]
                duplicated_child, _ = NodeDuplicator.duplicate_branch_recursive(
                    child_node, nodes_registry, id_mapping=id_mapping
                )
                duplicated_child.parent_id = duplicated_node.id
                new_children_ids.append(duplicated_child.id)
                id_mapping[child_id] = duplicated_child.id
        
        duplicated_node.children_ids = new_children_ids
        
        logger.info(f"Duplicada rama: {node.id} -> {duplicated_node.id} "
                   f"({len(new_children_ids)} hijos)")
        
        return duplicated_node, id_mapping
    
    @staticmethod
    def duplicate_multiple_nodes(nodes: List[Any],
                                nodes_registry: Dict[str, Any],
                                target_parent_id: str,
                                preserve_hierarchy: bool = True) -> List[Any]:
        """
        Duplicar múltiples nodos preservando jerarquía
        
        Args:
            nodes: Lista de nodos a duplicar
            nodes_registry: Registro de todos los nodos
            target_parent_id: ID del padre de destino
            preserve_hierarchy: Si preservar relaciones jerárquicas
            
        Returns:
            Lista de nodos duplicados
        """
        duplicated_nodes = []
        id_mapping = {}
        
        # Ordenar nodos por profundidad (padres antes que hijos)
        if preserve_hierarchy:
            nodes = sorted(nodes, key=lambda n: len(n.get_path_components(nodes_registry)))
        
        for node in nodes:
            # Verificar si ya fue duplicado como parte de una rama
            if node.id in id_mapping:
                continue
            
            # Si es una rama completa, duplicar recursivamente
            if node.is_folder and preserve_hierarchy:
                duplicated, mapping = NodeDuplicator.duplicate_branch_recursive(
                    node, nodes_registry, id_mapping=id_mapping
                )
                id_mapping.update(mapping)
            else:
                duplicated = NodeDuplicator.duplicate_single_node(node)
                id_mapping[node.id] = duplicated.id
            
            duplicated.parent_id = target_parent_id
            duplicated_nodes.append(duplicated)
        
        logger.info(f"Duplicados {len(duplicated_nodes)} nodos múltiples")
        return duplicated_nodes
    
    @staticmethod
    def duplicate_with_modifications(node: Any,
                                   nodes_registry: Dict[str, Any],
                                   modifications: Dict[str, Any]) -> Any:
        """
        Duplicar nodo aplicando modificaciones específicas
        
        Args:
            node: Nodo a duplicar
            nodes_registry: Registro de nodos
            modifications: Diccionario con modificaciones a aplicar
            
        Returns:
            Nodo duplicado con modificaciones
        """
        duplicated = NodeDuplicator.duplicate_single_node(node)
        
        # Aplicar modificaciones
        for field, value in modifications.items():
            if hasattr(duplicated, field):
                setattr(duplicated, field, value)
            elif hasattr(duplicated.editor_fields, field):
                setattr(duplicated.editor_fields, field, value)
            elif hasattr(duplicated.metadata, field):
                setattr(duplicated.metadata, field, value)
        
        logger.debug(f"Duplicado con modificaciones: {node.id} -> {duplicated.id}")
        return duplicated
    
    @staticmethod
    def duplicate_as_template(node: Any,
                            template_name: str,
                            clear_content: bool = True) -> Any:
        """
        Duplicar nodo como plantilla
        
        Args:
            node: Nodo a usar como base
            template_name: Nombre de la plantilla
            clear_content: Si limpiar el contenido
            
        Returns:
            Nodo plantilla
        """
        template = NodeDuplicator.duplicate_single_node(node, new_name=template_name)
        
        if clear_content:
            # Limpiar contenidos pero mantener estructura
            template.editor_fields.markdown_content = f"# {template_name}\n\n"
            template.editor_fields.technical_notes = ""
            template.editor_fields.code_content = ""
            
            # Resetear metadatos
            template.metadata.tags = ["plantilla"]
            template.metadata.completion_percentage = 0
            template.metadata.comments = []
        
        logger.info(f"Creada plantilla: {template_name} basada en {node.id}")
        return template
    
    @staticmethod
    def batch_duplicate(nodes: List[Any],
                       naming_pattern: str = "{name} (copia {counter})",
                       target_parent_id: Optional[str] = None) -> List[Any]:
        """
        Duplicación en lote con patrón de nombres
        
        Args:
            nodes: Lista de nodos a duplicar
            naming_pattern: Patrón para generar nombres
            target_parent_id: ID del padre de destino
            
        Returns:
            Lista de nodos duplicados
        """
        duplicated_nodes = []
        name_counters = {}
        
        for node in nodes:
            # Generar nombre único
            base_name = node.name
            if base_name not in name_counters:
                name_counters[base_name] = 1
            else:
                name_counters[base_name] += 1
            
            new_name = naming_pattern.format(
                name=base_name,
                counter=name_counters[base_name]
            )
            
            # Duplicar nodo
            duplicated = NodeDuplicator.duplicate_single_node(node, new_name)
            
            if target_parent_id:
                duplicated.parent_id = target_parent_id
            
            duplicated_nodes.append(duplicated)
        
        logger.info(f"Duplicación en lote completada: {len(duplicated_nodes)} nodos")
        return duplicated_nodes
    
    @staticmethod
    def duplicate_filtered(nodes: List[Any],
                         filter_func: callable,
                         nodes_registry: Dict[str, Any]) -> List[Any]:
        """
        Duplicar solo nodos que pasen un filtro
        
        Args:
            nodes: Lista de nodos candidatos
            filter_func: Función que retorna True para nodos a duplicar
            nodes_registry: Registro de nodos
            
        Returns:
            Lista de nodos duplicados que pasaron el filtro
        """
        filtered_nodes = [node for node in nodes if filter_func(node)]
        
        duplicated_nodes = []
        for node in filtered_nodes:
            duplicated = NodeDuplicator.duplicate_single_node(node)
            duplicated_nodes.append(duplicated)
        
        logger.info(f"Duplicación filtrada: {len(filtered_nodes)} de {len(nodes)} nodos")
        return duplicated_nodes

class DuplicationValidator:
    """
    Validador para operaciones de duplicación
    """
    
    @staticmethod
    def can_duplicate_to_parent(node_ids: List[str],
                              target_parent_id: str,
                              nodes_registry: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verificar si se pueden duplicar nodos a un padre específico
        
        Args:
            node_ids: Lista de IDs de nodos a duplicar
            target_parent_id: ID del padre de destino
            nodes_registry: Registro de nodos
            
        Returns:
            Tupla (es_posible, mensaje_error)
        """
        if target_parent_id not in nodes_registry:
            return False, "El destino no existe"
        
        target_parent = nodes_registry[target_parent_id]
        if not target_parent.is_folder:
            return False, "El destino debe ser una carpeta"
        
        # Verificar que no se duplique un nodo dentro de sí mismo
        for node_id in node_ids:
            if node_id not in nodes_registry:
                continue
            
            # Verificar si el destino es descendiente del nodo a duplicar
            current_id = target_parent_id
            while current_id and current_id in nodes_registry:
                if current_id == node_id:
                    return False, f"No se puede duplicar el nodo {node_id} dentro de sí mismo"
                current_id = nodes_registry[current_id].parent_id
        
        return True, ""
    
    @staticmethod
    def validate_duplication_names(nodes: List[Any],
                                 target_parent: Any,
                                 nodes_registry: Dict[str, Any]) -> List[str]:
        """
        Validar y resolver conflictos de nombres en duplicación
        
        Args:
            nodes: Lista de nodos a duplicar
            target_parent: Nodo padre de destino
            nodes_registry: Registro de nodos
            
        Returns:
            Lista de nombres sin conflictos
        """
        existing_names = set()
        
        # Obtener nombres existentes en el destino
        for child_id in target_parent.children_ids:
            if child_id in nodes_registry:
                existing_names.add(nodes_registry[child_id].name)
        
        resolved_names = []
        
        for node in nodes:
            base_name = node.name
            if base_name not in existing_names:
                resolved_names.append(base_name)
                existing_names.add(base_name)
            else:
                # Generar nuevo nombre
                counter = 1
                new_name = f"{base_name} (copia)"
                while new_name in existing_names:
                    counter += 1
                    new_name = f"{base_name} (copia {counter})"
                
                resolved_names.append(new_name)
                existing_names.add(new_name)
        
        return resolved_names
    
    @staticmethod
    def estimate_duplication_size(nodes: List[Any],
                                nodes_registry: Dict[str, Any]) -> Dict[str, int]:
        """
        Estimar el tamaño de una operación de duplicación
        
        Args:
            nodes: Lista de nodos a duplicar
            nodes_registry: Registro de nodos
            
        Returns:
            Diccionario con estadísticas estimadas
        """
        stats = {
            "total_nodes": 0,
            "files": 0,
            "folders": 0,
            "max_depth": 0,
            "total_children": 0
        }
        
        def count_descendants(node_id: str, depth: int = 0) -> int:
            count = 1
            stats["max_depth"] = max(stats["max_depth"], depth)
            
            if node_id in nodes_registry:
                node = nodes_registry[node_id]
                if node.is_file:
                    stats["files"] += 1
                else:
                    stats["folders"] += 1
                
                for child_id in node.children_ids:
                    count += count_descendants(child_id, depth + 1)
                    stats["total_children"] += 1
            
            return count
        
        for node in nodes:
            stats["total_nodes"] += count_descendants(node.id)
        
        return stats