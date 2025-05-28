#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Portapapeles para TreeApp v4 Pro
Gestión de operaciones copy/cut/paste para nodos
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class ClipboardData:
    """Datos del portapapeles para copy/paste"""
    node_ids: List[str] = field(default_factory=list)
    operation: str = "copy"  # "copy" o "cut"
    source_parent_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def is_empty(self) -> bool:
        """Verificar si el portapapeles está vacío"""
        return len(self.node_ids) == 0
    
    def clear(self):
        """Limpiar portapapeles"""
        self.node_ids.clear()
        self.operation = "copy"
        self.source_parent_id = None
        self.timestamp = datetime.now().isoformat()

class NodeClipboard:
    """
    Gestor del portapapeles para operaciones copy/paste en nodos
    """
    
    def __init__(self):
        self.clipboard_data = ClipboardData()
    
    def copy_nodes(self, node_ids: List[str], source_parent_id: Optional[str] = None):
        """
        Copiar nodos al portapapeles
        
        Args:
            node_ids: Lista de IDs de nodos a copiar
            source_parent_id: ID del padre de origen
        """
        self.clipboard_data = ClipboardData(
            node_ids=node_ids.copy(),
            operation="copy",
            source_parent_id=source_parent_id
        )
        logger.info(f"Copiados {len(node_ids)} nodos al portapapeles")
    
    def cut_nodes(self, node_ids: List[str], source_parent_id: Optional[str] = None):
        """
        Cortar nodos al portapapeles
        
        Args:
            node_ids: Lista de IDs de nodos a cortar
            source_parent_id: ID del padre de origen
        """
        self.clipboard_data = ClipboardData(
            node_ids=node_ids.copy(),
            operation="cut",
            source_parent_id=source_parent_id
        )
        logger.info(f"Cortados {len(node_ids)} nodos al portapapeles")
    
    def get_clipboard_data(self) -> ClipboardData:
        """Obtener datos del portapapeles"""
        return self.clipboard_data
    
    def clear_clipboard(self):
        """Limpiar portapapeles"""
        self.clipboard_data.clear()
        logger.info("Portapapeles limpiado")
    
    def has_data(self) -> bool:
        """Verificar si hay datos en el portapapeles"""
        return not self.clipboard_data.is_empty()
    
    def get_operation_description(self) -> str:
        """
        Obtener descripción legible de la operación
        
        Returns:
            Descripción de la operación en el portapapeles
        """
        if self.clipboard_data.is_empty():
            return "Portapapeles vacío"
        
        count = len(self.clipboard_data.node_ids)
        operation = "copiados" if self.clipboard_data.operation == "copy" else "cortados"
        
        return f"{count} nodo(s) {operation}"
    
    def is_cut_operation(self) -> bool:
        """Verificar si la operación es cut (cortar)"""
        return self.clipboard_data.operation == "cut"
    
    def is_copy_operation(self) -> bool:
        """Verificar si la operación es copy (copiar)"""
        return self.clipboard_data.operation == "copy"