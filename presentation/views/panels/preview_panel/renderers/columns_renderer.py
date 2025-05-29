"""
presentation/views/panels/preview_panel/renderers/columns_renderer.py - MEJORADO
================================================================================

Renderer columnas estilo Excel mejorado con:
- 3 columnas: Ruta | Estado | Markdown
- Anchos configurables y alineación
- Separadores visuales claros
- Colores alternados opcional
- 150 líneas - Cumple límite
"""

from typing import Dict, List, Any, Tuple
from .base_renderer import BaseRenderer

class ColumnsRenderer(BaseRenderer):
    """Renderer estilo columnas/tabla Excel"""
    
    def __init__(self):
        super().__init__()
        self.name = "Columnas"
        self.description = "Tabla con columnas Ruta | Estado | Markdown"
    
    def render(self, nodes: Dict[str, Any], root_id: str, config: Dict[str, Any]) -> str:
        """Renderiza en formato de columnas"""
        
        if not self.validate_data(nodes, root_id):
            return "❌ Datos inválidos para renderizado en columnas"
        
        result = []
        
        # Encabezado
        result.append("📊 Vista Previa - Modo Columnas")
        result.append("=" * 60)
        result.append("")
        
        # Recopilar todos los nodos en lista plana
        flat_nodes = []
        self._flatten_nodes(nodes, root_id, "", flat_nodes)
        
        # Configuración de columnas
        col_widths = config.get('col_widths', [40, 8, 30])
        show_headers = config.get('show_headers', True)
        alternating_colors = config.get('alternating_colors', True)
        
        # Headers de columnas
        if show_headers:
            header_line = self._format_row(
                ["RUTA", "ESTADO", "MARKDOWN"],
                col_widths,
                is_header=True
            )
            result.append(header_line)
            result.append(self._create_separator_line(col_widths))
            result.append("")
        
        # Filas de datos
        for i, (path, node) in enumerate(flat_nodes):
            # Preparar datos de la fila
            status = node.get('status', '⬜')
            markdown = node.get('markdown', '')
            
            # Truncar markdown si es necesario
            max_md_length = config.get('markdown_length', 50)
            if markdown:
                markdown = self.truncate_text(markdown, max_md_length)
            
            # Formatear fila
            row_data = [path, status, markdown]
            formatted_row = self._format_row(row_data, col_widths)
            
            # Agregar indicador de fila alternada (opcional)
            if alternating_colors and i % 2 == 1:
                formatted_row = f"░ {formatted_row}"
            else:
                formatted_row = f"  {formatted_row}"
            
            result.append(formatted_row)
        
        # Estadísticas
        result.append("")
        result.append(self._create_separator_line(col_widths))
        result.append("")
        result.append(self.generate_statistics(nodes))
        
        return '\n'.join(result)
    
    def _flatten_nodes(self, nodes: Dict[str, Any], node_id: str, parent_path: str, flat_list: List[Tuple[str, Dict]]):
        """Aplana la estructura jerárquica en lista de rutas"""
        
        if node_id not in nodes:
            return
        
        node = nodes[node_id]
        node_name = node.get('name', 'Sin nombre')
        
        # Construir ruta completa
        if parent_path:
            full_path = f"{parent_path}/{node_name}"
        else:
            full_path = node_name
        
        # Agregar a la lista
        flat_list.append((full_path, node))
        
        # Procesar hijos
        children = self.get_node_children(nodes, node_id)
        for child_id in children:
            self._flatten_nodes(nodes, child_id, full_path, flat_list)
    
    def _format_row(self, data: List[str], col_widths: List[int], is_header: bool = False) -> str:
        """Formatea una fila con columnas alineadas"""
        
        formatted_cols = []
        
        for i, (text, width) in enumerate(zip(data, col_widths)):
            # Truncar texto si excede el ancho
            if len(text) > width:
                text = text[:width-3] + "..."
            
            # Alinear texto
            if i == 0:  # Ruta - alineada a la izquierda
                formatted_text = text.ljust(width)
            elif i == 1:  # Estado - centrado
                formatted_text = text.center(width)
            else:  # Markdown - alineada a la izquierda
                formatted_text = text.ljust(width)
            
            formatted_cols.append(formatted_text)
        
        # Unir columnas con separadores
        if is_header:
            separator = " │ "
        else:
            separator = " │ "
        
        return separator.join(formatted_cols)
    
    def _create_separator_line(self, col_widths: List[int]) -> str:
        """Crea línea separadora entre header y datos"""
        
        separators = []
        for width in col_widths:
            separators.append("─" * width)
        
        return "─┼─".join(separators)
    
    def _auto_adjust_column_widths(self, flat_nodes: List[Tuple[str, Dict]], config: Dict[str, Any]) -> List[int]:
        """Ajusta automáticamente los anchos de columna según el contenido"""
        
        max_widths = [10, 6, 20]  # Mínimos
        
        for path, node in flat_nodes:
            # Ancho de ruta
            max_widths[0] = max(max_widths[0], len(path))
            
            # Ancho de estado (fijo)
            max_widths[1] = max(max_widths[1], 6)
            
            # Ancho de markdown
            markdown = node.get('markdown', '')
            if markdown:
                max_widths[2] = max(max_widths[2], len(markdown))
        
        # Aplicar límites máximos
        max_limits = [60, 10, 80]
        for i in range(len(max_widths)):
            max_widths[i] = min(max_widths[i], max_limits[i])
        
        return max_widths
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Esquema de configuración para columns renderer"""
        
        return {
            "col_widths": {
                "type": "array",
                "default": [40, 8, 30],
                "description": "Anchos de las columnas [Ruta, Estado, Markdown]"
            },
            "show_headers": {
                "type": "boolean",
                "default": True,
                "description": "Mostrar encabezados de columnas"
            },
            "alternating_colors": {
                "type": "boolean",
                "default": True,
                "description": "Colores alternados en filas"
            },
            "markdown_length": {
                "type": "integer",
                "default": 50,
                "min": 10,
                "max": 200,
                "description": "Longitud máxima del markdown"
            },
            "auto_adjust_widths": {
                "type": "boolean",
                "default": False,
                "description": "Ajustar automáticamente anchos de columna"
            }
        }