#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo Principal de Nodos para TreeApp v4 Pro
Contiene las definiciones fundamentales: Node, NodeStatus, NodeType, EditorFields, NodeMetadata
"""

import uuid
import json
import re
import copy
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)

# Patrón compilado para mejor performance en validación
INVALID_CHAR_PATTERN = re.compile(r'[<>:"/\\|?*]')

class NodeType(Enum):
    """Tipos de nodos disponibles"""
    FILE = "file"
    FOLDER = "folder"
    
    @classmethod
    def from_str(cls, value: str) -> 'NodeType':
        """
        Crear NodeType desde string con validación robusta
        
        Args:
            value: String del tipo de nodo
            
        Returns:
            NodeType correspondiente
            
        Raises:
            ValueError: Si el valor no es válido
        """
        if not isinstance(value, str):
            raise ValueError(f"NodeType debe ser string, recibido: {type(value)}")
        
        value_lower = value.lower().strip()
        
        # Mapeo de valores comunes
        type_mapping = {
            "file": cls.FILE,
            "archivo": cls.FILE,
            "document": cls.FILE,
            "folder": cls.FOLDER,
            "carpeta": cls.FOLDER,
            "directory": cls.FOLDER,
            "dir": cls.FOLDER
        }
        
        if value_lower in type_mapping:
            return type_mapping[value_lower]
        
        # Intentar match directo con los valores del enum
        for node_type in cls:
            if node_type.value.lower() == value_lower:
                return node_type
        
        raise ValueError(f"Tipo de nodo no válido: '{value}'. Valores permitidos: {[t.value for t in cls]}")

class NodeStatus(Enum):
    """Estados disponibles para los nodos"""
    COMPLETED = "✅"
    IN_PROGRESS = "⬜"
    PENDING = "❌"
    NONE = ""
    
    @property
    def display_text(self) -> str:
        """Texto legible del estado (para futuras internacionalizaciones)"""
        status_texts = {
            "✅": "Completado",
            "⬜": "En Proceso",
            "❌": "Pendiente",
            "": "Sin Estado"
        }
        return status_texts.get(self.value, self.value)
    
    @classmethod
    def from_str(cls, value: str) -> 'NodeStatus':
        """
        Crear NodeStatus desde string con validación robusta
        
        Args:
            value: String del estado
            
        Returns:
            NodeStatus correspondiente
            
        Raises:
            ValueError: Si el valor no es válido
        """
        if not isinstance(value, str):
            # Si es None o vacío, retornar NONE
            if value is None or value == "":
                return cls.NONE
            raise ValueError(f"NodeStatus debe ser string, recibido: {type(value)}")
        
        # Mapeo de valores comunes (incluyendo texto y emojis)
        status_mapping = {
            # Emojis directos
            "✅": cls.COMPLETED,
            "⬜": cls.IN_PROGRESS, 
            "❌": cls.PENDING,
            "": cls.NONE,
            
            # Texto en español
            "completado": cls.COMPLETED,
            "completo": cls.COMPLETED,
            "terminado": cls.COMPLETED,
            "listo": cls.COMPLETED,
            "done": cls.COMPLETED,
            "finished": cls.COMPLETED,
            
            "en proceso": cls.IN_PROGRESS,
            "proceso": cls.IN_PROGRESS,
            "progreso": cls.IN_PROGRESS,
            "working": cls.IN_PROGRESS,
            "progress": cls.IN_PROGRESS,
            "wip": cls.IN_PROGRESS,
            
            "pendiente": cls.PENDING,
            "por hacer": cls.PENDING,
            "todo": cls.PENDING,
            "pending": cls.PENDING,
            
            "sin estado": cls.NONE,
            "ninguno": cls.NONE,
            "none": cls.NONE,
            "null": cls.NONE,
            
            # Símbolos alternativos comunes
            "🕓": cls.IN_PROGRESS,  # Reloj - a veces se usa
            "⏳": cls.IN_PROGRESS,  # Reloj de arena
            "🔄": cls.IN_PROGRESS,  # Recarga
            "❎": cls.PENDING,      # X alternativa
            "✗": cls.PENDING,       # X sin fondo
            "✓": cls.COMPLETED,     # Check sin fondo
            "☑": cls.COMPLETED,     # Check en caja
        }
        
        value_lower = value.lower().strip()
        
        if value_lower in status_mapping:
            return status_mapping[value_lower]
        
        # Intentar match directo con los valores del enum
        for status in cls:
            if status.value == value:
                return status
        
        # Si no se encuentra, log warning y retornar NONE
        logger.warning(f"Estado no reconocido: '{value}'. Usando estado 'Sin Estado'.")
        return cls.NONE

@dataclass
class EditorFields:
    """Los 4 campos del editor mejorado"""
    name: str = ""                    # Campo 1: Nombre del archivo/carpeta
    markdown_content: str = ""        # Campo 2: Contenido Markdown principal
    technical_notes: str = ""         # Campo 3: Notas técnicas/descripción extendida
    code_content: str = ""            # Campo 4: Ventana de código/estructura

    def to_dict(self) -> Dict[str, str]:
        """Convertir a diccionario para serialización"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'EditorFields':
        """
        Crear desde diccionario con validación mejorada
        
        Args:
            data: Diccionario con datos de los campos
            
        Returns:
            EditorFields con datos validados
        """
        # Extraer campos con valores por defecto
        name = data.get('name', '').strip()
        markdown_content = data.get('markdown_content', '')
        technical_notes = data.get('technical_notes', '')
        code_content = data.get('code_content', '')
        
        # 🔥 VALIDACIÓN MEJORADA: Warning si el nombre viene vacío
        if not name:
            logger.warning("EditorFields.from_dict(): campo 'name' está vacío. "
                         "Esto puede causar problemas de visualización.")
        
        # Validar que los campos sean strings
        for field_name, value in [
            ('name', name),
            ('markdown_content', markdown_content), 
            ('technical_notes', technical_notes),
            ('code_content', code_content)
        ]:
            if not isinstance(value, str):
                logger.warning(f"Campo '{field_name}' no es string, convirtiendo: {type(value)}")
                data[field_name] = str(value) if value is not None else ""
        
        return cls(
            name=name,
            markdown_content=markdown_content,
            technical_notes=technical_notes,
            code_content=code_content
        )

