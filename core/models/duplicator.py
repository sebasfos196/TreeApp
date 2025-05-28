#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Duplicación para TreeApp v4 Pro
Gestión de duplicación de nodos individuales, ramas completas y operaciones múltiples
Integrado con las mejoras de node.py (deepcopy, from_str, etc.)
"""

import uuid
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class NodeDuplicator:
    """
    Gestor para duplicación avanzada de nodos y ramas
    Integrado con las nuevas capacidades de Node (deepcopy, validaciones robustas)
    """
    
    @staticmethod
    def duplicate_single_node(node: Any, 
                            new_name: Optional[str] = None,
                            generate_new_ids: bool = True,
                            include_children_ids: bool = False) -> Any:
        """
        🔥 MEJORADO: Duplicar un solo nodo usando deepcopy() personalizado
        
        Args:
            node: Nodo a duplicar
            new_name: Nuevo nombre (opcional)
            generate_new_ids: Si generar nuevos IDs
            include_children_ids: Si mantener referencias a hijos (para clonación de ramas)
            
        Returns:
            Nodo duplicado
        """
        # 🔥 USAR NUEVO deepcopy() en lugar de clone()
        duplicated = node.deepcopy(
            include_children=include_children_ids,
            generate_new_ids=generate_new_ids
        )
        
        # Aplicar nuevo nombre si se proporciona
        if new_name:
            duplicated.update_name(new_name)
        else:
            # Generar nombre automático más inteligente
            base_name = node.name
            if "(copia)" not in base_name:
                duplicated.update_name(f"{base_name} (copia)")
            else:
                # Si ya tiene "(copia)", agregar número
                import re
                match = re.search(r'\(copia( (\d+))?\)', base_name)
                if match:
                    current_num = int(match.group(2)) if match.group(2) else 1
                    new_name = base_name.replace(match.group(0), f"(copia {current_num + 1})")
                    duplicated.update_name(new_name)
                else:
                    duplicated.update_name(f"{base_name} (copia)")
        
        logger.debug(f"Duplicado nodo individual: {node.id} -> {duplicated.id} "
                    f"(name: '{duplicated.name}')")
        return duplicated
    
    @staticmethod
    def duplicate_branch_recursive(node: Any, 
                                 nodes_registry: Dict[str, Any],
                                 new_name: Optional[str] = None,
                                 id_mapping: Optional[Dict[str, str]] = None,
                                 preserve_structure: bool = True) -> Tuple[Any, Dict[str, str]]:
        """
        🔥 MEJORADO: Duplicar rama completa recursivamente con mejor gestión de IDs
        
        Args:
            node: Nodo raíz de la rama a duplicar
            nodes_registry: Registro de todos los nodos
            new_name: Nuevo nombre para el nodo raíz
            id_mapping: Mapeo de IDs antiguos a nuevos (para tracking)
            preserve_structure: Si preservar la estructura jerárquica original
            
        Returns:
            Tupla con (nodo_duplicado, mapeo_ids_completo)
        """
        if id_mapping is None:
            id_mapping = {}
        
        # 🔥 USAR deepcopy() mejorado
        duplicated_node = NodeDuplicator.duplicate_single_node(
            node, 
            new_name=new_name,
            generate_new_ids=True,
            include_children_ids=False  # Los gestionamos manualmente para control total
        )
        
        id_mapping[node.id] = duplicated_node.id
        
        # Duplicar hijos recursivamente si preservamos estructura
        if preserve_structure:
            new_children_ids = []
            
            for child_id in node.children_ids:
                if child_id in nodes_registry:
                    child_node = nodes_registry[child_id]
                    
                    # Recursión para duplicar hijo
                    duplicated_child, _ = NodeDuplicator.duplicate_branch_recursive(
                        child_node, 
                        nodes_registry, 
                        new_name=None,  # Mantener nombre original para hijos
                        id_mapping=id_mapping,
                        preserve_structure=preserve_structure
                    )
                    
                    # Establecer relación padre-hijo
                    duplicated_child.parent_id = duplicated_node.id
                    new_children_ids.append(duplicated_child.id)
                    
                    # Actualizar mapping
                    id_mapping[child_id] = duplicated_child.id
                    
                    logger.debug(f"Hijo duplicado: {child_id} -> {duplicated_child.id}")
                else:
                    logger.warning(f"Hijo {child_id} no encontrado en registry")
            
            # Asignar nuevos hijos al nodo duplicado
            duplicated_node.children_ids = new_children_ids
        
        logger.info(f"Duplicada rama: {node.id} -> {duplicated_node.id} "
                   f"({len(duplicated_node.children_ids)} hijos directos)")
        
        return duplicated_node, id_mapping
    
    @staticmethod
    def duplicate_multiple_nodes(nodes: List[Any],
                                nodes_registry: Dict[str, Any],
                                target_parent_id: str,
                                preserve_hierarchy: bool = True,
                                auto_resolve_names: bool = True) -> Tuple[List[Any], Dict[str, str]]:
        """
        🔥 MEJORADO: Duplicar múltiples nodos con mejor gestión de jerarquías
        
        Args:
            nodes: Lista de nodos a duplicar
            nodes_registry: Registro de todos los nodos
            target_parent_id: ID del padre de destino
            preserve_hierarchy: Si preservar relaciones jerárquicas
            auto_resolve_names: Si resolver conflictos de nombres automáticamente
            
        Returns:
            Tupla (nodos_duplicados, mapeo_ids)
        """
        duplicated_nodes = []
        global_id_mapping = {}
        
        # Validar nodos antes de duplicar
        valid_nodes = [node for node in nodes if node.id in nodes_registry]
        if len(valid_nodes) != len(nodes):
            logger.warning(f"Algunos nodos no están en registry: "
                         f"{len(nodes) - len(valid_nodes)} nodos ignorados")
        
        # Ordenar nodos por profundidad si preservamos jerarquía (padres antes que hijos)
        if preserve_hierarchy:
            valid_nodes = sorted(valid_nodes, 
                               key=lambda n: len(n.get_path_components(nodes_registry)))
        
        # Obtener nombres existentes en destino para resolución de conflictos
        existing_names = set()
        if auto_resolve_names and target_parent_id in nodes_registry:
            target_parent = nodes_registry[target_parent_id]
            for child_id in target_parent.children_ids:
                if child_id in nodes_registry:
                    existing_names.add(nodes_registry[child_id].name)
        
        for node in valid_nodes:
            # Verificar si ya fue duplicado como parte de una rama
            if node.id in global_id_mapping:
                logger.debug(f"Nodo {node.id} ya duplicado como parte de rama")
                continue
            
            # Resolver conflicto de nombres si es necesario
            new_name = None
            if auto_resolve_names:
                new_name = NodeDuplicator._resolve_name_conflict(
                    node.name, existing_names
                )
                existing_names.add(new_name)
            
            # Decidir tipo de duplicación
            if node.is_folder and preserve_hierarchy and node.has_children:
                # Duplicación recursiva de rama completa
                duplicated, mapping = NodeDuplicator.duplicate_branch_recursive(
                    node, nodes_registry, new_name=new_name, 
                    id_mapping=global_id_mapping
                )
                global_id_mapping.update(mapping)
                
                logger.info(f"Rama duplicada: {node.id} -> {duplicated.id}")
            else:
                # Duplicación simple
                duplicated = NodeDuplicator.duplicate_single_node(
                    node, new_name=new_name
                )
                global_id_mapping[node.id] = duplicated.id
                
                logger.debug(f"Nodo simple duplicado: {node.id} -> {duplicated.id}")
            
            # Establecer nuevo padre
            duplicated.parent_id = target_parent_id
            duplicated_nodes.append(duplicated)
        
        logger.info(f"Duplicación múltiple completada: {len(duplicated_nodes)} nodos, "
                   f"{len(global_id_mapping)} mapeos de ID")
        
        return duplicated_nodes, global_id_mapping
    
    @staticmethod
    def _resolve_name_conflict(original_name: str, existing_names: set) -> str:
        """
        🔥 NUEVO: Resolver conflictos de nombres automáticamente
        
        Args:
            original_name: Nombre original
            existing_names: Set de nombres existentes
            
        Returns:
            Nombre sin conflictos
        """
        if original_name not in existing_names:
            return original_name
        
        # Estrategia: agregar número incremental
        base_name = original_name
        counter = 1
        
        # Si ya tiene formato "(copia X)", extraer base y número
        import re
        copy_pattern = r'^(.+?)\s*\(copia(?:\s+(\d+))?\)$'
        match = re.match(copy_pattern, original_name)
        
        if match:
            base_name = match.group(1).strip()
            counter = int(match.group(2)) if match.group(2) else 1
        
        # Generar nuevo nombre único
        while True:
            if counter == 1:
                candidate = f"{base_name} (copia)"
            else:
                candidate = f"{base_name} (copia {counter})"
            
            if candidate not in existing_names:
                return candidate
            
            counter += 1
            
            # Prevenir bucle infinito
            if counter > 1000:
                import time
                timestamp = str(int(time.time()))
                return f"{base_name} (copia {timestamp})"
    
    @staticmethod
    def duplicate_with_modifications(node: Any,
                                   nodes_registry: Dict[str, Any],
                                   modifications: Dict[str, Any]) -> Any:
        """
        🔥 MEJORADO: Duplicar nodo aplicando modificaciones específicas
        
        Args:
            node: Nodo a duplicar
            nodes_registry: Registro de nodos
            modifications: Diccionario con modificaciones a aplicar
            
        Returns:
            Nodo duplicado con modificaciones
        """
        # Usar deepcopy() mejorado
        duplicated = NodeDuplicator.duplicate_single_node(node)
        
        # Aplicar modificaciones con validación mejorada
        for field, value in modifications.items():
            try:
                if hasattr(duplicated, field):
                    setattr(duplicated, field, value)
                    logger.debug(f"Modificado campo directo: {field} = {value}")
                    
                elif hasattr(duplicated.editor_fields, field):
                    setattr(duplicated.editor_fields, field, value)
                    logger.debug(f"Modificado campo editor: {field} = {value}")
                    
                elif hasattr(duplicated.metadata, field):
                    setattr(duplicated.metadata, field, value)
                    logger.debug(f"Modificado metadato: {field} = {value}")
                    
                else:
                    logger.warning(f"Campo desconocido en modificaciones: {field}")
                    
            except Exception as e:
                logger.error(f"Error aplicando modificación {field}={value}: {e}")
        
        # Actualizar tiempo de modificación
        duplicated.update_modified_time()
        
        logger.info(f"Duplicado con modificaciones: {node.id} -> {duplicated.id} "
                   f"({len(modifications)} cambios)")
        return duplicated
    
    @staticmethod
    def duplicate_as_template(node: Any,
                            template_name: str,
                            clear_content: bool = True,
                            preserve_structure: bool = False) -> Any:
        """
        🔥 MEJORADO: Duplicar nodo como plantilla con más opciones
        
        Args:
            node: Nodo a usar como base
            template_name: Nombre de la plantilla
            clear_content: Si limpiar el contenido
            preserve_structure: Si preservar estructura de carpetas (si es folder)
            
        Returns:
            Nodo plantilla
        """
        # Usar deepcopy() mejorado
        template = NodeDuplicator.duplicate_single_node(
            node, 
            new_name=template_name,
            include_children_ids=preserve_structure
        )
        
        if clear_content:
            # Limpiar contenidos pero mantener estructura básica
            template.editor_fields.markdown_content = f"# {template_name}\n\n[Plantilla basada en {node.name}]"
            template.editor_fields.technical_notes = f"Plantilla creada desde: {node.name}"
            template.editor_fields.code_content = ""
            
            # Resetear metadatos relevantes
            template.metadata.tags = ["plantilla", f"basada-en-{node.type.value}"]
            template.metadata.completion_percentage = 0
            template.metadata.comments = []
            template.metadata.priority = 0
            
            # Limpiar atributos personalizados pero mantener algunos útiles
            useful_attrs = ["original_template_source", "template_type"]
            filtered_attrs = {k: v for k, v in template.metadata.custom_attributes.items() 
                            if k in useful_attrs}
            filtered_attrs["original_template_source"] = node.id
            filtered_attrs["template_type"] = node.type.value
            template.metadata.custom_attributes = filtered_attrs
        
        logger.info(f"Creada plantilla: {template_name} basada en {node.id} "
                   f"(clear_content: {clear_content}, preserve_structure: {preserve_structure})")
        return template
    
    @staticmethod
    def batch_duplicate(nodes: List[Any],
                       naming_pattern: str = "{name} (copia {counter})",
                       target_parent_id: Optional[str] = None,
                       smart_numbering: bool = True) -> List[Any]:
        """
        🔥 MEJORADO: Duplicación en lote con patrones de nombres inteligentes
        
        Args:
            nodes: Lista de nodos a duplicar
            naming_pattern: Patrón para generar nombres
            target_parent_id: ID del padre de destino
            smart_numbering: Si usar numeración inteligente (evitar conflictos)
            
        Returns:
            Lista de nodos duplicados
        """
        duplicated_nodes = []
        name_counters = {}
        used_names = set()
        
        for node in nodes:
            base_name = node.name
            
            # Incrementar contador para este nombre base
            if base_name not in name_counters:
                name_counters[base_name] = 1
            else:
                name_counters[base_name] += 1
            
            # Generar nombre usando patrón
            new_name = naming_pattern.format(
                name=base_name,
                counter=name_counters[base_name],
                type=node.type.value,
                status=node.status.display_text
            )
            
            # Verificar unicidad si smart_numbering está activo
            if smart_numbering:
                original_new_name = new_name
                suffix_counter = 1
                while new_name in used_names:
                    suffix_counter += 1
                    new_name = f"{original_new_name} ({suffix_counter})"
                used_names.add(new_name)
            
            # Duplicar nodo con deepcopy()
            duplicated = NodeDuplicator.duplicate_single_node(node, new_name=new_name)
            
            if target_parent_id:
                duplicated.parent_id = target_parent_id
            
            duplicated_nodes.append(duplicated)
            
            logger.debug(f"Batch duplicate: {node.id} -> {duplicated.id} ('{new_name}')")
        
        logger.info(f"Duplicación en lote completada: {len(duplicated_nodes)} nodos "
                   f"(smart_numbering: {smart_numbering})")
        return duplicated_nodes
    
    @staticmethod
    def duplicate_filtered(nodes: List[Any],
                         filter_func: callable,
                         nodes_registry: Dict[str, Any],
                         apply_filter_to_children: bool = True) -> List[Any]:
        """
        🔥 MEJORADO: Duplicar solo nodos que pasen un filtro con opciones avanzadas
        
        Args:
            nodes: Lista de nodos candidatos
            filter_func: Función que retorna True para nodos a duplicar
            nodes_registry: Registro de nodos
            apply_filter_to_children: Si aplicar filtro también a hijos en ramas
            
        Returns:
            Lista de nodos duplicados que pasaron el filtro
        """
        # Filtrar nodos principales
        filtered_nodes = []
        
        for node in nodes:
            try:
                if filter_func(node):
                    filtered_nodes.append(node)
                    logger.debug(f"Nodo {node.id} pasó filtro")
                else:
                    logger.debug(f"Nodo {node.id} filtrado")
            except Exception as e:
                logger.error(f"Error aplicando filtro a {node.id}: {e}")
        
        # Duplicar nodos filtrados
        duplicated_nodes = []
        for node in filtered_nodes:
            if node.is_folder and node.has_children and apply_filter_to_children:
                # Para carpetas, usar duplicación recursiva con filtro en hijos
                duplicated, _ = NodeDuplicator.duplicate_branch_recursive(
                    node, nodes_registry
                )
                # TODO: Aplicar filtro recursivo a hijos (feature avanzada)
                duplicated_nodes.append(duplicated)
            else:
                # Duplicación simple
                duplicated = NodeDuplicator.duplicate_single_node(node)
                duplicated_nodes.append(duplicated)
        
        logger.info(f"Duplicación filtrada: {len(filtered_nodes)} de {len(nodes)} nodos pasaron filtro")
        return duplicated_nodes

class DuplicationValidator:
    """
    🔥 MEJORADO: Validador para operaciones de duplicación con validaciones más robustas
    """
    
    @staticmethod
    def can_duplicate_to_parent(node_ids: List[str],
                              target_parent_id: str,
                              nodes_registry: Dict[str, Any]) -> Tuple[bool, str]:
        """
        🔥 MEJORADO: Verificar si se pueden duplicar nodos a un padre específico
        
        Args:
            node_ids: Lista de IDs de nodos a duplicar
            target_parent_id: ID del padre de destino
            nodes_registry: Registro de nodos
            
        Returns:
            Tupla (es_posible, mensaje_error_detallado)
        """
        # Validación básica del destino
        if target_parent_id not in nodes_registry:
            return False, f"El destino '{target_parent_id}' no existe en el registro"
        
        target_parent = nodes_registry[target_parent_id]
        if not target_parent.is_folder:
            return False, f"El destino '{target_parent.name}' debe ser una carpeta, no un archivo"
        
        # Validar cada nodo individualmente
        problematic_nodes = []
        
        for node_id in node_ids:
            if node_id not in nodes_registry:
                problematic_nodes.append(f"Nodo '{node_id}' no existe")
                continue
            
            node = nodes_registry[node_id]
            
            # Verificar que no se duplique un nodo dentro de sí mismo o sus descendientes
            if DuplicationValidator._would_create_cycle(node_id, target_parent_id, nodes_registry):
                problematic_nodes.append(f"'{node.name}' crearía un ciclo (duplicar dentro de sí mismo)")
        
        if problematic_nodes:
            error_msg = "Problemas encontrados:\n" + "\n".join(f"• {p}" for p in problematic_nodes)
            return False, error_msg
        
        return True, ""
    
    @staticmethod
    def _would_create_cycle(node_id: str, target_parent_id: str, nodes_registry: Dict[str, Any]) -> bool:
        """
        Verificar si duplicar un nodo crearía un ciclo (nodo dentro de sí mismo)
        
        Args:
            node_id: ID del nodo a duplicar
            target_parent_id: ID del destino
            nodes_registry: Registro de nodos
            
        Returns:
            True si crearía un ciclo
        """
        # Verificar si el destino es el mismo nodo o un descendiente
        current_id = target_parent_id
        visited_ids = set()  # Prevenir bucles infinitos en caso de datos corruptos
        
        while current_id and current_id in nodes_registry:
            if current_id in visited_ids:
                logger.warning(f"Detectado bucle infinito en validación de ciclo: {visited_ids}")
                break
            visited_ids.add(current_id)
            
            if current_id == node_id:
                return True
            
            current_id = nodes_registry[current_id].parent_id
        
        return False
    
    @staticmethod
    def validate_duplication_names(nodes: List[Any],
                                 target_parent: Any,
                                 nodes_registry: Dict[str, Any],
                                 auto_resolve: bool = True) -> List[str]:
        """
        🔥 MEJORADO: Validar y resolver conflictos de nombres en duplicación
        
        Args:
            nodes: Lista de nodos a duplicar
            target_parent: Nodo padre de destino
            nodes_registry: Registro de nodos
            auto_resolve: Si resolver conflictos automáticamente
            
        Returns:
            Lista de nombres sin conflictos (en el mismo orden que nodes)
        """
        # Obtener nombres existentes en el destino
        existing_names = set()
        for child_id in target_parent.children_ids:
            if child_id in nodes_registry:
                existing_names.add(nodes_registry[child_id].name)
        
        resolved_names = []
        used_names = existing_names.copy()  # Track nombres ya resueltos
        
        for node in nodes:
            base_name = node.name
            
            if base_name not in used_names:
                # No hay conflicto
                resolved_names.append(base_name)
                used_names.add(base_name)
            elif auto_resolve:
                # Resolver conflicto automáticamente
                new_name = NodeDuplicator._resolve_name_conflict(base_name, used_names)
                resolved_names.append(new_name)
                used_names.add(new_name)
            else:
                # No resolver, mantener nombre original (podría causar problemas)
                resolved_names.append(base_name)
                logger.warning(f"Conflicto de nombre no resuelto: '{base_name}' ya existe")
        
        return resolved_names
    
    @staticmethod
    def estimate_duplication_size(nodes: List[Any],
                                nodes_registry: Dict[str, Any],
                                include_recursive: bool = True) -> Dict[str, int]:
        """
        🔥 MEJORADO: Estimar el tamaño de una operación de duplicación
        
        Args:
            nodes: Lista de nodos a duplicar
            nodes_registry: Registro de nodos
            include_recursive: Si incluir estimación recursiva para carpetas
            
        Returns:
            Diccionario con estadísticas estimadas detalladas
        """
        stats = {
            "total_nodes": 0,
            "files": 0,
            "folders": 0,
            "max_depth": 0,
            "total_children": 0,
            "estimated_memory_mb": 0,
            "processing_time_estimate_seconds": 0
        }
        
        processed_ids = set()  # Evitar contar duplicados
        
        def count_descendants(node_id: str, depth: int = 0) -> int:
            if node_id in processed_ids or node_id not in nodes_registry:
                return 0
            
            processed_ids.add(node_id)
            count = 1
            stats["max_depth"] = max(stats["max_depth"], depth)
            
            node = nodes_registry[node_id]
            if node.is_file:
                stats["files"] += 1
            else:
                stats["folders"] += 1
            
            # Estimar memoria (aproximado)
            stats["estimated_memory_mb"] += 0.001  # ~1KB por nodo
            
            # Contar hijos si incluimos recursión
            if include_recursive:
                for child_id in node.children_ids:
                    if child_id not in processed_ids:
                        count += count_descendants(child_id, depth + 1)
                        stats["total_children"] += 1
            
            return count
        
        # Procesar todos los nodos
        for node in nodes:
            stats["total_nodes"] += count_descendants(node.id)
        
        # Estimar tiempo de procesamiento (muy aproximado)
        # Basado en: 100 nodos/segundo para operaciones simples
        stats["processing_time_estimate_seconds"] = max(1, stats["total_nodes"] / 100)
        
        logger.info(f"Estimación de duplicación: {stats['total_nodes']} nodos, "
                   f"{stats['estimated_memory_mb']:.2f}MB, "
                   f"~{stats['processing_time_estimate_seconds']}s")
        
        return stats
    
    @staticmethod
    def validate_target_capacity(target_parent_id: str, 
                               estimated_nodes: int,
                               nodes_registry: Dict[str, Any],
                               max_children_per_folder: int = 1000) -> Tuple[bool, str]:
        """
        🔥 NUEVO: Validar que el destino pueda manejar la cantidad de nodos
        
        Args:
            target_parent_id: ID del padre de destino
            estimated_nodes: Cantidad estimada de nodos a agregar
            nodes_registry: Registro de nodos
            max_children_per_folder: Límite máximo de hijos por carpeta
            
        Returns:
            Tupla (es_viable, mensaje_info)
        """
        if target_parent_id not in nodes_registry:
            return False, "Destino no válido"
        
        target_parent = nodes_registry[target_parent_id]
        current_children = len(target_parent.children_ids)
        projected_total = current_children + estimated_nodes
        
        if projected_total > max_children_per_folder:
            return False, (f"El destino tendría {projected_total} hijos "
                          f"(límite: {max_children_per_folder}). "
                          f"Considera crear subcarpetas.")
        
        # Warning si se acerca al límite
        warning_threshold = max_children_per_folder * 0.8
        if projected_total > warning_threshold:
            return True, (f"Advertencia: El destino tendrá {projected_total} hijos "
                         f"(cerca del límite de {max_children_per_folder})")
        
        return True, f"Destino viable: {projected_total} hijos después de duplicación"