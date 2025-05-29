"""
presentation/styling/constants/colors.py - VERSIÓN FINAL
=======================================================

Tu archivo colors.py actualizado con:
- Integración completa con VS Code colors
- Mantiene compatibilidad con código existente
- Nuevos colores para funcionalidades FASE 1
- 50 líneas - Cumple límite
"""

# ═══════════════════════════════════════════════════════════════
# IMPORTAR COLORES VS CODE EXACTOS
# ═══════════════════════════════════════════════════════════════

from .vscode_colors import VSCodeColors

# ═══════════════════════════════════════════════════════════════
# COLORES PRINCIPALES - ACTUALIZADOS CON VS CODE
# ═══════════════════════════════════════════════════════════════

# Colores base (mantener nombres existentes para compatibilidad)
BACKGROUND = VSCodeColors.BACKGROUND        # "#1e1e1e"
FOREGROUND = VSCodeColors.TEXT_PRIMARY      # "#cccccc" 
PRIMARY = VSCodeColors.BACKGROUND           # Alias
SECONDARY = VSCodeColors.SIDEBAR            # "#252526"
ACCENT = VSCodeColors.FOCUS                 # "#007acc"

# ═══════════════════════════════════════════════════════════════
# COLORES DE TEXTO
# ═══════════════════════════════════════════════════════════════

TEXT = VSCodeColors.TEXT_PRIMARY            # "#cccccc"
TEXT_SECONDARY = VSCodeColors.TEXT_SECONDARY # "#969696"
TEXT_MUTED = VSCodeColors.TEXT_MUTED        # "#6a6a6a"
TEXT_DISABLED = VSCodeColors.TEXT_DISABLED  # "#3c3c3c"

# ═══════════════════════════════════════════════════════════════
# COLORES DE ESTADO
# ═══════════════════════════════════════════════════════════════

SUCCESS = VSCodeColors.STATUS_SUCCESS       # "#4ec9b0" (✅)
WARNING = VSCodeColors.STATUS_WARNING       # "#ffcc02" (⬜)
ERROR = VSCodeColors.STATUS_ERROR          # "#f44747" (❌)

# ═══════════════════════════════════════════════════════════════
# COLORES INTERACTIVOS - NUEVOS PARA FASE 1
# ═══════════════════════════════════════════════════════════════

HOVER = VSCodeColors.HOVER                  # "#2a2d2e" (Req. 2)
SELECTED = VSCodeColors.SELECTED           # "#094771"
FOCUS = VSCodeColors.FOCUS                 # "#007acc" (Req. 6)
FOCUS_GLOW = VSCodeColors.FOCUS_GLOW       # "rgba(0, 122, 204, 0.4)"

# ═══════════════════════════════════════════════════════════════
# COLORES DE BORDE
# ═══════════════════════════════════════════════════════════════

BORDER = VSCodeColors.BORDER_NORMAL         # "#3c3c3c"
BORDER_ACTIVE = VSCodeColors.BORDER_ACTIVE  # "#007acc" (Req. 1)
SEPARATOR = VSCodeColors.SEPARATOR          # "#2d2d30"
SEPARATOR_ACTIVE = VSCodeColors.SEPARATOR_ACTIVE # "#007acc" (Req. 1)

# ═══════════════════════════════════════════════════════════════
# UTILIDADES DE COMPATIBILIDAD
# ═══════════════════════════════════════════════════════════════

def get_status_color(status: str) -> str:
    """Obtiene color según estado del nodo"""
    return VSCodeColors.get_status_color(status)

def get_hover_color(is_root: bool = False) -> str:
    """Obtiene color hover - Root sin hover (Req. 3)"""
    return VSCodeColors.get_hover_color(is_root)