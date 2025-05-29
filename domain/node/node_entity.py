# domain/node/node_entity.py
"""
Entidad principal del nodo en TreeApp v4 Pro.
Representa un archivo o carpeta con sus 4 campos de contenido.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class NodeType(Enum):
    """Tipos de nodo soportados."""
    FILE = "file"
    FOLDER = "folder"


class NodeStatus(Enum):
    """Estados posibles de un nodo."""
    COMPLETED = "✅"
    IN_PROGRESS = "⬜"  
    PENDING = "❌"
    NONE = ""


@dataclass
class Node:
    """
    Entidad principal del nodo con los 4 campos requeridos:
    1. name: Nombre del archivo/carpeta
    2. markdown_short: Contenido markdown principal  
    3. explanation: Notas técnicas extendidas
    4. code: Código/estructura asociada
    """
    # Campos principales (los 4 requeridos)
    name: str
    node_type: NodeType
    markdown_short: str = ""
    explanation: str = ""  # Notas técnicas
    code: str = ""         # Código/estructura
    
    # Metadatos
    node_id: str = ""
    status: NodeStatus = NodeStatus.NONE
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    
    # Timestamps
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    modified: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Metadatos adicionales
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.name.strip():
            raise ValueError("El nombre del nodo no puede estar vacío")
        
        if not self.node_id:
            self.node_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generar ID único para el nodo."""
        import uuid
        return f"{self.node_type.value}_{uuid.uuid4().hex[:8]}"
    
    def update_modified(self) -> None:
        """Actualizar timestamp de modificación."""
        self.modified = datetime.now().isoformat()
    
    def is_folder(self) -> bool:
        """Verificar si el nodo es una carpeta."""
        return self.node_type == NodeType.FOLDER
    
    def is_file(self) -> bool:
        """Verificar si el nodo es un archivo."""
        return self.node_type == NodeType.FILE
    
    def add_child(self, child_id: str) -> None:
        """Agregar ID de hijo."""
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)
            self.update_modified()
    
    def remove_child(self, child_id: str) -> None:
        """Remover ID de hijo."""
        if child_id in self.children_ids:
            self.children_ids.remove(child_id)
            self.update_modified()