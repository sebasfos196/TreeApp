#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estructuras y helpers para manejar árboles jerárquicos de nodos en TreeApp v4 Pro.
Incluye utilidades para recorrer, buscar, y manipular árboles de nodos.
"""

from typing import Dict, List, Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

class TreeWalker:
    """
    Utilidad para recorrer árboles de nodos con distintas estrategias (preorder, postorder, bfs).
    """

    @staticmethod
    def traverse_preorder(node_id: str, nodes: Dict[str, Any], visit: Callable[[Any], None]) -> None:
        """
        Recorrido en preorden (padre antes que hijos).

        Args:
            node_id: ID del nodo raíz.
            nodes: Diccionario {id: Node}.
            visit: Función a aplicar a cada nodo.
        """
        if node_id not in nodes:
            return
        visit(nodes[node_id])
        for child_id in getattr(nodes[node_id], "children_ids", []):
            TreeWalker.traverse_preorder(child_id, nodes, visit)

    @staticmethod
    def traverse_postorder(node_id: str, nodes: Dict[str, Any], visit: Callable[[Any], None]) -> None:
        """
        Recorrido en postorden (hijos antes que padre).
        """
        if node_id not in nodes:
            return
        for child_id in getattr(nodes[node_id], "children_ids", []):
            TreeWalker.traverse_postorder(child_id, nodes, visit)
        visit(nodes[node_id])

    @staticmethod
    def traverse_bfs(root_id: str, nodes: Dict[str, Any], visit: Callable[[Any], None]) -> None:
        """
        Recorrido en anchura (nivel por nivel).
        """
        queue = [root_id]
        while queue:
            current_id = queue.pop(0)
            if current_id in nodes:
                visit(nodes[current_id])
                queue.extend(getattr(nodes[current_id], "children_ids", []))

def find_node_by_name(name: str, nodes: Dict[str, Any]) -> Optional[Any]:
    """
    Buscar un nodo por nombre exacto (case-insensitive).

    Args:
        name: Nombre a buscar.
        nodes: Diccionario {id: Node}.

    Returns:
        El primer nodo que coincida, o None.
    """
    name = name.strip().lower()
    for node in nodes.values():
        if getattr(node, "name", "").strip().lower() == name:
            return node
    return None

def collect_subtree_ids(root_id: str, nodes: Dict[str, Any]) -> List[str]:
    """
    Obtener todos los IDs de los nodos descendientes de un nodo raíz (incluido).

    Args:
        root_id: ID raíz.
        nodes: Diccionario {id: Node}.

    Returns:
        Lista de IDs.
    """
    ids = []
    def collect(node):
        ids.append(node.id)
    TreeWalker.traverse_preorder(root_id, nodes, collect)
    return ids

def get_all_leaf_nodes(nodes: Dict[str, Any]) -> List[Any]:
    """
    Retorna todos los nodos hoja (sin hijos).
    """
    return [n for n in nodes.values() if not getattr(n, "children_ids", [])]

def get_parent_chain(node_id: str, nodes: Dict[str, Any]) -> List[Any]:
    """
    Devuelve la cadena de nodos padres desde el nodo dado hasta la raíz.

    Args:
        node_id: ID del nodo.
        nodes: Diccionario {id: Node}.

    Returns:
        Lista de nodos desde el más cercano hasta la raíz.
    """
    chain = []
    current = nodes.get(node_id)
    while current and getattr(current, "parent_id", None):
        parent = nodes.get(current.parent_id)
        if parent:
            chain.append(parent)
            current = parent
        else:
            break
    return chain
