# presentation/views/panels/preview_panel/renderers/classic_renderer.py
"""
Renderizador para modo clásico de vista previa.
"""
from typing import List, Dict, Any
from domain.node.node_entity import Node


class ClassicRenderer:
    """Renderizador para vista previa en modo clásico."""
    
    def __init__(self, node_repository):
        self.node_repository = node_repository
    
    def render(self, root_nodes: List[Node], config: Dict[str, Any]) -> str:
        """
        Renderizar vista clásica.
        
        Args:
            root_nodes: Lista de nodos raíz
            config: Configuración del modo clásico
            
        Returns:
            str: Contenido renderizado
        """
        if not root_nodes:
            return "📂 Sin contenido"
        
        lines = []
        
        for root in root_nodes:
            self._render_node(root, lines, 0, config)
        
        return '\n'.join(lines) if lines else "📂 Sin contenido"
    
    def _render_node(self, node: Node, lines: List[str], depth: int, config: Dict[str, Any]):
        """Renderizar un nodo individual y sus hijos."""
        if depth > config.get('max_depth', 10):
            return
        
        # Indentación
        indent = ' ' * (depth * config.get('indent_spaces', 4))
        
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
            max_length = config.get('markdown_max_length', 50)
            if len(md_text) > max_length:
                md_text = md_text[:max_length] + "..."
            markdown = f" - {md_text}"
        
        # Línea completa
        line = f"{indent}{icon}{node.name}{status}{markdown}"
        lines.append(line)
        
        # Hijos recursivos
        if node.is_folder():
            children = self.node_repository.find_children(node.node_id)
            # Ordenar hijos
            children.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for child in children:
                self._render_node(child, lines, depth + 1, config)