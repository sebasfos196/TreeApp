# presentation/views/panels/preview_panel/renderers/columns_renderer.py
"""
Renderizador para modo columnas de vista previa con estadísticas.
"""
from typing import List, Dict, Any, NamedTuple
from domain.node.node_entity import Node, NodeStatus


class NodeData(NamedTuple):
    """Estructura para datos de nodo en columnas."""
    path: str
    status: str
    markdown: str


class ColumnsRenderer:
    """Renderizador para vista previa en modo columnas con estadísticas."""
    
    def __init__(self, node_repository):
        self.node_repository = node_repository
    
    def render(self, root_nodes: List[Node], config: Dict[str, Any]) -> str:
        """
        Renderizar vista en columnas con estadísticas.
        
        Args:
            root_nodes: Lista de nodos raíz
            config: Configuración del modo columnas
            
        Returns:
            str: Contenido renderizado
        """
        if not root_nodes:
            return "📂 Sin contenido"
        
        # Recopilar todos los nodos
        all_nodes_data = []
        stats = self._initialize_stats()
        
        for root in root_nodes:
            self._collect_nodes_data(root, "", all_nodes_data, stats)
        
        if not all_nodes_data:
            return "📂 Sin contenido"
        
        # Calcular anchos óptimos
        widths = self._calculate_optimal_widths(all_nodes_data, config)
        
        # Generar contenido
        lines = []
        
        # Encabezados
        if config.get('show_headers', True):
            self._add_headers(lines, widths)
        
        # Datos
        self._add_data_rows(lines, all_nodes_data, widths)
        
        # Estadísticas
        self._add_statistics(lines, stats, widths)
        
        return '\n'.join(lines)
    
    def _initialize_stats(self) -> Dict[str, int]:
        """Inicializar diccionario de estadísticas."""
        return {
            'total_folders': 0,
            'total_files': 0,
            'completed': 0,
            'pending': 0,
            'in_progress': 0,
            'no_status': 0
        }
    
    def _collect_nodes_data(self, node: Node, path_prefix: str, data_list: List[NodeData], stats: Dict[str, int]):
        """Recopilar datos de nodos y actualizar estadísticas."""
        # Ruta completa con icono
        full_path = f"{path_prefix}/{node.name}" if path_prefix else node.name
        icon = "📁 " if node.is_folder() else "📄 "
        path_with_icon = f"{icon}{full_path}"
        
        # Datos del nodo
        node_data = NodeData(
            path=path_with_icon,
            status=node.status.value or "",
            markdown=node.markdown_short.strip() if node.markdown_short else ""
        )
        data_list.append(node_data)
        
        # Actualizar estadísticas
        if node.is_folder():
            stats['total_folders'] += 1
        else:
            stats['total_files'] += 1
        
        # Estadísticas por estado
        if node.status == NodeStatus.COMPLETED:
            stats['completed'] += 1
        elif node.status == NodeStatus.PENDING:
            stats['pending'] += 1
        elif node.status == NodeStatus.IN_PROGRESS:
            stats['in_progress'] += 1
        else:
            stats['no_status'] += 1
        
        # Procesar hijos recursivamente
        if node.is_folder():
            children = self.node_repository.find_children(node.node_id)
            children.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for child in children:
                self._collect_nodes_data(child, full_path, data_list, stats)
    
    def _calculate_optimal_widths(self, data_list: List[NodeData], config: Dict[str, Any]) -> Dict[str, int]:
        """Calcular anchos óptimos para las columnas."""
        # Calcular anchos basados en contenido
        max_path_len = max(len(data.path) for data in data_list) if data_list else 20
        max_status_len = max(len(data.status) for data in data_list) if data_list else 8
        max_markdown_len = max(len(data.markdown) for data in data_list) if data_list else 20
        
        # Aplicar límites configurables
        return {
            'path': min(max(max_path_len, 20), config.get('col_path_width', 200)),
            'status': min(max(max_status_len, 8), config.get('col_status_width', 80)),
            'markdown': min(max(max_markdown_len, 20), config.get('col_markdown_width', 300))
        }
    
    def _add_headers(self, lines: List[str], widths: Dict[str, int]):
        """Agregar encabezados de columnas."""
        path_header = "RUTA".ljust(widths['path'])
        status_header = "ESTADO".center(widths['status'])
        markdown_header = "DESCRIPCIÓN".ljust(widths['markdown'])
        
        lines.append(f"{path_header} │ {status_header} │ {markdown_header}")
        
        # Línea separadora
        separator = "─" * widths['path'] + "─┼─" + "─" * widths['status'] + "─┼─" + "─" * widths['markdown']
        lines.append(separator)
    
    def _add_data_rows(self, lines: List[str], data_list: List[NodeData], widths: Dict[str, int]):
        """Agregar filas de datos."""
        for data in data_list:
            # Formatear columnas con truncado si es necesario
            path_col = self._truncate_and_pad(data.path, widths['path'], align='left')
            status_col = self._truncate_and_pad(data.status, widths['status'], align='center')
            markdown_col = self._truncate_and_pad(data.markdown, widths['markdown'], align='left')
            
            line = f"{path_col} │ {status_col} │ {markdown_col}"
            lines.append(line)
    
    def _add_statistics(self, lines: List[str], stats: Dict[str, int], widths: Dict[str, int]):
        """Agregar estadísticas al final."""
        total_width = widths['path'] + widths['status'] + widths['markdown'] + 6  # 6 por separadores
        
        lines.extend([
            "",
            "═" * total_width,
            "📊 ESTADÍSTICAS DEL PROYECTO:",
            "═" * total_width,
            f"📁 Total carpetas:     {stats['total_folders']}",
            f"📄 Total archivos:     {stats['total_files']}",
            f"✅ Completados:        {stats['completed']}",
            f"⬜ En progreso:        {stats['in_progress']}",
            f"❌ Pendientes:         {stats['pending']}",
            f"🔘 Sin estado:         {stats['no_status']}",
            f"🔢 Total elementos:    {stats['total_folders'] + stats['total_files']}",
            "═" * total_width
        ])
    
    def _truncate_and_pad(self, text: str, width: int, align: str = 'left') -> str:
        """Truncar texto si es necesario y aplicar padding con alineación."""
        if len(text) > width:
            text = text[:width-3] + "..."
        
        if align == 'center':
            return text.center(width)
        elif align == 'right':
            return text.rjust(width)
        else:  # left
            return text.ljust(width)