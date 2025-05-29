"""
presentation/views/widgets/vscode_widgets.py
============================================

Widgets base con estilo Visual Studio Code
- Text, Entry, Frame, Treeview con tema VS Code
- Focus highlighting automático (Req. 6)
- Hover effects para TreeView (Req. 2, 3)
- Separadores con highlight para columnas (Req. 1)
- 180 líneas - Cumple con límite
"""

import tkinter as tk
from tkinter import ttk
from ..styling.constants.vscode_colors import VSCodeColors

# ═══════════════════════════════════════════════════════════════════════════════════════
# BASE WIDGETS CON TEMA VS CODE
# ═══════════════════════════════════════════════════════════════════════════════════════

class VSCodeFrame(ttk.Frame):
    """Frame con estilo VS Code"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure_style()
    
    def configure_style(self):
        style = ttk.Style()
        style.configure(
            "VSCode.TFrame",
            background=VSCodeColors.BACKGROUND,
            borderwidth=0,
            relief="flat"
        )
        self.configure(style="VSCode.TFrame")

class VSCodeText(tk.Text):
    """Text widget con highlight de foco (Req. 6)"""
    
    def __init__(self, parent, **kwargs):
        # Config VS Code por defecto
        defaults = {
            'bg': VSCodeColors.INPUT_BACKGROUND,
            'fg': VSCodeColors.TEXT_PRIMARY,
            'insertbackground': VSCodeColors.TEXT_PRIMARY,
            'selectbackground': VSCodeColors.INPUT_SELECTION,
            'selectforeground': VSCodeColors.TEXT_PRIMARY,
            'relief': 'solid',
            'borderwidth': 1,
            'highlightthickness': 0,
            'font': ('Consolas', 10)
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        self.setup_focus_highlight()
    
    def setup_focus_highlight(self):
        """Configura highlight automático al enfocar (Req. 6)"""
        
        def on_focus_in(event):
            self.configure(
                highlightthickness=2,
                highlightcolor=VSCodeColors.INPUT_BORDER_FOCUS,
                highlightbackground=VSCodeColors.INPUT_BORDER_FOCUS
            )
        
        def on_focus_out(event):
            self.configure(
                highlightthickness=0
            )
        
        self.bind("<FocusIn>", on_focus_in)
        self.bind("<FocusOut>", on_focus_out)

class VSCodeEntry(tk.Entry):
    """Entry con highlight de foco (Req. 6)"""
    
    def __init__(self, parent, **kwargs):
        defaults = {
            'bg': VSCodeColors.INPUT_BACKGROUND,
            'fg': VSCodeColors.TEXT_PRIMARY,
            'insertbackground': VSCodeColors.TEXT_PRIMARY,
            'selectbackground': VSCodeColors.INPUT_SELECTION,
            'selectforeground': VSCodeColors.TEXT_PRIMARY,
            'relief': 'solid',
            'borderwidth': 1,
            'highlightthickness': 0,
            'font': ('Segoe UI', 9)
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        self.setup_focus_highlight()
    
    def setup_focus_highlight(self):
        """Highlight al enfocar (Req. 6)"""
        
        def on_focus_in(event):
            self.configure(
                highlightthickness=2,
                highlightcolor=VSCodeColors.INPUT_BORDER_FOCUS,
                highlightbackground=VSCodeColors.INPUT_BORDER_FOCUS
            )
        
        def on_focus_out(event):
            self.configure(highlightthickness=0)
        
        self.bind("<FocusIn>", on_focus_in)
        self.bind("<FocusOut>", on_focus_out)

# ═══════════════════════════════════════════════════════════════════════════════════════
# TREEVIEW CON HOVER EFFECTS (Req. 2, 3)
# ═══════════════════════════════════════════════════════════════════════════════════════

class VSCodeTreeView(ttk.Treeview):
    """TreeView con hover effects - Root sin hover (Req. 2, 3)"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.root_items = set()  # Items que son root (sin hover)
        self.hovered_item = None
        self.setup_vscode_style()
        self.setup_hover_effects()
    
    def setup_vscode_style(self):
        """Estilo VS Code para TreeView"""
        style = ttk.Style()
        
        style.configure(
            "VSCode.Treeview",
            background=VSCodeColors.TREE_BACKGROUND,
            foreground=VSCodeColors.TEXT_PRIMARY,
            fieldbackground=VSCodeColors.TREE_BACKGROUND,
            borderwidth=0,
            relief="flat"
        )
        
        style.map(
            "VSCode.Treeview",
            background=[
                ('selected', VSCodeColors.TREE_SELECTED),
                ('!selected', VSCodeColors.TREE_BACKGROUND)
            ]
        )
        
        self.configure(style="VSCode.Treeview")
    
    def setup_hover_effects(self):
        """Hover effects - Root sin hover (Req. 2, 3)"""
        
        def on_motion(event):
            item = self.identify_row(event.y)
            
            # Limpiar hover anterior
            if self.hovered_item and self.hovered_item != item:
                self.clear_hover()
            
            # Aplicar hover solo si NO es root (Req. 3)
            if item and item not in self.root_items:
                self.set_hover(item)
        
        def on_leave(event):
            self.clear_hover()
        
        self.bind("<Motion>", on_motion)
        self.bind("<Leave>", on_leave)
    
    def set_hover(self, item):
        """Aplica hover a item (excepto root)"""
        if item in self.root_items:
            return  # Root no tiene hover (Req. 3)
        
        # Configurar tag hover
        self.tag_configure("hover", background=VSCodeColors.TREE_HOVER)
        
        # Aplicar tag
        current_tags = self.item(item, "tags")
        if "hover" not in current_tags:
            self.item(item, tags=current_tags + ("hover",))
        
        self.hovered_item = item
    
    def clear_hover(self):
        """Limpia efectos hover"""
        if self.hovered_item:
            current_tags = list(self.item(self.hovered_item, "tags"))
            if "hover" in current_tags:
                current_tags.remove("hover")
                self.item(self.hovered_item, tags=current_tags)
        
        self.hovered_item = None
    
    def set_root_item(self, item_id):
        """Marca un item como root (sin hover)"""
        self.root_items.add(item_id)

