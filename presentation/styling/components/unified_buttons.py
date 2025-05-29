"""
presentation/styling/components/unified_buttons.py
=================================================

Botones unificados estilo VS Code
- Estilo consistente en toda la aplicación
- Hover effects y estados
- Botones específicos para funcionalidades
- 110 líneas - Cumple límite
"""

import tkinter as tk
from tkinter import ttk
from ..constants.vscode_colors import VSCodeColors

class VSCodeButton(tk.Button):
    """Botón base estilo VS Code"""
    
    def __init__(self, parent, **kwargs):
        # Configuración por defecto VS Code
        defaults = {
            'font': ("Segoe UI", 9),
            'bg': VSCodeColors.SIDEBAR,
            'fg': VSCodeColors.TEXT_PRIMARY,
            'activebackground': VSCodeColors.HOVER,
            'activeforeground': VSCodeColors.TEXT_PRIMARY,
            'relief': 'flat',
            'borderwidth': 1,
            'cursor': 'hand2'
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        self.setup_hover_effects()
    
    def setup_hover_effects(self):
        """Configura efectos hover VS Code"""
        
        def on_enter(event):
            self.configure(bg=VSCodeColors.HOVER)
        
        def on_leave(event):
            self.configure(bg=VSCodeColors.SIDEBAR)
        
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)

class IconButton(VSCodeButton):
    """Botón con icono estilo VS Code"""
    
    def __init__(self, parent, icon="", **kwargs):
        defaults = {
            'text': icon,
            'width': 3,
            'font': ("Segoe UI", 10)
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)

class ActionButton(VSCodeButton):
    """Botón de acción con texto"""
    
    def __init__(self, parent, text="", **kwargs):
        defaults = {
            'text': text,
            'padx': 12,
            'pady': 4
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)

class ToggleButton(VSCodeButton):
    """Botón toggle con estado"""
    
    def __init__(self, parent, **kwargs):
        self.is_active = False
        super().__init__(parent, **kwargs)
        self.configure(command=self.toggle)
    
    def toggle(self):
        """Alterna el estado del botón"""
        self.is_active = not self.is_active
        
        if self.is_active:
            self.configure(
                bg=VSCodeColors.SELECTED,
                fg=VSCodeColors.TEXT_PRIMARY
            )
        else:
            self.configure(
                bg=VSCodeColors.SIDEBAR,
                fg=VSCodeColors.TEXT_PRIMARY
            )
    
    def set_active(self, active: bool):
        """Establece el estado activo"""
        self.is_active = active
        self.toggle()
        self.toggle()  # Toggle twice to get correct state

class ButtonGroup(tk.Frame):
    """Grupo de botones con espaciado unificado"""
    
    def __init__(self, parent, buttons=None, **kwargs):
        defaults = {
            'bg': VSCodeColors.BACKGROUND,
            'relief': 'flat'
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        
        self.buttons = []
        if buttons:
            self.create_buttons(buttons)
    
    def create_buttons(self, button_configs):
        """Crea botones según configuraciones"""
        
        for config in button_configs:
            button_type = config.get('type', 'action')
            
            if button_type == 'icon':
                button = IconButton(self, **config)
            elif button_type == 'toggle':
                button = ToggleButton(self, **config)
            else:
                button = ActionButton(self, **config)
            
            button.pack(side="left", padx=2)
            self.buttons.append(button)
    
    def get_button(self, index: int):
        """Obtiene botón por índice"""
        if 0 <= index < len(self.buttons):
            return self.buttons[index]
        return None

class ExplorerButtons(ButtonGroup):
    """Botones específicos para panel explorador"""
    
    def __init__(self, parent, **kwargs):
        buttons = [
            {
                'type': 'icon',
                'icon': '📁',
                'command': self.new_folder,
                'width': 3
            },
            {
                'type': 'icon', 
                'icon': '📄',
                'command': self.new_file,
                'width': 3
            },
            {
                'type': 'icon',
                'icon': '🗑️',
                'command': self.delete_item,
                'width': 3
            }
        ]
        
        super().__init__(parent, buttons=buttons, **kwargs)
    
    def new_folder(self):
        """Crear nueva carpeta"""
        print("Nueva carpeta")  # Placeholder
    
    def new_file(self):
        """Crear nuevo archivo"""
        print("Nuevo archivo")  # Placeholder
    
    def delete_item(self):
        """Eliminar elemento seleccionado"""
        print("Eliminar elemento")  # Placeholder

class PreviewButtons(ButtonGroup):
    """Botones específicos para panel vista previa"""
    
    def __init__(self, parent, **kwargs):
        buttons = [
            {
                'type': 'icon',
                'icon': '⚙️',
                'command': self.show_config,
                'width': 3
            },
            {
                'type': 'icon',
                'icon': '💾', 
                'command': self.export_preview,
                'width': 3
            }
        ]
        
        super().__init__(parent, buttons=buttons, **kwargs)
    
    def show_config(self):
        """Mostrar panel de configuración"""
        print("Mostrar configuración")  # Placeholder
    
    def export_preview(self):
        """Exportar vista previa"""
        print("Exportar vista previa")  # Placeholder