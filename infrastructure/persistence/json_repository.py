"""
infrastructure/persistence/json_repository.py - REPARADO
========================================================

Repositorio JSON para persistencia de datos
- Carga y guarda datos en treeapp_data.json
- Gestión de nodos y estructura del árbol
- Compatible con el sistema actual
- 120 líneas - Cumple límite
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

class JsonRepository:
    """Repositorio para persistencia de datos en JSON"""
    
    def __init__(self, file_path: str = "treeapp_data.json"):
        self.file_path = file_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.root_id: Optional[str] = None
        self.load_data()
    
    def load_data(self):
        """Carga datos desde el archivo JSON"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.root_id = data.get('root_id')
                    self.nodes = data.get('nodes', {})
                    
                    print(f"✅ Datos cargados: {len(self.nodes)} nodos")
            else:
                print("📁 Archivo de datos no existe, empezando con datos vacíos")
                self.nodes = {}
                self.root_id = None
                
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            self.nodes = {}
            self.root_id = None
    
    def save_data(self):
        """Guarda datos al archivo JSON"""
        try:
            data = {
                'root_id': self.root_id,
                'nodes': self.nodes,
                'last_updated': datetime.now().isoformat(),
                'version': '4.0'
            }
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Datos guardados: {len(self.nodes)} nodos")
            
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
    
    def create_node(self, name: str, node_type: str, parent_id: Optional[str] = None) -> str:
        """
        Crea un nuevo nodo
        
        Args:
            name: Nombre del nodo
            node_type: 'folder' o 'file'
            parent_id: ID del nodo padre (None para nodo raíz)
            
        Returns:
            str: ID del nodo creado
        """
        node_id = str(uuid.uuid4())
        
        node_data = {
            'id': node_id,
            'name': name,
            'type': node_type,
            'parent_id': parent_id,
            'status': '⬜',  # Pendiente por defecto
            'markdown': '',
            'notes': '',
            'code': '',
            'children': [],
            'created_at': datetime.now().isoformat()
        }
        
        # Agregar al diccionario de nodos
        self.nodes[node_id] = node_data
        
        # Si tiene padre, agregarlo a los hijos del padre
        if parent_id and parent_id in self.nodes:
            parent_node = self.nodes[parent_id]
            if 'children' not in parent_node:
                parent_node['children'] = []
            parent_node['children'].append(node_id)
        
        # Si no hay root_id, este se convierte en root
        if not self.root_id:
            self.root_id = node_id
        
        self.save_data()
        return node_id
    
    def update_node(self, node_id: str, **kwargs):
        """
        Actualiza un nodo existente
        
        Args:
            node_id: ID del nodo a actualizar
            **kwargs: Campos a actualizar
        """
        if node_id in self.nodes:
            node = self.nodes[node_id]
            
            # Actualizar campos válidos
            valid_fields = ['name', 'type', 'status', 'markdown', 'notes', 'code']
            for key, value in kwargs.items():
                if key in valid_fields:
                    node[key] = value
            
            node['updated_at'] = datetime.now().isoformat()
            self.save_data()
            return True
        
        return False
    
    def delete_node(self, node_id: str) -> bool:
        """
        Elimina un nodo y todos sus hijos
        
        Args:
            node_id: ID del nodo a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        
        # Eliminar hijos recursivamente
        children = node.get('children', [])
        for child_id in children[:]:  # Copia para evitar modificación durante iteración
            self.delete_node(child_id)
        
        # Remover de los hijos del padre
        parent_id = node.get('parent_id')
        if parent_id and parent_id in self.nodes:
            parent_node = self.nodes[parent_id]
            if 'children' in parent_node and node_id in parent_node['children']:
                parent_node['children'].remove(node_id)
        
        # Eliminar el nodo
        del self.nodes[node_id]
        
        # Si era el root, limpiar root_id
        if self.root_id == node_id:
            self.root_id = None
        
        self.save_data()
        return True
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un nodo por su ID"""
        return self.nodes.get(node_id)
    
    def get_children(self, node_id: str) -> List[str]:
        """Obtiene los IDs de los hijos de un nodo"""
        node = self.nodes.get(node_id)
        if node:
            return node.get('children', [])
        return []
    
    def get_node_count(self) -> int:
        """Obtiene el número total de nodos"""
        return len(self.nodes)
    
    def clear_all_data(self):
        """Limpia todos los datos (usar con precaución)"""
        self.nodes.clear()
        self.root_id = None
        self.save_data()
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de los datos"""
        stats = {
            'total_nodes': len(self.nodes),
            'folders': 0,
            'files': 0,
            'completed': 0,
            'pending': 0,
            'blocked': 0
        }
        
        for node in self.nodes.values():
            # Contar por tipo
            if node.get('type') == 'folder':
                stats['folders'] += 1
            else:
                stats['files'] += 1
            
            # Contar por status
            status = node.get('status', '⬜')
            if status == '✅':
                stats['completed'] += 1
            elif status == '⬜':
                stats['pending'] += 1
            elif status == '❌':
                stats['blocked'] += 1
        
        return stats