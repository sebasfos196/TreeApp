# presentation/views/panels/preview_panel/renderers/folders_renderer.py
"""
Renderizador para modo ASCII solo carpetas de vista previa.
"""
from typing import List, Dict, Any
from domain.node.node_entity import Node


class FoldersRenderer:
    """Renderizador para vista previa solo carpetas con markdown y estado."""
    
    def __init__(self, node_repository):
        self.node_repository = node_repository
    
    def render(self, root_nodes: List[Node], config: Dict[str, Any]) -> str:
        """
        Renderizar vista ASCII solo carpetas.
        
        Args:
            root_nodes: Lista de nodos raíz
            config: Configuración del modo solo carpetas
            
        Returns:
            str: Contenido renderizado
        """
        if not root_nodes:
            return "📂 Sin contenido"
        
        lines = []
        
        for i, root in enumerate(root_nodes):
            is_last_root = (i == len(root_nodes) - 1)
            self._render_folder_node(root, lines, "", is_last_root, config)
        
        return '\n'.join(lines) if lines else "📂 Sin contenido"
    
    def _render_folder_node(self, node: Node, lines: List[str], prefix: str, is_last: bool, config: Dict[str, Any]):
        """Renderizar solo nodos de tipo carpeta con información extendida."""
        if node.is_folder():
            # Contar archivos en esta carpeta
            children = self.node_repository.find_children(node.node_id)
            file_count = len([child for child in children if child.is_file()])
            
            # Caracteres ASCII
            branch = "├── " if not is_last else "└── "
            extend = "│   " if not is_last else "    "
            
            # Icono
            icon = "📁 " if config.get('show_icons', True) else ""
            
            # Contador de archivos
            count_info = ""
            if config.get('show_file_count', True) and file_count > 0:
                count_info = f" ({file_count} archivos)"
            
            # Estado de la carpeta
            status_info = ""
            if node.status.value:
                status_info = f" {node.status.value}"
            
            # Markdown de la carpeta
            markdown_info = ""
            if node.markdown_short:
                md_text = node.markdown_short.strip()
                # Remover # del markdown para display más limpio
                if md_text.startswith('#'):
                    md_text = md_text.lstrip('#').strip()
                
                max_length = config.get('markdown_max_length', 40)
                if len(md_text) > max_length:
                    md_text = md_text[:max_length] + "..."
                
                if md_text:
                    markdown_info = f" - {md_text}"
            
            # Línea completa
            line = f"{prefix}{branch}{icon}{node.name}{count_info}{status_info}{markdown_info}"
            lines.append(line)
            
            # Hijos (solo carpetas)
            folders = [child for child in children if child.is_folder()]
            folders.sort(key=lambda x: x.name.lower())
            
            for i, child in enumerate(folders):
                is_last_child = (i == len(folders) - 1)
                self._render_folder_node(child, lines, prefix + extend, is_last_child, config)