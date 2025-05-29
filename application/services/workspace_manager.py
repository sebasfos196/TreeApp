"""
application/services/workspace_manager.py - REPARADO
===================================================

Gestor de workspace inicial compatible con JsonRepository
- Crea workspace inicial con carpeta Root (Req. 4)
- Configuración inicial automática (Req. 5)
- Integración con repositorio actual
- 100 líneas - Cumple límite
"""

from typing import Dict, Any, Optional
from datetime import datetime

class WorkspaceManager:
    """Gestor de workspace inicial y configuración"""
    
    def __init__(self, repository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
        
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
            print("✅ Workspace inicial creado con carpeta Root")
        else:
            workspace_info['root_id'] = self.repository.root_id
            print("📁 Workspace existente cargado")
        
        # Obtener datos para vista previa
        workspace_info['preview_data'] = self.get_initial_preview_data()
        
        return workspace_info
    
    def should_create_initial_workspace(self) -> bool:
        """
        Determina si debe crear workspace inicial
        
        Returns:
            bool: True si debe crear workspace inicial
        """
        
        # Crear si no hay nodos
        if not self.repository.nodes:
            return True
        
        # Crear si no hay root
        if not self.repository.root_id:
            return True
        
        # Crear si el root no existe en los nodos
        if self.repository.root_id not in self.repository.nodes:
            return True
        
        return False
    
    def create_initial_workspace(self) -> str:
        """
        Crea workspace inicial con carpeta Root (Req. 4)
        
        Returns:
            str: ID del nodo root creado
        """
        
        # Limpiar workspace existente si es necesario
        if self.repository.nodes:
            print("🧹 Limpiando workspace anterior...")
            self.repository.clear_all_data()
        
        # Crear nodo Root inicial
        root_id = self.repository.create_node(
            name="Root",
            node_type="folder",
            parent_id=None
        )
        
        # Actualizar con datos específicos del workspace inicial
        self.repository.update_node(
            root_id,
            status='⬜',  # Pendiente (Req. 4)
            markdown='# Nueva carpeta raíz',  # Req. 4
            notes='Carpeta raíz del proyecto inicial',
            code=''
        )
        
        # Establecer como root
        self.repository.root_id = root_id
        self.repository.save_data()
        
        # Notificar creación si hay event bus
        if self.event_bus:
            self.event_bus.publish('workspace_created', {
                'root_id': root_id,
                'workspace_type': 'initial'
            })
        
        return root_id
    
    def get_initial_preview_data(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos iniciales para vista previa (Req. 5)
        
        Returns:
            Dict con datos del root para mostrar inmediatamente
        """
        
        if not self.repository.root_id:
            return None
        
        root_node = self.repository.get_node(self.repository.root_id)
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
    
    def get_workspace_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del workspace actual
        
        Returns:
            Dict con estadísticas del workspace
        """
        
        return self.repository.get_stats()
    
    def reset_workspace(self):
        """Resetea el workspace a estado inicial"""
        
        print("🔄 Reseteando workspace...")
        self.repository.clear_all_data()
        root_id = self.create_initial_workspace()
        
        if self.event_bus:
            self.event_bus.publish('workspace_reset', {
                'new_root_id': root_id
            })
        
        return root_id
    
    def export_workspace_info(self) -> Dict[str, Any]:
        """Exporta información del workspace para debugging"""
        
        stats = self.get_workspace_stats()
        
        return {
            'root_id': self.repository.root_id,
            'total_nodes': stats['total_nodes'],
            'folders': stats['folders'],
            'files': stats['files'],
            'status_distribution': {
                'completed': stats['completed'],
                'pending': stats['pending'],
                'blocked': stats['blocked']
            },
            'repository_file': self.repository.file_path,
            'workspace_ready': bool(self.repository.root_id and self.repository.nodes)
        }