@dataclass
class NodeMetadata:
    """Metadatos adicionales del nodo"""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    priority: int = 0  # 0=normal, 1=high, -1=low
    estimated_time: Optional[int] = None  # en minutos
    completion_percentage: int = 0  # 0-100
    comments: List[Dict[str, Any]] = field(default_factory=list)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeMetadata':
        """Crear desde diccionario"""
        return cls(
            created_at=data.get('created_at', datetime.now().isoformat()),
            modified_at=data.get('modified_at', datetime.now().isoformat()),
            tags=data.get('tags', []),
            priority=data.get('priority', 0),
            estimated_time=data.get('estimated_time'),
            completion_percentage=data.get('completion_percentage', 0),
            comments=data.get('comments', []),
            custom_attributes=data.get('custom_attributes', {})
        )

class Node:
    """
    Modelo principal de nodo para TreeApp v4 Pro
    Representa archivos y carpetas con todos los atributos necesarios
    """
    
    def __init__(self, 
                 name: str,
                 node_type: Union[NodeType, str],
                 node_id: Optional[str] = None,
                 parent_id: Optional[str] = None,
                 status: Union[NodeStatus, str] = NodeStatus.NONE,
                 editor_fields: Optional[EditorFields] = None,
                 metadata: Optional[NodeMetadata] = None,
                 children_ids: Optional[List[str]] = None):
        """
        Inicializar nodo
        
        Args:
            name: Nombre del archivo/carpeta
            node_type: Tipo de nodo (file/folder)
            node_id: ID único (se genera automáticamente si no se proporciona)
            parent_id: ID del nodo padre
            status: Estado del nodo
            editor_fields: Los 4 campos del editor
            metadata: Metadatos adicionales
            children_ids: Lista de IDs de nodos hijos
        """
        self.id = node_id or str(uuid.uuid4())
        self.name = name
        
        # 🔥 MEJORA: Usar métodos from_str() para robustez
        self.type = NodeType.from_str(node_type) if isinstance(node_type, str) else node_type
        self.status = NodeStatus.from_str(status) if isinstance(status, str) else status
        
        self.parent_id = parent_id
        self.children_ids = children_ids or []
        
        # Los 4 campos del editor
        self.editor_fields = editor_fields or EditorFields(name=name)
        
        # Metadatos
        self.metadata = metadata or NodeMetadata()
        
        # Actualizar el nombre en los campos del editor si no está set
        if not self.editor_fields.name and name:
            self.editor_fields.name = name
    
    @property
    def is_folder(self) -> bool:
        """Verificar si es carpeta"""
        return self.type == NodeType.FOLDER
    
    @property
    def is_file(self) -> bool:
        """Verificar si es archivo"""
        return self.type == NodeType.FILE
    
    @property
    def has_children(self) -> bool:
        """Verificar si tiene hijos"""
        return len(self.children_ids) > 0
    
    @property
    def status_emoji(self) -> str:
        """Obtener emoji del estado"""
        return self.status.value
    
    @property
    def icon_emoji(self) -> str:
        """Obtener emoji del icono según el tipo"""
        return "📁" if self.is_folder else "📄"
    
    def add_child(self, child_id: str) -> None:
        """Agregar hijo al nodo"""
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)
            self.update_modified_time()
    
    def remove_child(self, child_id: str) -> None:
        """Remover hijo del nodo"""
        if child_id in self.children_ids:
            self.children_ids.remove(child_id)
            self.update_modified_time()
    
    def update_modified_time(self) -> None:
        """Actualizar tiempo de modificación"""
        self.metadata.modified_at = datetime.now().isoformat()
    
    def update_name(self, new_name: str) -> None:
        """Actualizar nombre del nodo y sincronizar con editor"""
        self.name = new_name
        self.editor_fields.name = new_name
        self.update_modified_time()
    
    def update_editor_field(self, field_name: str, content: str) -> None:
        """
        Actualizar campo específico del editor
        
        Args:
            field_name: Nombre del campo (name, markdown_content, technical_notes, code_content)
            content: Nuevo contenido
        """
        if hasattr(self.editor_fields, field_name):
            setattr(self.editor_fields, field_name, content)
            
            # Si se actualiza el nombre, sincronizar con el nodo
            if field_name == 'name':
                self.name = content
            
            self.update_modified_time()
        else:
            logger.warning(f"Campo '{field_name}' no existe en EditorFields")
    
    def add_tag(self, tag: str) -> None:
        """Agregar tag al nodo"""
        if tag and tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
            self.update_modified_time()
    
    def remove_tag(self, tag: str) -> None:
        """Remover tag del nodo"""
        if tag in self.metadata.tags:
            self.metadata.tags.remove(tag)
            self.update_modified_time()
    
    def add_comment(self, comment_text: str, author: str = "Usuario") -> str:
        """
        Agregar comentario al nodo
        
        Args:
            comment_text: Texto del comentario
            author: Autor del comentario
            
        Returns:
            ID del comentario creado
        """
        comment_id = str(uuid.uuid4())
        comment = {
            "id": comment_id,
            "text": comment_text,
            "author": author,
            "timestamp": datetime.now().isoformat()
        }
        self.metadata.comments.append(comment)
        self.update_modified_time()
        return comment_id
    
    def get_display_name(self, include_icon: bool = True, include_status: bool = True) -> str:
        """
        Obtener nombre para mostrar en la UI
        
        Args:
            include_icon: Incluir emoji de icono
            include_status: Incluir emoji de estado
            
        Returns:
            Nombre formateado para display
        """
        parts = []
        
        if include_icon:
            parts.append(self.icon_emoji)
        
        parts.append(self.name)
        
        if self.is_folder and not self.name.endswith('/'):
            parts[-1] += '/'
        
        if include_status and self.status != NodeStatus.NONE:
            parts.append(self.status_emoji)
        
        return " ".join(parts)
    
    def get_path_components(self, node_registry: Dict[str, 'Node']) -> List[str]:
        """
        Obtener componentes de la ruta completa
        
        Args:
            node_registry: Diccionario con todos los nodos por ID
            
        Returns:
            Lista de nombres de nodos desde la raíz hasta este nodo
        """
        path = []
        current_node = self
        
        while current_node:
            path.insert(0, current_node.name)
            if current_node.parent_id and current_node.parent_id in node_registry:
                current_node = node_registry[current_node.parent_id]
            else:
                break
        
        return path
    
    def get_full_path(self, node_registry: Dict[str, 'Node'], separator: str = "/") -> str:
        """
        Obtener ruta completa del nodo
        
        Args:
            node_registry: Diccionario con todos los nodos
            separator: Separador de ruta
            
        Returns:
            Ruta completa como string
        """
        components = self.get_path_components(node_registry)
        return separator.join(components)
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Validar el nodo y retornar lista de errores
        
        Args:
            config: Configuración opcional con caracteres inválidos personalizados
        
        Returns:
            Lista de mensajes de error (vacía si es válido)
        """
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("El nombre no puede estar vacío")
        
        if not self.id:
            errors.append("El ID no puede estar vacío")
        
        # Validar caracteres no permitidos (configurable)
        if config and 'invalid_chars' in config:
            invalid_chars = config['invalid_chars']
            if any(char in self.name for char in invalid_chars):
                errors.append(f"El nombre contiene caracteres no válidos: {invalid_chars}")
        else:
            # Usar patrón compilado para mejor performance
            if INVALID_CHAR_PATTERN.search(self.name):
                errors.append("El nombre contiene caracteres no válidos: <>:\"/\\|?*")
        
        # Validar que carpetas no tengan extensión
        if self.is_folder and '.' in self.name:
            errors.append("Las carpetas no deberían tener extensión")
        
        return errors
    
    def is_valid(self) -> bool:
        """Verificar si el nodo es válido"""
        return len(self.validate()) == 0
    
    def deepcopy(self, include_children: bool = False, generate_new_ids: bool = True) -> 'Node':
        """
        🔥 NUEVO: Crear copia profunda personalizada del nodo
        
        Args:
            include_children: Si incluir lista de hijos (con los mismos IDs)
            generate_new_ids: Si generar nuevos IDs para el nodo clonado
            
        Returns:
            Copia profunda del nodo
        """
        # Crear copias profundas de objetos complejos
        editor_fields_copy = EditorFields(
            name=self.editor_fields.name,
            markdown_content=self.editor_fields.markdown_content,
            technical_notes=self.editor_fields.technical_notes,
            code_content=self.editor_fields.code_content
        )
        
        metadata_copy = NodeMetadata(
            created_at=self.metadata.created_at,
            modified_at=self.metadata.modified_at,
            tags=copy.deepcopy(self.metadata.tags),
            priority=self.metadata.priority,
            estimated_time=self.metadata.estimated_time,
            completion_percentage=self.metadata.completion_percentage,
            comments=copy.deepcopy(self.metadata.comments),
            custom_attributes=copy.deepcopy(self.metadata.custom_attributes)
        )
        
        # Clonar lista de hijos si se solicita
        children_ids_copy = copy.deepcopy(self.children_ids) if include_children else []
        
        # Crear nuevo nodo
        new_node = Node(
            name=self.name,
            node_type=self.type,
            node_id=str(uuid.uuid4()) if generate_new_ids else self.id,
            parent_id=self.parent_id,
            status=self.status,
            editor_fields=editor_fields_copy,
            metadata=metadata_copy,
            children_ids=children_ids_copy
        )
        
        logger.debug(f"deepcopy(): {self.id} -> {new_node.id} "
                    f"(children: {include_children}, new_ids: {generate_new_ids})")
        
        return new_node
    
    def clone(self, 
              new_name: Optional[str] = None, 
              include_children: bool = False,
              deep_clone_children: bool = False) -> 'Node':
        """
        🔥 MEJORADO: Clonar el nodo (ahora usa deepcopy interno)
        
        Args:
            new_name: Nuevo nombre (opcional)
            include_children: Si incluir los IDs de hijos
            deep_clone_children: Si clonar recursivamente los hijos con nuevos IDs
            
        Returns:
            Nuevo nodo clonado
            
        Note:
            En futuras versiones, este método podría delegar al NodeDuplicator
            para operaciones más complejas de clonación recursiva.
        """
        # Usar deepcopy como base
        cloned = self.deepcopy(include_children=include_children, generate_new_ids=True)
        
        # Aplicar nuevo nombre si se proporciona
        if new_name:
            cloned.update_name(new_name)
        else:
            # Nombre por defecto para copia
            cloned.update_name(f"{self.name} (copia)")
        
        # TODO: En futuras versiones, delegar deep_clone_children al NodeDuplicator
        if deep_clone_children:
            logger.info("deep_clone_children=True requiere NodeDuplicator - feature pendiente")
        
        return cloned
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertir nodo a diccionario para serialización
        
        Returns:
            Diccionario con todos los datos del nodo
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "parent_id": self.parent_id,
            "status": self.status.value,
            "children_ids": self.children_ids.copy(),
            "editor_fields": self.editor_fields.to_dict(),
            "metadata": self.metadata.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """
        Crear nodo desde diccionario con validación robusta
        
        Args:
            data: Diccionario con datos del nodo
            
        Returns:
            Instancia de Node
        """
        # Usar métodos from_dict mejorados
        editor_fields = EditorFields.from_dict(data.get('editor_fields', {}))
        metadata = NodeMetadata.from_dict(data.get('metadata', {}))
        
        # Usar from_str() para tipos y estados
        return cls(
            name=data['name'],
            node_type=data['type'],  # from_str() se llama automáticamente en __init__
            node_id=data.get('id'),
            parent_id=data.get('parent_id'),
            status=data.get('status', NodeStatus.NONE.value),  # from_str() automático
            editor_fields=editor_fields,
            metadata=metadata,
            children_ids=data.get('children_ids', [])
        )
    
    def to_json(self) -> str:
        """Convertir a JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Node':
        """Crear desde JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """Representación string del nodo"""
        return f"Node(id='{self.id}', name='{self.name}', type='{self.type.value}')"
    
    def __repr__(self) -> str:
        """Representación detallada del nodo"""
        return (f"Node(id='{self.id}', name='{self.name}', type='{self.type.value}', "
                f"status='{self.status.value}', children={len(self.children_ids)})")
    
    def __eq__(self, other) -> bool:
        """Comparar nodos por ID"""
        if not isinstance(other, Node):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash basado en el ID"""
        return hash(self.id)