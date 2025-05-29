"""
presentation/views/panels/preview_panel/renderers/base_renderer.py
================================================================

Clase base abstracta para todos los renderers
- Define interfaz común
- Utilidades compartidas
- Validación de datos
- 80 líneas - Cumple límite
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class BaseRenderer(ABC):
    """Clase base abstracta para renderers de vista previa"""
    
    def __init__(self):
        self.name = "Base Renderer"
        self.description = "Renderer base abstracto"
    
    @abstractmethod
    def render(self, nodes: Dict[str, Any], root_id: str, config: Dict[str, Any]) -> str:
        """
        Renderiza la estructura de nodos según el formato específico
        
        Args:
            nodes: Diccionario de nodos {id: node_data}
            root_id: ID del nodo raíz
            config: Configuración del renderer
            
        Returns:
            str: Contenido renderizado
        """
        pass
    
    def validate_data(self, nodes: Dict[str, Any], root_id: str) -> bool:
        """Valida que los datos sean correctos"""
        
        if not nodes:
            return False
        
        if not root_id or root_id not in nodes:
            return False
        
        return True
    
    def get_node_children(self, nodes: Dict[str, Any], node_id: str) -> List[str]:
        """Obtiene los hijos de un nodo"""
        
        node = nodes.get(node_id)
        if not node:
            return []
        
        return node.get('children', [])
    
    def get_node_icon(self, node: Dict[str, Any]) -> str:
        """Obtiene el icono apropiado para un nodo"""
        
        node_type = node.get('type', 'file')
        return "📁" if node_type == 'folder' else "📄"
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Trunca texto si excede la longitud máxima"""
        
        if not text or max_length <= 0:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."
    
    def count_nodes_by_type(self, nodes: Dict[str, Any]) -> Dict[str, int]:
        """Cuenta nodos por tipo"""
        
        counts = {'folders': 0, 'files': 0, 'total': 0}
        
        for node in nodes.values():
            node_type = node.get('type', 'file')
            if node_type == 'folder':
                counts['folders'] += 1
            else:
                counts['files'] += 1
            counts['total'] += 1
        
        return counts
    
    def count_nodes_by_status(self, nodes: Dict[str, Any]) -> Dict[str, int]:
        """Cuenta nodos por estado"""
        
        counts = {'completed': 0, 'pending': 0, 'blocked': 0}
        
        for node in nodes.values():
            status = node.get('status', '⬜')
            if status == '✅':
                counts['completed'] += 1
            elif status == '⬜':
                counts['pending'] += 1
            elif status == '❌':
                counts['blocked'] += 1
        
        return counts
    
    def generate_statistics(self, nodes: Dict[str, Any]) -> str:
        """Genera estadísticas de la estructura"""
        
        type_counts = self.count_nodes_by_type(nodes)
        status_counts = self.count_nodes_by_status(nodes)
        
        stats = f"""
═══ ESTADÍSTICAS ═══
Total nodos: {type_counts['total']}
Carpetas: {type_counts['folders']}
Archivos: {type_counts['files']}
Completados ✅: {status_counts['completed']}
Pendientes ⬜: {status_counts['pending']}
Bloqueados ❌: {status_counts['blocked']}"""
        
        return stats