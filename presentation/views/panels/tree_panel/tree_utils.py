# presentation/views/panels/tree_panel/tree_utils.py
"""
Utilidades y helpers para TreeView - iconos, validaciones, formateo.
"""
from typing import Dict, Optional
import re
from datetime import datetime
from domain.node.node_entity import Node


class FlatIcons:
    """Iconos flat modernos para el explorador."""
    
    # Iconos principales
    FOLDER_CLOSED = "📁"
    FOLDER_OPEN = "📂" 
    FILE = "📄"
    
    # Iconos por tipo de archivo
    FILE_TYPES = {
        '.py': '🐍',
        '.js': '📜',
        '.ts': '📜',
        '.html': '🌐',
        '.css': '🎨',
        '.md': '📝',
        '.json': '⚙️',
        '.txt': '📄',
        '.pdf': '📑',
        '.png': '🖼️',
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.gif': '🖼️',
        '.svg': '🖼️',
        '.zip': '📦',
        '.rar': '📦',
        '.7z': '📦',
        '.exe': '⚡',
        '.bat': '⚡',
        '.sh': '⚡',
        '.xml': '📋',
        '.yml': '⚙️',
        '.yaml': '⚙️',
        '.rs': '🦀',
        '.go': '🐹',
        '.java': '☕',
        '.cpp': '⚙️',
        '.c': '⚙️',
        '.php': '🐘',
        '.rb': '💎',
        '.swift': '🐦',
        '.kt': '🎯'
    }
    
    @classmethod
    def get_file_icon(cls, filename: str) -> str:
        """Obtener icono específico según extensión del archivo."""
        if not filename:
            return cls.FILE
        
        # Obtener extensión
        parts = filename.split('.')
        if len(parts) > 1:
            ext = '.' + parts[-1].lower()
            return cls.FILE_TYPES.get(ext, cls.FILE)
        
        return cls.FILE


class NodeValidator:
    """Validador centralizado para nombres de nodos."""
    
    # Caracteres prohibidos en nombres de archivos/carpetas
    FORBIDDEN_CHARS = r'[<>:"/\\|?*]'
    RESERVED_NAMES = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 
                      'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 
                      'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 
                      'LPT7', 'LPT8', 'LPT9']
    
    @classmethod
    def validate_name(cls, name: str, parent_id: Optional[str] = None, 
                     current_node_id: Optional[str] = None, 
                     node_repository=None) -> tuple[bool, str]:
        """
        Validar nombre de nodo de forma completa.
        
        Returns:
            tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not name or not name.strip():
            return False, "El nombre no puede estar vacío"
        
        name = name.strip()
        
        # Longitud máxima
        if len(name) > 255:
            return False, "El nombre no puede exceder 255 caracteres"
        
        # Caracteres prohibidos
        if re.search(cls.FORBIDDEN_CHARS, name):
            return False, "El nombre contiene caracteres prohibidos:\n< > : \" / \\ | ? *"
        
        # Nombres reservados del sistema
        if name.upper() in cls.RESERVED_NAMES:
            return False, f"'{name}' es un nombre reservado del sistema"
        
        # Solo puntos
        if name.startswith('.') and len(name.strip('.')) == 0:
            return False, "El nombre no puede consistir solo de puntos"
        
        # Verificar duplicados si se proporciona repositorio
        if parent_id and node_repository:
            try:
                siblings = node_repository.find_children(parent_id)
                for sibling in siblings:
                    # Excluir el propio nodo en caso de renombrado
                    if current_node_id and sibling.node_id == current_node_id:
                        continue
                    if sibling.name.lower() == name.lower():
                        return False, f"Ya existe un elemento con el nombre '{name}'"
            except Exception as e:
                print(f"❌ Error verificando duplicados: {e}")
                # Continuar sin verificación si hay error
        
        return True, ""


class FileTemplateGenerator:
    """Generador de plantillas de código por extensión."""
    
    @staticmethod
    def generate_template(filename: str) -> str:
        """Generar código plantilla según la extensión del archivo."""
        # Obtener extensión
        parts = filename.split('.')
        if len(parts) < 2:
            return f"# Contenido de {filename}\n"
        
        ext = parts[-1].lower()
        timestamp = datetime.now().isoformat()
        
        # Plantillas por extensión
        templates = {
            'py': f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{filename} - Archivo Python generado automáticamente por TreeCreator
Creado: {timestamp}
"""

def main():
    """Función principal."""
    print("Hola desde {filename}")


if __name__ == "__main__":
    main()
''',
            'js': f'''/**
 * {filename} - Archivo JavaScript generado por TreeCreator
 * Creado: {timestamp}
 */

console.log("Hola desde {filename}");

/**
 * Función principal
 */
function main() {{
    // Implementar funcionalidad aquí
}}

main();
''',
            'ts': f'''/**
 * {filename} - Archivo TypeScript generado por TreeCreator
 * Creado: {timestamp}
 */

console.log("Hola desde {filename}");

/**
 * Función principal
 */
function main(): void {{
    // Implementar funcionalidad aquí
}}

