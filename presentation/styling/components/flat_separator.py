"""
presentation/styling/components/flat_separator.py
================================================

Separadores flat estilo VS Code
- Separadores sutiles entre paneles
- Separadores redimensionables con highlight (Req. 1)
- Integración con tema VS Code
- 85 líneas - Cumple límite
"""

import tkinter as tk
from tkinter import ttk
from ..constants.vscode_colors import VSCodeColors

class FlatSeparator(ttk.Separator):
    """Separador flat estilo VS Code"""
    
    def __init__(self, parent, orient="horizontal", **kwargs):
        super().__init__(parent, orient=orient, **kwargs)
        self.setup_vscode_style()
    
    def setup_vscode_style(self):
        """Aplica estilo VS Code al separador"""
        
        style = ttk.Style()
        style.configure(
            "VSCodeFlat.TSeparator",
            background=VSCodeColors.SEPARATOR
        )
        
        self.configure(style="VSCodeFlat.TSeparator")

class ResizableFlatSeparator(tk.Frame):
    """Separador redimensionable con highlight flat (Req. 1)"""
    
    def __init__(self, parent, on_resize=None, orient="vertical", **kwargs):
        
        # Configuración según orientación
        if orient == "vertical":
            defaults = {
                'width': 2,
                'cursor': 'sb_h_double_arrow',
                'bg': VSCodeColors.SEPARATOR
            }
        else:
            defaults = {
                'height': 2,
                'cursor': 'sb_v_double_arrow',
                'bg': VSCodeColors.SEPARATOR
            }
        
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
        self.on_resize = on_resize
        self.orient = orient
        self.is_dragging = False
        self.is_hovering = False
        
        self.setup_events()
    
    def setup_events(self):
        """Configura eventos de redimensionado y hover (Req. 1)"""
        
        def on_enter(event):
            """Highlight sutil al hacer hover"""
            if not self.is_dragging:
                self.is_hovering = True
                self.configure(bg=VSCodeColors.BORDER_HIGHLIGHT)
        
        def on_leave(event):
            """Quitar highlight al salir"""
            if not self.is_dragging:
                self.is_hovering = False
                self.configure(bg=VSCodeColors.SEPARATOR)
        
        def on_button_press(event):
            """Iniciar drag - highlight activo"""
            self.is_dragging = True
            self.configure(bg=VSCodeColors.SEPARATOR_ACTIVE)
            
            if self.orient == "vertical":
                self.start_pos = event.x_root
            else:
                self.start_pos = event.y_root
        
        def on_drag(event):
            """Durante el drag con highlight activo"""
            if self.is_dragging and self.on_resize:
                if self.orient == "vertical":
                    delta = event.x_root - self.start_pos
                    self.start_pos = event.x_root
                else:
                    delta = event.y_root - self.start_pos
                    self.start_pos = event.y_root
                
                self.on_resize(delta)
        
        def on_release(event):
            """Fin del drag - volver a estado normal"""
            self.is_dragging = False
            
            # Volver al color apropiado
            if self.is_hovering:
                self.configure(bg=VSCodeColors.BORDER_HIGHLIGHT)
            else:
                self.configure(bg=VSCodeColors.SEPARATOR)
        
        # Bind events
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        self.bind("<Button-1>", on_button_press)
        self.bind("<B1-Motion>", on_drag)
        self.bind("<ButtonRelease-1>", on_release)

class PanelSeparator(tk.Frame):
    """Separador específico entre paneles principales"""
    
    def __init__(self, parent, **kwargs):
        defaults = {
            'width': 1,
            'bg': VSCodeColors.BORDER_NORMAL,
            'relief': 'flat'
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)