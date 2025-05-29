"""
presentation/views/panels/preview_panel/renderers/ascii_renderer.py - MEJORADO
==============================================================================

Renderer ASCII mejorado con:
- Caracteres ASCII configurables (├── └── │)
- Líneas de conexión continuas
- Estilos Unicode/ASCII básico
- Separadores configurables
- 140 líneas - Cumple límite
"""

from typing import Dict, List, Any
from .base_renderer import BaseRenderer

class ASCIIRenderer(BaseRenderer):
    """Renderer ASCII con caracteres de árbol"""
    
    def __init__(self):
        super().__init__()
        self.name = "ASCII"
        self.description = "Árbol con caracteres ASCII (├── └── │)"
        
        # Estilos de caracteres ASCII
        self.ascii_styles = {
            "standard": {
                "branch": "├── ",
                "last": "└── ",
                "vertical": "│   ",
                "space": "    "
            },
            "unicode