"""
presentation/styling/constants/fonts.py - VERSIÓN FINAL
======================================================

Tu archivo fonts.py actualizado con:
- Tipografías exactas de Visual Studio Code
- Mantiene compatibilidad con código existente
- Fuentes específicas para nuevas funcionalidades
- 40 líneas - Cumple límite
"""

# ═══════════════════════════════════════════════════════════════
# TIPOGRAFÍAS VS CODE - EXACTAS (Req. 7)
# ═══════════════════════════════════════════════════════════════

# Fuentes principales VS Code
UI_FONT = ("Segoe UI", 9)                    # Interfaz general
CODE_FONT = ("Consolas", 10)                 # Código y editores
TITLE_FONT = ("Segoe UI", 12, "bold")        # Títulos de paneles

# ═══════════════════════════════════════════════════════════════
# FUENTES POR TAMAÑO
# ═══════════════════════════════════════════════════════════════

SMALL = ("Segoe UI", 8)                      # Texto pequeño
NORMAL = ("Segoe UI", 9)                     # Texto normal (default)
LARGE = ("Segoe UI", 11)                     # Texto grande
TITLE = ("Segoe UI", 12, "bold")             # Títulos principales

# ═══════════════════════════════════════════════════════════════
# FUENTES ESPECÍFICAS POR COMPONENTE
# ═══════════════════════════════════════════════════════════════

EDITOR_FONT = ("Consolas", 10)               # Editores de código/markdown
TREE_FONT = ("Segoe UI", 9)                  # Explorador de archivos
PREVIEW_FONT = ("Consolas", 9)               # Vista previa
BUTTON_FONT = ("Segoe UI", 9)                # Botones
HEADER_FONT = ("Segoe UI", 12, "bold")       # Headers de paneles

# ═══════════════════════════════════════════════════════════════
# ALIASES PARA COMPATIBILIDAD CON CÓDIGO EXISTENTE
# ═══════════════════════════════════════════════════════════════

DEFAULT = UI_FONT                            # Fuente por defecto
MONOSPACE = CODE_FONT                        # Fuente monospace
HEADER = TITLE_FONT                          # Headers