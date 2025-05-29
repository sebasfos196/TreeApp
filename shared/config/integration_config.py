"""
shared/config/integration_config.py
===================================

Configuración de integración para FASE 1
- Configuración de funcionalidades específicas
- Constantes para comportamiento UX
- Integración de componentes VS Code
- 85 líneas - Within limit
"""

class IntegrationConfig:
    """Configuración para integración de funcionalidades FASE 1"""
    
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE WORKSPACE INICIAL (Req. 4, 5)
    # ═══════════════════════════════════════════════════════════════
    
    INITIAL_WORKSPACE = {
        'root_name': 'Root',
        'root_status': '⬜',  # Pendiente
        'root_markdown': '# Nueva carpeta raíz',
        'root_notes': 'Carpeta raíz del proyecto inicial',
        'auto_create': True,  # Crear automáticamente al iniciar
        'show_in_preview': True  # Mostrar inmediatamente en vista previa
    }
    
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE HOVER EFFECTS (Req. 2, 3)
    # ═══════════════════════════════════════════════════════════════
    
    HOVER_CONFIG = {
        'enable_hover': True,
        'root_hover': False,  # Root NO tiene hover (Req. 3)
        'hover_delay': 0,     # Sin delay
        'hover_color': '#2a2d2e',  # Color VS Code
        'hover_border': False,
        'clear_on_leave': True
    }
    
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE FOCUS HIGHLIGHTING (Req. 6)
    # ═══════════════════════════════════════════════════════════════
    
    FOCUS_CONFIG = {
        'enable_focus_highlight': True,
        'focus_color': '#007acc',  # Azul VS Code
        'focus_thickness': 2,
        'focus_glow': True,
        'auto_clear': True  # Limpiar al perder foco
    }
    
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE COLUMNAS REDIMENSIONABLES (Req. 1)
    # ═══════════════════════════════════════════════════════════════
    
    COLUMN_RESIZE_CONFIG = {
        'enable_highlight': True,
        'separator_width': 4,
        'normal_color': '#3c3c3c',
        'active_color': '#007acc',  # Highlight color VS Code
        'min_column_width': 200,
        'resize_cursor': 'sb_h_double_arrow',
        'smooth_resize': True
    }
    
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE TEMA VS CODE (Req. 7)
    # ═══════════════════════════════════════════════════════════════
    
    VSCODE_THEME_CONFIG = {
        'apply_global_theme': True,
        'dark_mode': True,
        'use_exact_colors': True,
        'apply_to_widgets': True,
        'custom_fonts': {
            'ui_font': ('Segoe UI', 9),
            'code_font': ('Consolas', 10),
            'title_font': ('Segoe UI', 12, 'bold')
        }
    }
    
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE ACTUALIZACIÓN EN TIEMPO REAL
    # ═══════════════════════════════════════════════════════════════
    
    REALTIME_CONFIG = {
        'enable_realtime_updates': True,
        'update_delay': 100,  # ms
        'batch_updates': True,
        'update_preview_on_change': True,
        'update_tree_on_change': True,
        'auto_save_delay': 500  # ms
    }
    
    # ═══════════════════════════════════════════════════════════════
    # UTILIDADES
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def get_config_section(cls, section_name: str) -> dict:
        """Obtiene una sección de configuración específica"""
        
        config_map = {
            'workspace': cls.INITIAL_WORKSPACE,
            'hover': cls.HOVER_CONFIG,
            'focus': cls.FOCUS_CONFIG,
            'columns': cls.COLUMN_RESIZE_CONFIG,
            'theme': cls.VSCODE_THEME_CONFIG,
            'realtime': cls.REALTIME_CONFIG
        }
        
        return config_map.get(section_name, {})
    
    @classmethod
    def is_feature_enabled(cls, feature_name: str) -> bool:
        """Verifica si una funcionalidad está habilitada"""
        
        feature_map = {
            'hover': cls.HOVER_CONFIG.get('enable_hover', True),
            'focus_highlight': cls.FOCUS_CONFIG.get('enable_focus_highlight', True),
            'column_highlight': cls.COLUMN_RESIZE_CONFIG.get('enable_highlight', True),
            'realtime_updates': cls.REALTIME_CONFIG.get('enable_realtime_updates', True),
            'vscode_theme': cls.VSCODE_THEME_CONFIG.get('apply_global_theme', True)
        }
        
        return feature_map.get(feature_name, False)