#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades y Helpers para TreeApp v4 Pro
Funciones de conveniencia, validadores y operaciones auxiliares para nodos
"""

from typing import Dict, List, Optional, Tuple, Any
import logging

from core.models.node import Node, NodeType, NodeStatus, EditorFields, NodeMetadata
from core.models.clipboard import ClipboardData

logger = logging.getLogger(__name__)

# ==================================================================================
# FUNCIONES DE CREACIÓN DE NODOS
# ==================================================================================

def create_file_node(name: str, 
                    parent_id: Optional[str] = None,
                    markdown_content: str = "",
                    technical_notes: str = "",
                    code_content: str = "") -> Node:
    """
    Función de conveniencia para crear un nodo archivo
    
    Args:
        name: Nombre del archivo
        parent_id: ID del padre
        markdown_content: Contenido markdown inicial
        technical_notes: Notas técnicas iniciales
        code_content: Código inicial
        
    Returns:
        Nuevo nodo archivo
    """
    editor_fields = EditorFields(
        name=name,
        markdown_content=markdown_content or f"# {name}\n\nContenido del archivo...",
        technical_notes=technical_notes,
        code_content=code_content
    )
    
    return Node(
        name=name,
        node_type=NodeType.FILE,
        parent_id=parent_id,
        editor_fields=editor_fields
    )

def create_folder_node(name: str,
                      parent_id: Optional[str] = None,
                      technical_notes: str = "") -> Node:
    """
    Función de conveniencia para crear un nodo carpeta
    
    Args:
        name: Nombre de la carpeta
        parent_id: ID del padre
        technical_notes: Notas técnicas iniciales
        
    Returns:
        Nuevo nodo carpeta
    """
    editor_fields = EditorFields(
        name=name,
        markdown_content=f"# {name}\n\nDescripción de la carpeta...",
        technical_notes=technical_notes,
        code_content=""
    )
    
    return Node(
        name=name,
        node_type=NodeType.FOLDER,
        parent_id=parent_id,
        editor_fields=editor_fields
    )

def create_root_node(project_name: str = "Root") -> Node:
    """
    Crear nodo raíz del proyecto
    
    Args:
        project_name: Nombre del proyecto
        
    Returns:
        Nodo raíz
    """
    editor_fields = EditorFields(
        name=project_name,
        markdown_content=f"# {project_name}\n\nProyecto principal...",
        technical_notes="Carpeta raíz del proyecto",
        code_content=""
    )
    
    return Node(
        name=project_name,
        node_type=NodeType.FOLDER,
        node_id="root",
        editor_fields=editor_fields
    )

def create_template_node(template_type: str, name: str) -> Node:
    """
    Crear nodo basado en plantilla predefinida
    
    Args:
        template_type: Tipo de plantilla ("readme", "config", "script", etc.)
        name: Nombre del nodo
        
    Returns:
        Nodo basado en plantilla
    """
    templates = {
        "readme": {
            "markdown": f"# {name}\n\n## Descripción\n\n## Instalación\n\n## Uso\n\n",
            "notes": "Archivo README principal del proyecto"
        },
        "config": {
            "markdown": f"# {name}\n\nArchivo de configuración",
            "notes": "Configuración del proyecto",
            "code": "{\n  \"version\": \"1.0\",\n  \"name\": \"" + name + "\"\n}"
        },
        "script": {
            "markdown": f"# {name}\n\nScript de automatización",
            "notes": "Script para tareas automatizadas",
            "code": "#!/usr/bin/env python3\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()"
        },
        "documentation": {
            "markdown": f"# {name}\n\n## Índice\n\n## Secciones\n\n",
            "notes": "Documentación técnica"
        }
    }
    
    template = templates.get(template_type, templates["readme"])
    
    editor_fields = EditorFields(
        name=name,
        markdown_content=template.get("markdown", f"# {name}\n\n"),
        technical_notes=template.get("notes", ""),
        code_content=template.get("code", "")
    )
    
    # Determinar tipo de archivo basado en extensión
    node_type = NodeType.FILE if "." in name else NodeType.FOLDER
    
    node = Node(
        name=name,
        node_type=node_type,
        editor_fields=editor_fields
    )
    
    # Agregar tag de plantilla
    node.add_tag(f"plantilla-{template_type}")
    
    return node

# ==================================================================================
# VALIDADORES DE OPERACIONES
# ==================================================================================

def can_paste_nodes(clipboard_data: ClipboardData, 
                   target_parent_id: str,
                   nodes_registry: Dict[str, Node]) -> Tuple[bool, str]:
    """
    Verificar si se pueden pegar nodos en una ubicación
    
    Args:
        clipboard_data: Datos del portapapeles
        target_parent_id: ID del padre de destino
        nodes_registry: Registro de nodos
        
    Returns:
        Tupla (es_posible, mensaje_error)
    """
    if clipboard_data.is_empty():
        return False, "El portapapeles está vacío"
    
    if target_parent_id not in nodes_registry:
        return False, "El destino no existe"
    
    target_parent = nodes_registry[target_parent_id]
    if not target_parent.is_folder:
        return False, "El destino debe ser una carpeta"
    
    # Verificar que no se pegue un nodo dentro de sí mismo
    for node_id in clipboard_data.node_ids:
        if node_id not in nodes_registry:
            continue
        
        # Verificar si el destino es descendiente del nodo a pegar
        current_id = target_parent_id
        while current_id and current_id in nodes_registry:
            if current_id == node_id:
                return False, f"No se puede pegar el nodo {node_id} dentro de sí mismo"
            current_id = nodes_registry[current_id].parent_id
    
    return True, ""

def validate_node_move(node_id: str, 
                      target_parent_id: str,
                      nodes_registry: Dict[str, Node]) -> Tuple[bool, str]:
    """
    Validar si se puede mover un nodo a una nueva ubicación
    
    Args:
        node_id: ID del nodo a mover
        target_parent_id: ID del nuevo padre
        nodes_registry: Registro de nodos
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if node_id not in nodes_registry:
        return False, "El nodo no existe"
    
    if target_parent_id not in nodes_registry:
        return False, "El destino no existe"
    
    if node_id == target_parent_id:
        return False, "No se puede mover un nodo dentro de sí mismo"
    
    target_parent = nodes_registry[target_parent_id]
    if not target_parent.is_folder:
        return False, "El destino debe ser una carpeta"
    
    # Verificar que no se mueva a un descendiente
    current_id = target_parent_id
    while current_id and current_id in nodes_registry:
        if current_id == node_id:
            return False, "No se puede mover un nodo a sus descendientes"
        current_id = nodes_registry[current_id].parent_id
    
    return True, ""

def validate_node_name(name: str, 
                      parent_id: Optional[str],
                      nodes_registry: Dict[str, Node],
                      exclude_node_id: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validar si un nombre de nodo es válido y único en su contexto
    
    Args:
        name: Nombre a validar
        parent_id: ID del padre
        nodes_registry: Registro de nodos
        exclude_node_id: ID del nodo a excluir de la validación (para renombrado)
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not name or not name.strip():
        return False, "El nombre no puede estar vacío"
    
    # Verificar caracteres inválidos