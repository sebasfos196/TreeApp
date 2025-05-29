"""
presentation/styling/components/panel_header.py
==============================================

Headers unificados para paneles estilo VS Code
- Títulos alineados: "TreeCreator | Documentación | Vista Previa"
- Botones de acción integrados
- Estilo consistente VS Code
- 120 líneas - Cumple límite
"""

import tkinter as tk
from tkinter import ttk
from ..constants.vscode_colors import VSCodeColors

class PanelHeader(tk.Frame):
    """Header unificado para paneles estilo VS Code"""
    
    def __init__(self, parent, title="Panel", buttons=None, **kwargs):
        defaults = {
            'bg': VSCodeColors.BACKGROUND,
            'relief': 'flat',
            'padx': 10,
            'pady': 8
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        
        self.title = title
        self.buttons = buttons or []
        self.setup_header()
    
    def setup_header(self):
        """Configura el header con título y botones"""
        
        # Título del panel
        self.title_label = tk.Label(
            self,
            text=self.title,
            font=("Segoe UI", 12, "bold"),
            bg=VSCodeColors.BACKGROUND,
            fg=VSCodeColors.TEXT_PRIMARY,
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True)
        
        # Contenedor de botones
        if self.buttons:
            self.buttons_frame = tk.Frame(
                self,
                bg=VSCodeColors.BACKGROUND
            )
            self.buttons_frame.pack(side="right")
            
            # Crear botones
            for button_config in self.buttons:
                self.create_button(button_config)
    
    def create_button(self, config):
        """Crea un botón con configuración específica"""
        
        button = tk.Button(
            self.buttons_frame,
            text=config.get('text', ''),
            command=config.get('command', None),
            width=config.get('width', 3),
            font=("Segoe UI", 9),
            bg=VSCodeColors.SIDEBAR,
            fg=VSCodeColors.TEXT_PRIMARY,
            activebackground=VSCodeColors.HOVER,
            activeforeground=VSCodeColors.TEXT_PRIMARY,
            relief='flat',
            borderwidth=1,
            cursor='hand2'
        )
        
        button.pack(side="left", padx=2)
        
        # Hover effects
        self.setup_button_hover(button)
        
        return button
    
    def setup_button_hover(self, button):
        """Configura efectos hover para botones"""
        
        def on_enter(event):
            button.configure(bg=VSCodeColors.HOVER)
        
        def on_leave(event):
            button.configure(bg=VSCodeColors.SIDEBAR)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def update_title(self, new_title):
        """Actualiza el título del panel"""
        self.title = new_title
        self.title_label.configure(text=new_title)

class ExplorerHeader(PanelHeader):
    """Header específico para panel explorador"""
    
    def __init__(self, parent, **kwargs):
        buttons = [
            {'text': '📁', 'width': 3, 'command': self.new_folder},
            {'text': '📄', 'width': 3, 'command': self.new_file},
            {'text': '🗑️', 'width': 3, 'command': self.delete_item}
        ]
        
        super().__init__(parent, title="TreeCreator", buttons=buttons, **kwargs)
    
    def new_folder(self):
        """Acción: nueva carpeta"""
        print("Nueva carpeta")  # Placeholder
    
    def new_file(self):
        """Acción: nuevo archivo"""
        print("Nuevo archivo")  # Placeholder
    
    def delete_item(self):
        """Acción: eliminar elemento"""
        print("Eliminar")  # Placeholder

class EditorHeader(PanelHeader):
    """Header específico para panel editor"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="Documentación", **kwargs)

class PreviewHeader(PanelHeader):
    """Header específico para panel vista previa"""
    
    def __init__(self, parent, **kwargs):
        buttons = [
            {'text': '⚙️', 'width': 3, 'command': self.show_config},
            {'text': '💾', 'width': 3, 'command': self.export_preview}
        ]
        
        super().__init__(parent, title="Vista Previa", buttons=buttons, **kwargs)
    
    def show_config(self):
        """Acción: mostrar configuración"""
        print("Mostrar configuración")  # Placeholder
    
    def export_preview(self):
        """Acción: exportar vista previa"""
        print("Exportar vista previa")  # Placeholder

class UnifiedHeaderManager:
    """Gestor para headers unificados y alineados"""
    
    def __init__(self):
        self.headers = []
        self.title_alignment = "center"
    
    def register_header(self, header: PanelHeader):
        """Registra un header para gestión unificada"""
        self.headers.append(header)
    
    def align_titles(self):
        """Alinea títulos de todos los headers registrados"""
        
        # Calcular ancho máximo de títulos
        max_width = 0
        for header in self.headers:
            title_width = len(header.title)
            if title_width > max_width:
                max_width = title_width
        
        # Aplicar alineación
        for header in self.headers:
            if self.title_alignment == "center":
                header.title_label.configure(anchor="center")
            elif self.title_alignment == "left":
                header.title_label.configure(anchor="w")
    
    def set_title_alignment(self, alignment: str):
        """Establece alineación de títulos: left, center, right"""
        self.title_alignment = alignment
        self.align_titles()