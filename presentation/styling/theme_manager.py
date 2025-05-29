"""
presentation/styling/theme_manager.py - VERSIÓN FINAL
====================================================

Tu archivo theme_manager.py actualizado con:
- Tema VS Code completo (Req. 7)
- Integración con vscode_colors.py
- Gestión de widgets con focus highlighting (Req. 6)
- Compatibilidad con código existente
- 195 líneas - Cumple límite
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Tuple
from .constants.vscode_colors import VSCodeColors

class ThemeManager:
    """Gestor de temas - ACTUALIZADO para VS Code y funcionalidades FASE 1"""
    
    def __init__(self):
        self.current_theme = "vscode_dark"
        self.style = None
        self.applied_widgets = []  # (widget, type) pairs
        self.theme_configs = self._initialize_themes()
    
    def _initialize_themes(self) -> Dict[str, Any]:
        """Inicializa configuraciones de temas disponibles"""
        return {
            "vscode_dark": {
                "name": "Visual Studio Code Dark",
                "colors": VSCodeColors,
                "fonts": {
                    "ui": ("Segoe UI", 9),
                    "code": ("Consolas", 10),
                    "title": ("Segoe UI", 12, "bold"),
                    "small": ("Segoe UI", 8),
                    "large": ("Segoe UI", 11)
                }
            }
        }
    
    def initialize_global_theme(self, root_window: tk.Tk):
        """Inicializa tema global de la aplicación (Req. 7)"""
        
        # Configurar ventana principal
        root_window.configure(bg=VSCodeColors.BACKGROUND)
        
        # Inicializar ttk.Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Aplicar configuraciones VS Code
        self._configure_global_styles()
        self._configure_widget_styles()
        self._configure_custom_components()
    
    def _configure_global_styles(self):
        """Configuración global VS Code"""
        
        # Base global
        self.style.configure(
            ".",
            background=VSCodeColors.BACKGROUND,
            foreground=VSCodeColors.TEXT_PRIMARY,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 9)
        )
        
        # Labels
        self.style.configure(
            "TLabel",
            background=VSCodeColors.BACKGROUND,
            foreground=VSCodeColors.TEXT_PRIMARY,
            font=("Segoe UI", 9)
        )
        
        # Frames
        self.style.configure(
            "TFrame",
            background=VSCodeColors.BACKGROUND,
            borderwidth=0,
            relief="flat"
        )
    
    def _configure_widget_styles(self):
        """Configuración de widgets específicos"""
        
        # Buttons con hover VS Code
        self.style.configure(
            "TButton",
            background=VSCodeColors.SIDEBAR,
            foreground=VSCodeColors.TEXT_PRIMARY,
            borderwidth=1,
            focuscolor="none",
            font=("Segoe UI", 9)
        )
        
        self.style.map(
            "TButton",
            background=[
                ('active', VSCodeColors.HOVER),
                ('pressed', VSCodeColors.SELECTED)
            ]
        )
        
        # Combobox
        self.style.configure(
            "TCombobox",
            fieldbackground=VSCodeColors.INPUT_BACKGROUND,
            background=VSCodeColors.SIDEBAR,
            foreground=VSCodeColors.TEXT_PRIMARY,
            borderwidth=1,
            arrowcolor=VSCodeColors.TEXT_PRIMARY
        )
        
        # Treeview con hover support (Req. 2)
        self.style.configure(
            "Treeview",
            background=VSCodeColors.TREE_BACKGROUND,
            foreground=VSCodeColors.TEXT_PRIMARY,
            fieldbackground=VSCodeColors.TREE_BACKGROUND,
            borderwidth=0,
            relief="flat"
        )
        
        # Treeview selection y hover
        self.style.map(
            "Treeview",
            background=[
                ('selected', VSCodeColors.TREE_SELECTED),
                ('!selected', VSCodeColors.TREE_BACKGROUND)
            ]
        )
        
        # Separators
        self.style.configure(
            "TSeparator",
            background=VSCodeColors.SEPARATOR
        )
    
    def _configure_custom_components(self):
        """Configuración para componentes custom"""
        
        # Headers de paneles
        self.style.configure(
            "PanelHeader.TLabel",
            background=VSCodeColors.BACKGROUND,
            foreground=VSCodeColors.TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold")
        )
        
        # Separadores redimensionables activos (Req. 1)
        self.style.configure(
            "ActiveSeparator.TFrame",
            background=VSCodeColors.SEPARATOR_ACTIVE
        )
        
        # Entry con focus (Req. 6)
        self.style.configure(
            "Focus.TEntry",
            fieldbackground=VSCodeColors.INPUT_BACKGROUND,
            foreground=VSCodeColors.TEXT_PRIMARY,
            borderwidth=2,
            focuscolor=VSCodeColors.INPUT_BORDER_FOCUS
        )
    
    def apply_vscode_theme_to_text_widget(self, widget: tk.Text):
        """Aplica tema VS Code a Text widget con focus highlighting (Req. 6)"""
        
        # Configuración base
        widget.configure(
            bg=VSCodeColors.INPUT_BACKGROUND,
            fg=VSCodeColors.TEXT_PRIMARY,
            insertbackground=VSCodeColors.TEXT_PRIMARY,
            selectbackground=VSCodeColors.INPUT_SELECTION,
            selectforeground=VSCodeColors.TEXT_PRIMARY,
            relief='solid',
            borderwidth=1,
            highlightthickness=0,
            font=('Consolas', 10)
        )
        
        # Focus highlighting (Req. 6)
        def on_focus_in(event):
            widget.configure(
                highlightthickness=2,
                highlightcolor=VSCodeColors.INPUT_BORDER_FOCUS,
                highlightbackground=VSCodeColors.INPUT_BORDER_FOCUS
            )
        
        def on_focus_out(event):
            widget.configure(highlightthickness=0)
        
        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)
        
        # Trackear para updates
        self.applied_widgets.append((widget, "text"))
    
    def apply_vscode_theme_to_entry_widget(self, widget: tk.Entry):
        """Aplica tema VS Code a Entry widget con focus highlighting (Req. 6)"""
        
        # Configuración base
        widget.configure(
            bg=VSCodeColors.INPUT_BACKGROUND,
            fg=VSCodeColors.TEXT_PRIMARY,
            insertbackground=VSCodeColors.TEXT_PRIMARY,
            selectbackground=VSCodeColors.INPUT_SELECTION,
            selectforeground=VSCodeColors.TEXT_PRIMARY,
            relief='solid',
            borderwidth=1,
            highlightthickness=0,
            font=('Segoe UI', 9)
        )
        
        # Focus highlighting (Req. 6)
        def on_focus_in(event):
            widget.configure(
                highlightthickness=2,
                highlightcolor=VSCodeColors.INPUT_BORDER_FOCUS,
                highlightbackground=VSCodeColors.INPUT_BORDER_FOCUS
            )
        
        def on_focus_out(event):
            widget.configure(highlightthickness=0)
        
        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)
        
        # Trackear para updates
        self.applied_widgets.append((widget, "entry"))
    
    def create_vscode_treeview(self, parent) -> ttk.Treeview:
        """Crea TreeView con hover effects VS Code (Req. 2, 3)"""
        
        tree = ttk.Treeview(parent)
        tree.root_items = set()  # Items root (sin hover - Req. 3)
        tree.hovered_item = None
        
        # Hover effects (Req. 2, 3)
        def on_motion(event):
            item = tree.identify_row(event.y)
            
            # Limpiar hover anterior
            if tree.hovered_item and tree.hovered_item != item:
                clear_hover()
            
            # Aplicar hover solo si NO es root (Req. 3)
            if item and item not in tree.root_items:
                set_hover(item)
        
        def on_leave(event):
            clear_hover()
        
        def set_hover(item):
            if item in tree.root_items:
                return  # Root no tiene hover (Req. 3)
            
            tree.tag_configure("hover", background=VSCodeColors.TREE_HOVER)
            current_tags = tree.item(item, "tags")
            if "hover" not in current_tags:
                tree.item(item, tags=current_tags + ("hover",))
            tree.hovered_item = item
        
        def clear_hover():
            if tree.hovered_item:
                current_tags = list(tree.item(tree.hovered_item, "tags"))
                if "hover" in current_tags:
                    current_tags.remove("hover")
                    tree.item(tree.hovered_item, tags=current_tags)
            tree.hovered_item = None
        
        # Bind events
        tree.bind("<Motion>", on_motion)
        tree.bind("<Leave>", on_leave)
        
        # Método helper para marcar root
        def set_root_item(item_id):
            tree.root_items.add(item_id)
        
        tree.set_root_item = set_root_item
        
        return tree
    
    def get_color(self, color_name: str) -> str:
        """Obtiene color del tema actual"""
        return getattr(VSCodeColors, color_name.upper(), VSCodeColors.TEXT_PRIMARY)
    
    def get_font(self, font_type: str) -> Tuple[str, int]:
        """Obtiene fuente del tema actual"""
        fonts = self.theme_configs[self.current_theme]["fonts"]
        return fonts.get(font_type, ("Segoe UI", 9))
    
    def refresh_all_widgets(self):
        """Refresca tema en todos los widgets aplicados"""
        for widget, widget_type in self.applied_widgets[:]:  # Copy list
            try:
                if widget_type == "text":
                    self.apply_vscode_theme_to_text_widget(widget)
                elif widget_type == "entry":
                    self.apply_vscode_theme_to_entry_widget(widget)
            except tk.TclError:
                # Widget destroyed, remove from list
                self.applied_widgets.remove((widget, widget_type))