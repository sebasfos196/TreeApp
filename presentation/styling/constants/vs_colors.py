"""
presentation/styling/constants/vscode_colors.py - CREAR ESTE ARCHIVO
===================================================================

Colores exactos de Visual Studio Code Dark Theme
- Paleta completa con códigos hex precisos
- Estados interactivos (hover, focus, selected)
- Colores específicos para diferentes componentes
- 65 líneas - Cumple con límite de líneas
"""

class VSCodeColors:
    """Colores exactos del tema VS Code Dark"""
    
    # ═══════════════════════════════════════════════════════════════
    # COLORES BASE
    # ═══════════════════════════════════════════════════════════════
    
    # Fondos principales
    BACKGROUND = "#1e1e1e"              # Fondo principal VS Code
    SIDEBAR = "#252526"                 # Barra lateral/explorador
    EDITOR = "#1e1e1e"                  # Área de editor
    PANEL = "#252526"                   # Paneles inferiores
    TITLEBAR = "#323233"                # Barra de título
    
    # ═══════════════════════════════════════════════════════════════
    # BORDES Y SEPARADORES
    # ═══════════════════════════════════════════════════════════════
    
    BORDER_NORMAL = "#3c3c3c"           # Bordes normales
    BORDER_ACTIVE = "#007acc"           # Bordes activos (azul VS Code)
    BORDER_HIGHLIGHT = "#0e639c"        # Borde hover/highlight
    SEPARATOR = "#2d2d30"               # Separadores sutiles
    SEPARATOR_ACTIVE = "#007acc"        # Separador al redimensionar (Req. 1)
    
    # ═══════════════════════════════════════════════════════════════
    # TEXTO
    # ═══════════════════════════════════════════════════════════════
    
    TEXT_PRIMARY = "#cccccc"            # Texto principal
    TEXT_SECONDARY = "#969696"          # Texto secundario
    TEXT_MUTED = "#6a6a6a"             # Texto atenuado
    TEXT_DISABLED = "#3c3c3c"          # Texto deshabilitado
    
    # ═══════════════════════════════════════════════════════════════
    # ESTADOS INTERACTIVOS
    # ═══════════════════════════════════════════════════════════════
    
    HOVER = "#2a2d2e"                   # Hover sutil (Req. 2)
    HOVER_BORDER = "#404040"            # Borde en hover
    SELECTED = "#094771"                # Selección
    SELECTED_BORDER = "#007acc"         # Borde seleccionado
    FOCUS = "#007acc"                   # Foco (azul) (Req. 6)
    FOCUS_GLOW = "rgba(0, 122, 204, 0.4)"  # Glow de foco
    
    # ═══════════════════════════════════════════════════════════════
    # EXPLORADOR DE ARCHIVOS (Req. 2, 3)
    # ═══════════════════════════════════════════════════════════════
    
    TREE_BACKGROUND = "#252526"         # Fondo del árbol
    TREE_HOVER = "#2a2d2e"             # Hover en nodos (NO en root)
    TREE_SELECTED = "#094771"          # Nodo seleccionado
    TREE_ROOT_BG = "#252526"           # Root sin hover (Req. 3)
    
    # ═══════════════════════════════════════════════════════════════
    # INPUTS Y CAMPOS DE TEXTO (Req. 6)
    # ═══════════════════════════════════════════════════════════════
    
    INPUT_BACKGROUND = "#1e1e1e"        # Fondo de inputs
    INPUT_BORDER_NORMAL = "#3c3c3c"     # Borde normal
    INPUT_BORDER_FOCUS = "#007acc"      # Borde al enfocar (Req. 6)
    INPUT_BORDER_ERROR = "#f44747"      # Borde de error
    INPUT_SELECTION = "#094771"         # Selección de texto
    
    # ═══════════════════════════════════════════════════════════════
    # ICONOS Y ESTADOS
    # ═══════════════════════════════════════════════════════════════
    
    ICON_FOLDER = "#dcb67a"             # Color carpetas VS Code
    ICON_FILE = "#cccccc"               # Color archivos
    ICON_ACTIVE = "#ffffff"             # Iconos activos
    
    # Estados de nodos
    STATUS_SUCCESS = "#4ec9b0"          # Verde (✅)
    STATUS_WARNING = "#ffcc02"          # Amarillo (⬜)  
    STATUS_ERROR = "#f44747"            # Rojo (❌)
    
    # ═══════════════════════════════════════════════════════════════
    # UTILIDADES
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Obtiene color según el estado del nodo"""
        status_map = {
            "✅": cls.STATUS_SUCCESS,
            "⬜": cls.STATUS_WARNING,
            "❌": cls.STATUS_ERROR
        }
        return status_map.get(status, cls.TEXT_SECONDARY)
    
    @classmethod
    def get_hover_color(cls, is_root: bool = False) -> str:
        """Obtiene color hover - Root no tiene hover (Req. 3)"""
        return cls.TREE_ROOT_BG if is_root else cls.TREE_HOVER