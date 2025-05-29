"""
presentation/styling/components/modern_splitters.py
==================================================

Splitters modernos estilo Sonnet/Claude
- Líneas ultra-finas elegantes
- Hover effects suaves
- Completamente flat, sin relieves 3D
- 40 líneas - Reutilizable globalmente
"""

import tkinter as tk
from ..constants.modern_colors import ModernColors

class ModernSplitter(tk.Frame):
    """Splitter moderno estilo Sonnet - línea ultra-fina con hover elegante"""
    
    def __init__(self, parent, orientation="vertical", on_drag=None, **kwargs):
        # Configuración base moderna
        defaults = {
            'bg': 'transparent',
            'relief': 'flat',
            'bd': 0,
            'highlightthickness': 0
        }
        
        if orientation == "vertical":
            defaults.update({'width': 1, 'cursor': 'sb_h_double_arrow'})
        else:
            defaults.update({'height': 1, 'cursor': 'sb_v_double_arrow'})
            
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
        self.orientation = orientation
        self.on_drag = on_drag
        self.is_hovering = False
        self.is_dragging = False
        
        self._setup_modern_behavior()
    
    def _setup_modern_behavior(self):
        """Configura comportamiento moderno del splitter"""
        
        # Estados hover modernos
        def on_enter(event):
            self.is_hovering = True
            self._update_appearance()
        
        def on_leave(event):
            self.is_hovering = False
            if not self.is_dragging:
                self._update_appearance()
        
        # Drag behavior suave
        def on_button_press(event):
            self.is_dragging = True
            self._update_appearance()
            if self.orientation == "vertical":
                self.start_pos = event.x_root
            else:
                self.start_pos = event.y_root
        
        def on_drag_motion(event):
            if self.is_dragging and self.on_drag:
                if self.orientation == "vertical":
                    delta = event.x_root - self.start_pos
                    self.start_pos = event.x_root
                else:
                    delta = event.y_root - self.start_pos  
                    self.start_pos = event.y_root
                self.on_drag(delta)
        
        def on_button_release(event):
            self.is_dragging = False
            self._update_appearance()
        
        # Bind events
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        self.bind("<Button-1>", on_button_press)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<ButtonRelease-1>", on_button_release)
    
    def _update_appearance(self):
        """Actualiza apariencia según estado - estilo Sonnet"""
        
        if self.is_dragging or self.is_hovering:
            # Línea azul sutil en hover/drag
            self.configure(
                bg=ModernColors.DARK_ACCENT,
                width=2 if self.orientation == "vertical" else 1,
                height=1 if self.orientation == "vertical" else 2
            )
        else:
            # Invisible/transparente en estado normal
            self.configure(
                bg=ModernColors.DARK_SEPARATOR,
                width=1,
                height=1
            )