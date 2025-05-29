# domain/validation.py
"""
Validaciones del dominio para TreeApp v4 Pro.
Valida nombres, jerarquías y reglas de negocio.
"""
import re
from typing import List, Optional
from domain.node.node_entity import Node, NodeType


class ValidationError(Exception):
    """Error de validación del dominio."""
    pass


class NodeValidator:
    """Validador para entidades Node."""
    
    # Caracteres prohibidos en nombres de archivos/carpetas
    FORBIDDEN_CHARS = r'[<>:"/\\|?*]'
    RESERVED_NAMES = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 
                      'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 
                      'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 
                      'LPT7', 'LPT8', 'LPT9']
    
    @classmethod
    def validate_name(cls, name: str) -> None:
        """Validar nombre de nodo."""
        if not name or not name.strip():
            raise ValidationError("El nombre no puede estar vacío")
        
        name = name.strip()
        
        if len(name) > 255:
            raise ValidationError("El nombre no puede exceder 255 caracteres")
        
        if re.search(cls.FORBIDDEN_CHARS, name):
            raise ValidationError("El nombre contiene caracteres prohibidos: < > : \" / \\ | ? *")
        
        if name.upper() in cls.RESERVED_NAMES:
            raise ValidationError(f"'{name}' es un nombre reservado del sistema")
        
        if name.startswith('.') and len(name.strip('.')) == 0:
            raise ValidationError("El nombre no puede consistir solo de puntos")
    
    @classmethod
    def validate_node(cls, node: Node) -> None:
        """Validar nodo completo."""
        cls.validate_name(node.name)
        
        if not node.node_id:
            raise ValidationError("El nodo debe tener un ID válido")
        
        # Validar jerarquía
        if node.parent_id == node.node_id:
            raise ValidationError("Un nodo no puede ser padre de sí mismo")


class TreeValidator:
    """Validador para estructuras de árbol."""
    
    @classmethod
    def validate_hierarchy(cls, nodes: List[Node]) -> None:
        """Validar jerarquía de nodos para evitar ciclos."""
        node_dict = {node.node_id: node for node in nodes}
        
        for node in nodes:
            if cls._has_cycle(node, node_dict, set()):
                raise ValidationError(f"Ciclo detectado en la jerarquía del nodo '{node.name}'")
    
    @classmethod
    def _has_cycle(cls, node: Node, node_dict: dict, visited: set) -> bool:
        """Detectar ciclos en la jerarquía."""
        if node.node_id in visited:
            return True
        
        visited.add(node.node_id)
        
        # Verificar children
        for child_id in node.children_ids:
            if child_id in node_dict:
                child = node_dict[child_id]
                if cls._has_cycle(child, node_dict, visited.copy()):
                    return True
        
        return False
    
    @classmethod
    def validate_parent_child_relationship(cls, parent: Node, child: Node) -> None:
        """Validar relación padre-hijo."""
        if parent.node_id == child.node_id:
            raise ValidationError("Un nodo no puede ser padre de sí mismo")
        
        if not parent.is_folder():
            raise ValidationError("Solo las carpetas pueden tener hijos")
        
        if child.parent_id and child.parent_id != parent.node_id:
            raise ValidationError("El hijo ya tiene otro padre asignado")