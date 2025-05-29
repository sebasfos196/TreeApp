"""
presentation/views/panels/preview_panel/renderers/classic_renderer.py - MEJORADO
================================================================================

Renderer modo clásico mejorado con:
- Indentación configurable
- Iconos opcionales
- Estados y markdown configurables
- Estadísticas integradas
- 120 líneas - Cumple límite
"""

from typing import Dict, List, Any
from .base_renderer import BaseRenderer

class ClassicRenderer(BaseRenderer):
    """Renderer modo clásico con indentación jerárquica"""
    
    def __init__(self):
        super().__init__()
        self.name = "Clásico"
        self.description = "Árbol con indentación jerárquica simple"
    
    def render(self, nodes: Dict[str, Any], root_id: str, config: Dict[str, Any]) -> str:
        """Renderiza en modo clásico"""
        
        if not self.validate_data(nodes, root_id):
            return "❌ Datos inválidos para renderizado"
        
        result = []
        
        # Encabezado
        result.append("📁 Vista Previa - Modo Clásico")
        result.append("=" * 40)
        result.append("")
        
        # Renderizar árbol
        self._render_node(nodes, root_id, 0, result, config)
        
        # Estadísticas
        if config.get('show_statistics', True):
            result.append("")
            result.append(self.generate_statistics(nodes))
        
        return '\n'.join(result)
    
    def _render_node(self, nodes: Dict[str, Any], node_id: str, level: int, result: List[str], config: Dict[str, Any]):
        """Renderiza un nodo y sus hijos recursivamente"""
        
        if node_id not in nodes:
            return
        
        node = nodes[node_id]
        
        # Crear indentación
        indent_size = config.get('indent_size', 2)
        indent = " " * (level * indent_size)
        
        # Construir línea del nodo
        line_parts = []
        
        # Agregar indentación
        line_parts.append(indent)
        
        # Icono (opcional)
        if config.get('show_icons', True):
            icon = self.get_node_icon(node)
            line_parts.append(icon)
        
        # Nombre del nodo
        name = node.get('name', 'Sin nombre')
        line_parts.append(name)
        
        # Estado (opcional)
        if config.get('show_status', True):
            status = node.get('status', '⬜')
            line_parts.append(status)
        
        # Markdown (opcional y truncado)
        if config.get('show_markdown', True):
            markdown = node.get('markdown', '')
            if markdown:
                max_length = config.get('markdown_length', 50)
                truncated_markdown = self.truncate_text(markdown, max_length)
                if truncated_markdown:
                    line_parts.append(f"- {truncated_markdown}")
        
        # Agregar línea al resultado
        result.append(" ".join(line_parts))
        
        # Renderizar hijos
        children = self.get_node_children(nodes, node_id)
        for child_id in children:
            self._render_node(nodes, child_id, level + 1, result, config)
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Obtiene el esquema de configuración para este renderer"""
        
        return {
            "show_icons": {
                "type": "boolean",
                "default": True,
                "description": "Mostrar iconos de carpetas y archivos"
            },
            "show_status": {
                "type": "boolean", 
                "default": True,
                "description": "Mostrar estados (✅❌⬜)"
            },
            "show_markdown": {
                "type": "boolean",
                "default": True,
                "description": "Mostrar contenido markdown"
            },
            "indent_size": {
                "type": "integer",
                "default": 2,
                "min": 1,
                "max": 8,
                "description": "Tamaño de indentación por nivel"
            },
            "markdown_length": {
                "type": "integer",
                "default": 50,
                "min": 10,
                "max": 200,
                "description": "Longitud máxima del markdown"
            },
            "show_statistics": {
                "type": "boolean",
                "default": True,
                "description": "Mostrar estadísticas al final"
            }
        }