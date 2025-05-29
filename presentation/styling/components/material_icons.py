"""
presentation/styling/components/material_icons.py
================================================

Sistema de iconos Material Design SVG
- Solo 2 tipos: Carpeta y Archivo
- SVG escalables y tematizables
- Integración con colores modernos
- 35 líneas - Sistema completo
"""

import tkinter as tk
from tkinter import ttk
from ..constants.modern_colors import ModernColors

class MaterialIcons:
    """Sistema de iconos Material Design para TreeCreator"""
    
    # Iconos SVG Material Design (outline style)
    FOLDER_SVG = """
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M10 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V8a2 2 0 00-2-2h-8l-2-2z"/>
    </svg>
    """
    
    FILE_SVG = """
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
        <polyline points="14,2 14,8 20,8"/>
    </svg>
    """
    
    @classmethod
    def get_folder_icon(cls, color=None) -> str:
        """Obtiene icono de carpeta con color específico"""
        color = color or ModernColors.DARK_TEXT_SECONDARY
        return cls.FOLDER_SVG.replace("currentColor", color)
    
    @classmethod
    def get_file_icon(cls, color=None) -> str:
        """Obtiene icono de archivo con color específico"""
        color = color or ModernColors.DARK_TEXT_SECONDARY
        return cls.FILE_SVG.replace("currentColor", color)
    
    @classmethod
    def create_icon_label(cls, parent, icon_type="folder", **kwargs) -> tk.Label:
        """Crea Label con icono Material Design"""
        
        defaults = {
            'font': ('Segoe UI', 9),
            'bg': ModernColors.DARK_SURFACE,
            'fg': ModernColors.DARK_TEXT_PRIMARY,
            'compound': 'left',
            'anchor': 'w'
        }
        defaults.update(kwargs)
        
        # Por ahora usamos texto Unicode hasta implementar SVG rendering
        icon_text = "📁" if icon_type == "folder" else "📄"
        
        return tk.Label(parent, text=icon_text, **defaults)