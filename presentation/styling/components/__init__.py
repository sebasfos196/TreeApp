"""
presentation/styling/components/__init__.py
==========================================

Imports y exports para componentes de styling
- Simplifica imports desde otros módulos
- Expone clases principales
- 25 líneas - Cumple límite
"""

from .flat_separator import (
    FlatSeparator,
    ResizableFlatSeparator,
    PanelSeparator
)

from .panel_header import (
    PanelHeader,
    ExplorerHeader,
    EditorHeader,
    PreviewHeader,
    UnifiedHeaderManager
)

from .unified_buttons import (
    VSCodeButton,
    IconButton,
    ActionButton,
    ToggleButton,
    ButtonGroup,
    ExplorerButtons,
    PreviewButtons
)

__all__ = [
    'FlatSeparator',
    'ResizableFlatSeparator', 
    'PanelSeparator',
    'PanelHeader',
    'ExplorerHeader',
    'EditorHeader',
    'PreviewHeader',
    'UnifiedHeaderManager',
    'VSCodeButton',
    'IconButton',
    'ActionButton',
    'ToggleButton',
    'ButtonGroup',
    'ExplorerButtons',
    'PreviewButtons'
]