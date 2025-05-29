# infrastructure/persistence/json_repository.py
"""
Repositorio JSON para persistencia de nodos en TreeApp v4 Pro.
"""
import json
import os
from typing import Dict, List, Optional
from domain.node.node_entity import Node, NodeType, NodeStatus


class NodeRepository:
    """Repositorio para gestionar nodos."""
    
    def __init__(self, file_path: str = "treeapp_data.json"):
        self._file_path = file_path
        self._nodes: Dict[str, Node] = {}
        self._load_from_file()
    
    def save(self, node: Node) -> Node:
        """Guardar un nodo."""
        self._nodes[node.node_id] = node
        self._save_to_file()
        return node
    
    def find_by_id(self, node_id: str) -> Optional[Node]:
        """Buscar nodo por ID."""
        return self._nodes.get(node_id)
    
    def find_all(self) -> List[Node]:
        """Obtener todos los nodos."""
        return list(self._nodes.values())
    
    def find_children(self, parent_id: str) -> List[Node]:
        """Obtener hijos de un nodo."""
        children = []
        for node in self._nodes.values():
            if node.parent_id == parent_id:
                children.append(node)
        return children
    
    def find_roots(self) -> List[Node]:
        """Obtener nodos raíz (sin padre)."""
        roots = []
        for node in self._nodes.values():
            if node.parent_id is None:
                roots.append(node)
        return roots
    
    def delete(self, node_id: str) -> bool:
        """Eliminar un nodo."""
        if node_id in self._nodes:
            del self._nodes[node_id]
            self._save_to_file()
            return True
        return False
    
    def _load_from_file(self) -> None:
        """Cargar nodos desde archivo JSON."""
        if not os.path.exists(self._file_path):
            return
        
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            nodes_data = data.get('nodes', [])
            for node_data in nodes_data:
                node = self._dict_to_node(node_data)
                self._nodes[node.node_id] = node
                
        except Exception as e:
            print(f"Error cargando datos: {e}")
    
    def _save_to_file(self) -> None:
        """Guardar nodos a archivo JSON."""
        try:
            nodes_list = []
            for node in self._nodes.values():
                node_dict = self._node_to_dict(node)
                nodes_list.append(node_dict)
            
            data = {'nodes': nodes_list}
            
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error guardando datos: {e}")
    
    def _node_to_dict(self, node: Node) -> dict:
        """Convertir nodo a diccionario."""
        return {
            'node_id': node.node_id,
            'name': node.name,
            'node_type': node.node_type.value,
            'markdown_short': node.markdown_short,
            'explanation': node.explanation,
            'code': node.code,
            'status': node.status.value,
            'parent_id': node.parent_id,
            'children_ids': node.children_ids,
            'created': node.created,
            'modified': node.modified,
            'tags': node.tags,
            'metadata': node.metadata
        }
    
    def _dict_to_node(self, data: dict) -> Node:
        """Convertir diccionario a nodo."""
        node = Node(
            name=data['name'],
            node_type=NodeType(data['node_type'])
        )
        node.node_id = data['node_id']
        node.markdown_short = data.get('markdown_short', '')
        node.explanation = data.get('explanation', '')
        node.code = data.get('code', '')
        node.status = NodeStatus(data.get('status', ''))
        node.parent_id = data.get('parent_id')
        node.children_ids = data.get('children_ids', [])
        node.created = data.get('created', '')
        node.modified = data.get('modified', '')
        node.tags = data.get('tags', [])
        node.metadata = data.get('metadata', {})
        return node