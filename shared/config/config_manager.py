# shared/config/config_manager.py
"""
Gestor de configuración centralizado para TreeCreator.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Gestor centralizado de configuración de la aplicación."""
    
    def __init__(self, config_file: str = "treeapp_config.json"):
        self.config_file = Path(config_file)
        self.config_data: Dict[str, Any] = {}
        self._load_default_config()
        self._load_user_config()
    
    def _load_default_config(self):
        """Cargar configuración por defecto."""
        self.config_data = {
            "app": {
                "version": "4.0.0",
                "name": "TreeCreator",
                "window_width": 1400,
                "window_height": 800,
                "remember_window_state": True
            },
            "tree_panel": {
                "auto_expand_new_folders": True,
                "show_line_numbers": False,
                "double_click_action": "inline_edit",  # "inline_edit" | "expand_collapse"
                "drag_drop_enabled": True,
                "context_menu_enabled": True
            },
            "preview_panel": {
                "default_mode": "Clásico",
                "auto_refresh": True,
                "font_family": "Consolas",
                "font_size": 10,
                "modes": {
                    "classic": {
                        "indent_spaces": 4,
                        "show_icons": True,
                        "show_status": True,
                        "show_markdown": True,
                        "markdown_max_length": 50,
                        "max_depth": 10
                    },
                    "ascii_full": {
                        "show_icons": True,
                        "show_status": True,
                        "show_markdown": True,
                        "markdown_max_length": 40,
                        "use_unicode": True,
                        "max_depth": 10
                    },
                    "ascii_folders": {
                        "show_icons": True,
                        "show_file_count": True,
                        "markdown_max_length": 40,
                        "max_depth": 10
                    },
                    "columns": {
                        "col_path_width": 200,
                        "col_status_width": 80,
                        "col_markdown_width": 300,
                        "show_headers": True,
                        "alternate_colors": True,
                        "markdown_max_length": 60
                    }
                }
            },
            "editor_panel": {
                "auto_save_delay": 500,
                "font_family": "Arial",
                "font_size": 10,
                "syntax_highlighting": True,
                "line_numbers": True
            },
            "validation": {
                "max_filename_length": 255,
                "forbidden_chars": r'[<>:"/\\|?*]',
                "reserved_names": ["CON", "PRN", "AUX", "NUL"],
                "allow_hidden_files": True
            },
            "file_templates": {
                "include_timestamp": True,
                "include_generator_comment": True,
                "custom_templates": {}
            },
            "theme": {
                "primary_color": "#3498db",
                "secondary_color": "#2c3e50",
                "success_color": "#27ae60",
                "error_color": "#e74c3c",
                "warning_color": "#f39c12",
                "background_color": "#f8f8f8"
            }
        }
    
    def _load_user_config(self):
        """Cargar configuración del usuario desde archivo."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(self.config_data, user_config)
                print(f"✅ Configuración cargada desde {self.config_file}")
            except Exception as e:
                print(f"❌ Error cargando configuración: {e}")
                self._create_backup_config()
    
    def _merge_config(self, default: Dict, user: Dict):
        """Fusionar configuración de usuario con la por defecto."""
        for key, value in user.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
    
    def save_config(self):
        """Guardar configuración actual a archivo."""
        try:
            # Crear directorio si no existe
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuración guardada en {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            return False
    
    def _create_backup_config(self):
        """Crear respaldo de configuración corrupta."""
        if self.config_file.exists():
            backup_file = self.config_file.with_suffix('.json.backup')
            try:
                self.config_file.rename(backup_file)
                print(f"⚠️ Configuración corrupta respaldada como {backup_file}")
            except Exception as e:
                print(f"❌ Error creando respaldo: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtener valor de configuración usando notación de punto.
        
        Ejemplo: get("preview_panel.modes.classic.indent_spaces")
        """
        keys = key_path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Establecer valor de configuración usando notación de punto.
        
        Ejemplo: set("preview_panel.modes.classic.indent_spaces", 6)
        """
        keys = key_path.split('.')
        current = self.config_data
        
        try:
            # Navegar hasta el penúltimo nivel
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Establecer el valor final
            current[keys[-1]] = value
            return True
            
        except Exception as e:
            print(f"❌ Error estableciendo configuración {key_path}: {e}")
            return False
    
    def get_preview_config(self, mode: str) -> Dict[str, Any]:
        """Obtener configuración específica para un modo de vista previa."""
        mode_key = mode.lower().replace(' ', '_').replace('ascii_completo', 'ascii_full').replace('solo_carpetas', 'folders')
        return self.get(f"preview_panel.modes.{mode_key}", {})
    
    def set_preview_config(self, mode: str, config: Dict[str, Any]) -> bool:
        """Establecer configuración para un modo de vista previa."""
        mode_key = mode.lower().replace(' ', '_').replace('ascii_completo', 'ascii_full').replace('solo_carpetas', 'folders')
        return self.set(f"preview_panel.modes.{mode_key}", config)
    
    def reset_to_defaults(self):
        """Restablecer configuración a valores por defecto."""
        self._load_default_config()
        return self.save_config()
    
    def export_config(self, export_file: str) -> bool:
        """Exportar configuración a archivo específico."""
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error exportando configuración: {e}")
            return False
    
    def import_config(self, import_file: str) -> bool:
        """Importar configuración desde archivo."""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                self._merge_config(self.config_data, imported_config)
            return self.save_config()
        except Exception as e:
            print(f"❌ Error importando configuración: {e}")
            return False
    
    def get_window_config(self) -> Dict[str, Any]:
        """Obtener configuración de ventana."""
        return {
            'width': self.get('app.window_width', 1400),
            'height': self.get('app.window_height', 800),
            'remember_state': self.get('app.remember_window_state', True)
        }
    
    def save_window_state(self, width: int, height: int, x: int = None, y: int = None):
        """Guardar estado de ventana."""
        self.set('app.window_width', width)
        self.set('app.window_height', height)
        
        if x is not None:
            self.set('app.window_x', x)
        if y is not None:
            self.set('app.window_y', y)
        
        self.save_config()


# Instancia global del gestor de configuración
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Obtener instancia global del gestor de configuración."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


# Ejemplo de uso:
if __name__ == "__main__":
    config = get_config_manager()
    
    # Obtener valores
    print(f"Espacios de indentación: {config.get('preview_panel.modes.classic.indent_spaces')}")
    print(f"Mostrar iconos: {config.get('preview_panel.modes.classic.show_icons')}")
    
    # Establecer valores
    config.set('preview_panel.modes.classic.indent_spaces', 6)
    config.set('app.window_width', 1600)
    
    # Guardar configuración
    config.save_config()