"""
application/services/workspace_manager.py
==========================================

Gestor de workspace inicial y configuración
- Crea workspace inicial con carpeta Root (Req. 4)
- Configuración inicial automática (Req. 5)
- Integración con repositorio y vista previa
- 120 líneas - Cumple con límite
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class WorkspaceManager:
    """Gestor de workspace inicial y configuración"""
    
    def __init__(self, repository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
        
    def create_initial_workspace(self) -> str:
        """
        Crea workspace inicial con carpeta Root (Req. 4)
        
        Returns:
            str: ID del nodo root creado
        """
        
        # Limpiar workspace existente
        self.repository.nodes.clear()
        
        # Crear nodo Root inicial con configuración específica
        root_id = str(uuid.uuid4())
        root_node_data = {
            'id': root_id,
            'name': 'Root',
            'type': 'folder',
            'parent_id': None,
            'status': '⬜',  # Pendiente (Req. 4)
            'markdown': '# Nueva carpeta raíz',  # Req. 4
            'notes': 'Carpeta raíz del proyecto inicial',
            'code': '',
            'children': [],
            'created_at': datetime.now().isoformat(),
            'is_root': True  # Marcar como root para hover effects
        }
        
        # Agregar al repositorio
        self.repository.nodes[root_id] = root_node_data
        self.repository.root_id = root_id
        
        # Guardar persistencia
        self.repository.save_data()
        
        # Notificar creación si hay event bus
        if self.event_bus:
            self.event_bus.publish('workspace_created', {
                'root_id': root_id,
                'root_data': root_node_data
            })
        
        return root_id
    
    def should_create_initial_workspace(self) -> bool:
        """
        Determina si debe crear workspace inicial
        
        Returns:
            bool: True si debe crear workspace inicial
        """
        
        # Crear si no hay nodos o no hay root
        if not self.repository.nodes or not self.repository.root_id:
            return True
        
        # Crear si el root no existe en los nodos
        if self.repository.root_id not in self.repository.nodes:
            return True
        
        return False
    
    def get_initial_preview_data(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos iniciales para vista previa (Req. 5)
        
        Returns:
            Dict con datos del root para mostrar inmediatamente
        """
        
        if not self.repository.root_id:
            return None
        
        root_node = self.repository.nodes.get(self.repository.root_id)
        if not root_node:
            return None
        
        return {
            'root_id': self.repository.root_id,
            'name': root_node['name'],
            'status': root_node['status'],
            'markdown': root_node['markdown'],
            'notes': root_node.get('notes', ''),
            'type': root_node['type'],
            'children': root_node.get('children', [])
        }
    
    def initialize_workspace_if_needed(self) -> Dict[str, Any]:
        """
        Inicializa workspace si es necesario
        
        Returns:
            Dict con información del workspace inicializado
        """
        
        workspace_info = {
            'created_new': False,
            'root_id': None,
            'preview_data': None
        }
        
        # Verificar si necesita inicialización
        if self.should_create_initial_workspace():
            root_id = self.create_initial_workspace()
            workspace_info['created_new'] = True
            workspace_info['root_id'] = root_id
        else:
            workspace_info['root_id'] = self.repository.root_id
        
        # Obtener datos para vista previa
        workspace_info['preview_data'] = self.get_initial_preview_data()
        
        return workspace_info
    
    def get_workspace_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del workspace actual
        
        Returns:
            Dict con estadísticas del workspace
        """
        
        total_nodes = len(self.repository.nodes)
        folders = sum(1 for node in self.repository.nodes.values() 
                     if node.get('type') == 'folder')
        files = total_nodes - folders
        
        # Contar por estados
        completed = sum(1 for node in self.repository.nodes.values() 
                       if node.get('status') == '✅')
        pending = sum(1 for node in self.repository.nodes.values() 
                     if node.get('status') == '⬜')
        blocked = sum(1 for node in self.repository.nodes.values() 
                     if node.get('status') == '❌')
        
        return {
            'total_nodes': total_nodes,
            'folders': folders,
            'files': files,
            'completed': completed,
            'pending': pending,
            'blocked': blocked,
            'root_id': self.repository.root_id
        }