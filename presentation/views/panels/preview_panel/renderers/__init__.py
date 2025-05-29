# presentation/views/panels/preview_panel/renderers/__init__.py
"""
Renderers para diferentes modos de vista previa.
"""
from .classic_renderer import ClassicRenderer
from .ascii_renderer import AsciiRenderer
from .folders_renderer import FoldersRenderer
from .columns_renderer import ColumnsRenderer

__all__ = ['ClassicRenderer', 'AsciiRenderer', 'FoldersRenderer', 'ColumnsRenderer']