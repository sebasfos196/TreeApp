# presentation/views/panels/preview_panel/renderers/ascii_renderer.py
"""
Renderizador para modo ASCII completo de vista previa.
"""
from typing import List, Dict, Any
from domain.node.node_entity import Node


class AsciiRenderer:
    """Renderizador para vista previa en modo ASCII completo."""
    
    def __init__(self, node_repository):
        self.node_repository = node_repository
    
    def render(self, root_nodes: List[Node], config: Dict[str, Any]) -> str:
        """
        Renderizar vista ASCII completa.
        
        Args:
            root_nodes: Lista de nodos raíz
            config: Configuración del modo ASCII
            
        Returns:
            str: Contenido renderizado
        """
        if not root_nodes:
            return "📂 Sin contenido"
        
        lines = []
        
        for i, root in enumerate(root_nodes):
            is_last_root = (i == len(root_nodes) - 1)
            self._render_node(root, lines, "", is_last_root, config)
        
        return '\n'.join(lines) if lines else "📂 Sin contenido"
    
    def _render_node(self, node: Node, lines: List[str], prefix: str, is_last: bool, config: Dict[str, Any]):
        """Renderizar un nodo individual con caracteres ASCII."""
        # Caracteres ASCII según configuración
        if config.get('use_unicode', True):
            branch = "├── " if not is_last else "└── "
            extend = "│   " if not is_last else "    "
        else:
            branch = "|-- " if not is_last else "`-- "
            extend = "|   " if not is_last else "    "
        
        # Icono
        icon = ""
        if config.get('show_icons', True):
            icon = "📁 " if node.is_folder() else "📄 "
        
        # Estado
        status = ""
        if config.get('show_status', True) and node.status.value:
            status = f" {node.status.value}"
        
        # Markdown
        markdown = ""
        if config.get('show_markdown', True) and node.markdown_short:
            md_text = node.markdown_short.strip()
            max_length = config.get('markdown_max_length', 40)
            if len(md_text) > max_length:
                md_text = md_text[:max_length] + "..."
            markdown = f" - {md_text}"
        
        # Línea completa
        line = f"{prefix}{branch}{icon}{node.name}{status}{markdown}"
        lines.append(line)
        
        # Hijos recursivos
        if node.is_folder():
            children = self.node_repository.find_children(node.node_id)
            children.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                self._render_node(child, lines, prefix + extend, is_last_child, config)