# ═══════════════════════════════════════════════════════════════════════════════════════
# SEPARADOR REDIMENSIONABLE CON HIGHLIGHT (Req. 1)
# ═══════════════════════════════════════════════════════════════════════════════════════

class ResizableSeparator(tk.Frame):
    """Separador con highlight en toda la línea al redimensionar (Req. 1)"""
    
    def __init__(self, parent, on_resize=None, **kwargs):
        defaults = {
            'width': 4,
            'bg': VSCodeColors.BORDER_NORMAL,
            'cursor': 'sb_h_double_arrow'
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        self.on_resize = on_resize
        self.is_dragging = False
        self.setup_events()
    
    def setup_events(self):
        """Configura eventos de redimensionado (Req. 1)"""
        
        def on_enter(event):
            """Highlight al hacer hover"""
            if not self.is_dragging:
                self.configure(bg=VSCodeColors.SEPARATOR_ACTIVE)
        
        def on_leave(event):
            """Quitar highlight al salir"""
            if not self.is_dragging:
                self.configure(bg=VSCodeColors.BORDER_NORMAL)
        
        def on_button_press(event):
            """Iniciar drag - highlight permanente"""
            self.is_dragging = True
            self.configure(bg=VSCodeColors.SEPARATOR_ACTIVE)
            self.start_x = event.x_root
        
        def on_drag(event):
            """Durante el drag"""
            if self.is_dragging and self.on_resize:
                delta = event.x_root - self.start_x
                self.on_resize(delta)
                self.start_x = event.x_root
        
        def on_release(event):
            """Fin del drag"""
            self.is_dragging = False
            self.configure(bg=VSCodeColors.BORDER_NORMAL)
        
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        self.bind("<Button-1>", on_button_press)
        self.bind("<B1-Motion>", on_drag)
        self.bind("<ButtonRelease-1>", on_release)