main();
''',
            'html': f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
    <!-- Generado por TreeCreator: {timestamp} -->
</head>
<body>
    <h1>Hola desde {filename}</h1>
    
    <main>
        <!-- Tu contenido aquí -->
    </main>
    
</body>
</html>
''',
            'css': f'''/**
 * {filename} - Archivo CSS generado por TreeCreator
 * Creado: {timestamp}
 */

/* Reset básico */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

/* Estilos base */
body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
}}

/* Tu estilo aquí */
''',
            'md': f'''# {filename.replace('.md', '').replace('_', ' ').title()}

> Documento generado por TreeCreator  
> Fecha: {timestamp}

## Descripción

Este documento fue generado automáticamente.

## Contenido

- Punto 1
- Punto 2
- Punto 3

## Notas

Agregar contenido aquí...

---
*Generado por TreeCreator*
''',
            'json': f'''{{
  "name": "{filename.replace('.json', '')}",
  "version": "1.0.0",
  "description": "Archivo JSON generado por TreeCreator",
  "created": "{timestamp}",
  "metadata": {{
    "generator": "TreeCreator",
    "type": "configuration"
  }},
  "data": {{
    "example": "valor",
    "enabled": true
  }}
}}
''',
            'rs': f'''// {filename} - Archivo Rust generado por TreeCreator
// Creado: {timestamp}

fn main() {{
    println!("Hola desde {filename}");
    
    // Tu código aquí
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_basic() {{
        // Implementar test
        assert_eq!(2 + 2, 4);
    }}
}}
''',
            'go': f'''// {filename} - Archivo Go generado por TreeCreator
// Creado: {timestamp}
package main

import (
    "fmt"
)

func main() {{
    fmt.Println("Hola desde {filename}")
    
    // Tu código aquí
}}
''',
            'java': f'''/**
 * {filename} - Archivo Java generado por TreeCreator
 * Creado: {timestamp}
 */

public class {filename.replace('.java', '').capitalize()} {{
    
    /**
     * Método principal
     */
    public static void main(String[] args) {{
        System.out.println("Hola desde {filename}");
        
        // Tu código aquí
    }}
}}
''',
            'txt': f'''Archivo de texto: {filename}
Generado por TreeCreator
Fecha: {timestamp}

Contenido:
----------

Tu texto aquí...

---
Generado automáticamente por TreeCreator
''',
            'xml': f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- {filename} - Archivo XML generado por TreeCreator -->
<!-- Creado: {timestamp} -->
<root>
    <metadata>
        <name>{filename}</name>
        <created>{timestamp}</created>
        <generator>TreeCreator</generator>
    </metadata>
    
    <data>
        <!-- Tu contenido XML aquí -->
        <example>valor</example>
    </data>
</root>
''',
            'yml': f'''# {filename} - Archivo YAML generado por TreeCreator
# Creado: {timestamp}

name: {filename.replace('.yml', '').replace('.yaml', '')}
version: "1.0.0"
description: "Archivo YAML generado por TreeCreator"

metadata:
  created: "{timestamp}"
  generator: "TreeCreator"

# Tu configuración aquí
config:
  example: valor
  enabled: true
  debug: false
''',
            'yaml': f'''# {filename} - Archivo YAML generado por TreeCreator
# Creado: {timestamp}

name: {filename.replace('.yml', '').replace('.yaml', '')}
version: "1.0.0"
description: "Archivo YAML generado por TreeCreator"

metadata:
  created: "{timestamp}"
  generator: "TreeCreator"

# Tu configuración aquí
config:
  example: valor
  enabled: true
  debug: false
'''
        }
        
        return templates.get(ext, f"# Contenido de {filename}\n# Archivo {ext.upper()} generado por TreeCreator\n# Creado: {timestamp}\n\n")
    
    @staticmethod
    def get_language_name(filename: str) -> str:
        """Obtener nombre del lenguaje por extensión."""
        parts = filename.split('.')
        if len(parts) < 2:
            return "genérico"
        
        ext = parts[-1].lower()
        
        language_names = {
            'py': 'Python',
            'js': 'JavaScript', 
            'ts': 'TypeScript',
            'html': 'HTML',
            'css': 'CSS',
            'md': 'Markdown',
            'json': 'JSON',
            'rs': 'Rust',
            'go': 'Go',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C',
            'sh': 'Bash',
            'bat': 'Batch',
            'txt': 'Texto',
            'xml': 'XML',
            'yml': 'YAML',
            'yaml': 'YAML',
            'php': 'PHP',
            'rb': 'Ruby',
            'swift': 'Swift',
            'kt': 'Kotlin'
        }
        
        return language_names.get(ext, ext.upper())


class NodeDisplayHelper:
    """Helper para formateo y display de nodos."""
    
    @staticmethod
    def format_node_display(node: Node, is_open: bool = False) -> str:
        """Formatear texto de display para un nodo."""
        if node.is_folder():
            icon = FlatIcons.FOLDER_OPEN if is_open else FlatIcons.FOLDER_CLOSED
        else:
            icon = FlatIcons.get_file_icon(node.name)
        
        return f"{icon} {node.name}"
    
    @staticmethod
    def get_node_path(node: Node, node_repository) -> str:
        """Obtener ruta completa de un nodo."""
        path_parts = [node.name]
        current = node
        
        try:
            while current.parent_id:
                parent = node_repository.find_by_id(current.parent_id)
                if parent:
                    path_parts.insert(0, parent.name)
                    current = parent
                else:
                    break
        except Exception as e:
            print(f"❌ Error construyendo ruta: {e}")
        
        return "/" + "/".join(path_parts)
    
    @staticmethod
    def get_node_statistics(nodes: list[Node]) -> Dict[str, int]:
        """Calcular estadísticas de una lista de nodos."""
        stats = {
            'total_folders': 0,
            'total_files': 0,
            'completed': 0,
            'in_progress': 0,
            'pending': 0,
            'no_status': 0
        }
        
        for node in nodes:
            if node.is_folder():
                stats['total_folders'] += 1
            else:
                stats['total_files'] += 1
            
            status_value = node.status.value
            if status_value == "✅":
                stats['completed'] += 1
            elif status_value == "⬜":
                stats['in_progress'] += 1
            elif status_value == "❌":
                stats['pending'] += 1
            else:
                stats['no_status'] += 1
        
        return stats