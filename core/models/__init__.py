#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Modelos para TreeApp v4 Pro
Exporta todas las clases y funciones principales para fácil importación
"""

# Importaciones principales del modelo de nodos
from .node import (
    Node,
    NodeType,
    NodeStatus,
    EditorFields,
    NodeMetadata,
    INVALID_CHAR_PATTERN
)

# Sistema de portapapeles
from .clipboard import (
    ClipboardData,
    NodeClipboard
)

# Sistema de selección múltiple
from .selection import (
    NodeSelection,
    MultiNodeSelector
)

# Sistema de duplicación
from .duplicator import (
    NodeDuplicator,
    DuplicationValidator
)

# Utilidades y helpers
from .node_utils import (
    # Funciones de creación
    create_file_node,
    create_folder_node,
    create_root_node,
    create_template_node,
    
    # Validadores
    can_paste_nodes,
    validate_node_move,
    validate_node_name,
    
    # Resolución de conflictos
    resolve_name_conflicts,
    resolve_path_conflicts,
    
    # Búsqueda y filtrado
    find_nodes_by_criteria,
    filter_nodes_by_predicate,
    get_nodes_by_depth,
    
    # Estadísticas
    calculate_node_statistics,
    get_completion_statistics,
    
    # Exportación
    prepare_nodes_for_export,
    generate_node_summary,
    
    # Debugging
    validate_tree_integrity,
    print_tree_structure
)

# Versión del módulo
__version__ = "4.0.0"

# Lista de todas las exportaciones públicas
__all__ = [
    # Clases principales
    "Node",
    "NodeType", 
    "NodeStatus",
    "EditorFields",
    "NodeMetadata",
    
    # Sistemas de operaciones
    "NodeClipboard",
    "ClipboardData",
    "MultiNodeSelector", 
    "NodeSelection",
    "NodeDuplicator",
    "DuplicationValidator",
    
    # Funciones de creación
    "create_file_node",
    "create_folder_node", 
    "create_root_node",
    "create_template_node",
    
    # Validadores
    "can_paste_nodes",
    "validate_node_move",
    "validate_node_name",
    
    # Utilidades
    "resolve_name_conflicts",
    "resolve_path_conflicts",
    "find_nodes_by_criteria",
    "filter_nodes_by_predicate",
    "get_nodes_by_depth",
    "calculate_node_statistics",
    "get_completion_statistics",
    "prepare_nodes_for_export",
    "generate_node_summary",
    "validate_tree_integrity",
    "print_tree_structure",
    
    # Constantes
    "INVALID_CHAR_PATTERN"
]

# Información del módulo
def get_module_info():
    """Obtener información sobre el módulo de modelos"""
    return {
        "name": "TreeApp v4 Pro - Models",
        "version": __version__,
        "description": "Sistema completo de modelos para gestión de nodos, selección, duplicación y operaciones avanzadas",
        "components": {
            "node": "Modelo principal de nodos con los 4 campos del editor",
            "clipboard": "Sistema de copy/paste para nodos",
            "selection": "Selección múltiple y operaciones por lotes", 
            "duplicator": "Duplicación avanzada de nodos y ramas",
            "node_utils": "Utilidades, validadores y funciones helper"
        },
        "features": [
            "Modelo completo de nodos con metadatos",
            "4 campos del editor (nombre, markdown, notas técnicas, código)",
            "Sistema de selección múltiple avanzado",
            "Copy/paste entre ramas",
            "Duplicación recursiva de ramas completas",
            "Validaciones robustas",
            "Resolución automática de conflictos",
            "Estadísticas detalladas",
            "Búsqueda y filtrado avanzado",
            "Debugging y validación de integridad"
        ]
    }

# Función de conveniencia para testing
def run_integrity_tests(nodes_registry):
    """
    Ejecutar tests de integridad en un registro de nodos
    
    Args:
        nodes_registry: Diccionario de nodos para validar
        
    Returns:
        Diccionario con resultados de los tests
    """
    results = {
        "tree_integrity": validate_tree_integrity(nodes_registry),
        "statistics": calculate_node_statistics(nodes_registry),
        "completion": get_completion_statistics(nodes_registry),
        "total_nodes": len(nodes_registry)
    }
    
    results["is_valid"] = len(results["tree_integrity"]) == 0
    
    return results