#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo y lógica de los 4 campos de edición para TreeApp v4 Pro.
Incluye nombre, markdown, notas técnicas y contenido de código.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict

@dataclass
class EditorFields:
    """
    Los 4 campos del editor mejorado:
    - name: Nombre del archivo/carpeta
    - markdown_content: Contenido principal en Markdown
    - technical_notes: Notas técnicas y descripción extendida
    - code_content: Ventana de código/estructura
    """
    name: str = ""
    markdown_content: str = ""
    technical_notes: str = ""
    code_content: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convertir a diccionario para serialización."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'EditorFields':
        """
        Crear instancia desde un diccionario, con validación básica.
        """
        return cls(
            name=str(data.get("name", "")).strip(),
            markdown_content=str(data.get("markdown_content", "")),
            technical_notes=str(data.get("technical_notes", "")),
            code_content=str(data.get("code_content", ""))
        )