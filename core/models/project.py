#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo de Proyecto para TreeApp v4 Pro
Gestión completa de proyectos con metadatos, configuración, historial y validación
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, field, asdict
import logging

from .node import Node, NodeType, NodeStatus
from .node_utils import (
    validate_tree_integrity, 
    calculate_node_statistics,
    get_completion_statistics,
    create_root_node,
    migrate_legacy_data
)

logger = logging.getLogger(__name__)

@dataclass
class ProjectMetadata:
    """Metadatos del proyecto"""
    name: str = "Nuevo Proyecto"
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_opened_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    category: str = ""
    priority: int = 0  # 0=normal, 1=high, -1=low
    estimated_duration_hours: Optional[float] = None
    actual_duration_hours: float = 0.0
    completion_target_date: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        """Crear desde diccionario"""
        return cls(
            name=data.get('name', 'Nuevo Proyecto'),
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            author=data.get('author', ''),
            created_at=data.get('created_at', datetime.now().isoformat()),
            modified_at=data.get('modified_at', datetime.now().isoformat()),
            last_opened_at=data.get('last_opened_at', datetime.now().isoformat()),
            tags=data.get('tags', []),
            category=data.get('category', ''),
            priority=data.get('priority', 0),
            estimated_duration_hours=data.get('estimated_duration_hours'),
            actual_duration_hours=data.get('actual_duration_hours', 0.0),
            completion_target_date=data.get('completion_target_date'),
            custom_fields=data.get('custom_fields', {})
        )

@dataclass
class ProjectSettings:
    """Configuración del proyecto"""
    auto_save: bool = True
    auto_save_interval_minutes: int = 5
    backup_enabled: bool = True
    max_backups: int = 10
    default_node_status: str = NodeStatus.NONE.value
    default_file_template: str = "readme"
    show_hidden_nodes: bool = False
    enable_drag_drop: bool = True
    enable_undo_redo: bool = True
    max_undo_levels: int = 50
    preview_mode: str = "classic"  # classic, ascii, ascii_folders, columns
    export_format: str = "txt"
    theme: str = "oscuro"
    font_size: int = 11
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectSettings':
        """Crear desde diccionario"""
        return cls(
            auto_save=data.get('auto_save', True),
            auto_save_interval_minutes=data.get('auto_save_interval_minutes', 5),
            backup_enabled=data.get('backup_enabled', True),
            max_backups=data.get('max_backups', 10),
            default_node_status=data.get('default_node_status', NodeStatus.NONE.value),
            default_file_template=data.get('default_file_template', 'readme'),
            show_hidden_nodes=data.get('show_hidden_nodes', False),
            enable_drag_drop=data.get('enable_drag_drop', True),
            enable_undo_redo=data.get('enable_undo_redo', True),
            max_undo_levels=data.get('max_undo_levels', 50),
            preview_mode=data.get('preview_mode', 'classic'),
            export_format=data.get('export_format', 'txt'),
            theme=data.get('theme', 'oscuro'),
            font_size=data.get('font_size', 11),
            custom_settings=data.get('custom_settings', {})
        )

@dataclass
class ProjectSnapshot:
    """Snapshot del estado del proyecto para undo/redo"""
    id: str
    timestamp: str
    description: str
    nodes_data: Dict[str, Dict[str, Any]]
    metadata_snapshot: Dict[str, Any]
    
    @classmethod
    def create(cls, project: 'Project', description: str) -> 'ProjectSnapshot':
        """Crear snapshot del estado actual"""
        snapshot_id = str(uuid.uuid4())
        
        # Crear copia profunda de los datos de nodos
        nodes_data = {}
        for node_id, node in project.nodes.items():
            nodes_data[node_id] = node.to_dict()
        
        return cls(
            id=snapshot_id,
            timestamp=datetime.now().isoformat(),
            description=description,
            nodes_data=nodes_data,
            metadata_snapshot=project.metadata.to_dict()
        )

class Project:
    """
    Modelo completo de proyecto para TreeApp v4 Pro
    Gestiona nodos, metadatos, configuración, historial y operaciones del proyecto
    """
    
    def __init__(self, 
                 project_id: Optional[str] = None,
                 metadata: Optional[ProjectMetadata] = None,
                 settings: Optional[ProjectSettings] = None,
                 file_path: Optional[str] = None):
        """
        Inicializar proyecto
        
        Args:
            project_id: ID único del proyecto
            metadata: Metadatos del proyecto
            settings: Configuración del proyecto
            file_path: Ruta del archivo del proyecto
        """
        self.id = project_id or str(uuid.uuid4())
        self.metadata = metadata or ProjectMetadata()
        self.settings = settings or ProjectSettings()
        self.file_path = file_path
        
        # Datos principales
        self.nodes: Dict[str, Node] = {}
        self.root_node_id: Optional[str] = None
        
        # Historial y snapshots
        self.snapshots: List[ProjectSnapshot] = []
        self.current_snapshot_index: int = -1
        
        # Estado de la sesión
        self.is_modified: bool = False
        self.is_loaded: bool = False
        self.last_save_time: Optional[datetime] = None
        
        # Cache de operaciones
        self._stats_cache: Optional[Dict[str, Any]] = None
        self._completion_cache: Optional[Dict[str, Any]] = None
        self._integrity_cache: Optional[List[str]] = None
        self._cache_timestamp: Optional[datetime] = None
        
        # Eventos de cambio
        self._change_listeners: List[callable] = []
        
        # Inicializar proyecto vacío
        self._initialize_empty_project()
    
    def _initialize_empty_project(self):
        """Inicializar proyecto con nodo raíz"""
        root_node = create_root_node(self.metadata.name)
        self.nodes[root_node.id] = root_node
        self.root_node_id = root_node.id
        self._invalidate_cache()
    
    # ==================================================================================
    # GESTIÓN DE NODOS
    # ==================================================================================
    
    def add_node(self, node: Node, parent_id: Optional[str] = None) -> bool:
        """
        Agregar nodo al proyecto
        
        Args:
            node: Nodo a agregar
            parent_id: ID del padre (None para raíz)
            
        Returns:
            True si se agregó correctamente
        """
        if node.id in self.nodes:
            logger.warning(f"El nodo {node.id} ya existe en el proyecto")
            return False
        
        # Validar padre si se especifica
        if parent_id:
            if parent_id not in self.nodes:
                logger.error(f"Padre {parent_id} no existe")
                return False
            
            parent_node = self.nodes[parent_id]
            if not parent_node.is_folder:
                logger.error(f"El padre {parent_id} no es una carpeta")
                return False
            
            # Establecer relación padre-hijo
            node.parent_id = parent_id
            parent_node.add_child(node.id)
        
        # Agregar nodo
        self.nodes[node.id] = node
        self._mark_modified("Nodo agregado")
        self._invalidate_cache()
        self._notify_change("node_added", {"node_id": node.id, "parent_id": parent_id})
        
        logger.info(f"Nodo {node.id} agregado al proyecto")
        return True
    
    def remove_node(self, node_id: str, recursive: bool = True) -> bool:
        """
        Remover nodo del proyecto
        
        Args:
            node_id: ID del nodo a remover
            recursive: Si remover hijos recursivamente
            
        Returns:
            True si se removió correctamente
        """
        if node_id not in self.nodes:
            logger.warning(f"Nodo {node_id} no existe")
            return False
        
        if node_id == self.root_node_id:
            logger.error("No se puede eliminar el nodo raíz")
            return False
        
        node = self.nodes[node_id]
        
        # Remover hijos recursivamente si se solicita
        if recursive:
            children_to_remove = list(node.children_ids)
            for child_id in children_to_remove:
                self.remove_node(child_id, recursive=True)
        
        # Remover de padre
        if node.parent_id and node.parent_id in self.nodes:
            parent_node = self.nodes[node.parent_id]
            parent_node.remove_child(node_id)
        
        # Remover nodo
        del self.nodes[node_id]
        self._mark_modified("Nodo eliminado")
        self._invalidate_cache()
        self._notify_change("node_removed", {"node_id": node_id})
        
        logger.info(f"Nodo {node_id} removido del proyecto")
        return True
    
    def move_node(self, node_id: str, new_parent_id: str) -> bool:
        """
        Mover nodo a nuevo padre
        
        Args:
            node_id: ID del nodo a mover
            new_parent_id: ID del nuevo padre
            
        Returns:
            True si se movió correctamente
        """
        if node_id not in self.nodes or new_parent_id not in self.nodes:
            logger.error("Nodo o padre no existen")
            return False
        
        if node_id == self.root_node_id:
            logger.error("No se puede mover el nodo raíz")
            return False
        
        node = self.nodes[node_id]
        new_parent = self.nodes[new_parent_id]
        
        if not new_parent.is_folder:
            logger.error("El nuevo padre debe ser una carpeta")
            return False
        
        # Validar que no se mueva dentro de sí mismo
        if self._is_descendant(new_parent_id, node_id):
            logger.error("No se puede mover un nodo dentro de sí mismo")
            return False
        
        # Remover del padre actual
        if node.parent_id and node.parent_id in self.nodes:
            old_parent = self.nodes[node.parent_id]
            old_parent.remove_child(node_id)
        
        # Agregar al nuevo padre
        node.parent_id = new_parent_id
        new_parent.add_child(node_id)
        
        self._mark_modified("Nodo movido")
        self._invalidate_cache()
        self._notify_change("node_moved", {
            "node_id": node_id, 
            "old_parent_id": node.parent_id,
            "new_parent_id": new_parent_id
        })
        
        logger.info(f"Nodo {node_id} movido a {new_parent_id}")
        return True
    
    def _is_descendant(self, potential_descendant: str, ancestor: str) -> bool:
        """Verificar si un nodo es descendiente de otro"""
        current = potential_descendant
        visited = set()
        
        while current and current in self.nodes:
            if current in visited:  # Prevenir ciclos
                break
            if current == ancestor:
                return True
            visited.add(current)
            current = self.nodes[current].parent_id
        
        return False
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Obtener nodo por ID"""
        return self.nodes.get(node_id)
    
    def get_root_node(self) -> Optional[Node]:
        """Obtener nodo raíz"""
        return self.nodes.get(self.root_node_id) if self.root_node_id else None
    
    def get_children(self, node_id: str) -> List[Node]:
        """Obtener hijos directos de un nodo"""
        if node_id not in self.nodes:
            return []
        
        node = self.nodes[node_id]
        return [self.nodes[child_id] for child_id in node.children_ids 
                if child_id in self.nodes]
    
    def get_all_descendants(self, node_id: str) -> List[Node]:
        """Obtener todos los descendientes de un nodo"""
        descendants = []
        queue = [node_id]
        
        while queue:
            current_id = queue.pop(0)
            if current_id in self.nodes:
                node = self.nodes[current_id]
                for child_id in node.children_ids:
                    if child_id in self.nodes:
                        descendants.append(self.nodes[child_id])
                        queue.append(child_id)
        
        return descendants
    
    def find_nodes(self, **criteria) -> List[Node]:
        """Buscar nodos por criterios (delega a node_utils)"""
        from .node_utils import find_nodes_by_criteria
        return find_nodes_by_criteria(self.nodes, **criteria)
    
    # ==================================================================================
    # GESTIÓN DE METADATOS Y CONFIGURACIÓN
    # ==================================================================================
    
    def update_metadata(self, **kwargs):
        """Actualizar metadatos del proyecto"""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
                self.metadata.modified_at = datetime.now().isoformat()
        
        self._mark_modified("Metadatos actualizados")
        self._notify_change("metadata_updated", kwargs)
    
    def update_settings(self, **kwargs):
        """Actualizar configuración del proyecto"""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        self._mark_modified("Configuración actualizada")
        self._notify_change("settings_updated", kwargs)
    
    def add_tag(self, tag: str):
        """Agregar tag al proyecto"""
        if tag and tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
            self.metadata.modified_at = datetime.now().isoformat()
            self._mark_modified("Tag agregado")
    
    def remove_tag(self, tag: str):
        """Remover tag del proyecto"""
        if tag in self.metadata.tags:
            self.metadata.tags.remove(tag)
            self.metadata.modified_at = datetime.now().isoformat()
            self._mark_modified("Tag removido")
    
    # ==================================================================================
    # HISTORIAL Y SNAPSHOTS (UNDO/REDO)
    # ==================================================================================
    
    def create_snapshot(self, description: str = "Cambio automático") -> str:
        """
        Crear snapshot del estado actual
        
        Args:
            description: Descripción del cambio
            
        Returns:
            ID del snapshot creado
        """
        if not self.settings.enable_undo_redo:
            return ""
        
        # Crear snapshot
        snapshot = ProjectSnapshot.create(self, description)
        
        # Limpiar snapshots futuros si estamos en el medio del historial
        if self.current_snapshot_index < len(self.snapshots) - 1:
            self.snapshots = self.snapshots[:self.current_snapshot_index + 1]
        
        # Agregar nuevo snapshot
        self.snapshots.append(snapshot)
        self.current_snapshot_index = len(self.snapshots) - 1
        
        # Mantener límite de snapshots
        if len(self.snapshots) > self.settings.max_undo_levels:
            self.snapshots.pop(0)
            self.current_snapshot_index -= 1
        
        logger.debug(f"Snapshot creado: {description}")
        return snapshot.id
    
    def can_undo(self) -> bool:
        """Verificar si se puede deshacer"""
        return self.current_snapshot_index > 0
    
    def can_redo(self) -> bool:
        """Verificar si se puede rehacer"""
        return self.current_snapshot_index < len(self.snapshots) - 1
    
    def undo(self) -> bool:
        """
        Deshacer último cambio
        
        Returns:
            True si se pudo deshacer
        """
        if not self.can_undo():
            return False
        
        self.current_snapshot_index -= 1
        snapshot = self.snapshots[self.current_snapshot_index]
        
        # Restaurar estado
        self._restore_from_snapshot(snapshot)
        
        logger.info(f"Deshecho: {snapshot.description}")
        self._notify_change("undo", {"snapshot_id": snapshot.id})
        return True
    
    def redo(self) -> bool:
        """
        Rehacer cambio deshecho
        
        Returns:
            True si se pudo rehacer
        """
        if not self.can_redo():
            return False
        
        self.current_snapshot_index += 1
        snapshot = self.snapshots[self.current_snapshot_index]
        
        # Restaurar estado
        self._restore_from_snapshot(snapshot)
        
        logger.info(f"Rehecho: {snapshot.description}")
        self._notify_change("redo", {"snapshot_id": snapshot.id})
        return True
    
    def _restore_from_snapshot(self, snapshot: ProjectSnapshot):
        """Restaurar proyecto desde snapshot"""
        # Restaurar nodos
        self.nodes.clear()
        for node_id, node_data in snapshot.nodes_data.items():
            self.nodes[node_id] = Node.from_dict(node_data)
        
        # Restaurar metadatos
        self.metadata = ProjectMetadata.from_dict(snapshot.metadata_snapshot)
        
        self._invalidate_cache()
        # No marcar como modificado durante restore
    
    def get_undo_description(self) -> Optional[str]:
        """Obtener descripción del próximo undo"""
        if self.can_undo():
            return self.snapshots[self.current_snapshot_index - 1].description
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Obtener descripción del próximo redo"""
        if self.can_redo():
            return self.snapshots[self.current_snapshot_index + 1].description
        return None
    
    # ==================================================================================
    # ESTADÍSTICAS Y VALIDACIÓN
    # ==================================================================================
    
    def get_statistics(self, use_cache: bool = True) -> Dict[str, Any]:
        """Obtener estadísticas del proyecto"""
        if use_cache and self._stats_cache and self._is_cache_valid():
            return self._stats_cache
        
        stats = calculate_node_statistics(self.nodes)
        
        # Agregar estadísticas específicas del proyecto
        stats.update({
            "project_metadata": {
                "name": self.metadata.name,
                "version": self.metadata.version,
                "created_at": self.metadata.created_at,
                "modified_at": self.metadata.modified_at,
                "tags": len(self.metadata.tags)
            },
            "session_info": {
                "is_modified": self.is_modified,
                "snapshots_count": len(self.snapshots),
                "can_undo": self.can_undo(),
                "can_redo": self.can_redo()
            }
        })
        
        if use_cache:
            self._stats_cache = stats
            self._cache_timestamp = datetime.now()
        
        return stats
    
    def get_completion_statistics(self, use_cache: bool = True) -> Dict[str, Any]:
        """Obtener estadísticas de completitud"""
        if use_cache and self._completion_cache and self._is_cache_valid():
            return self._completion_cache
        
        completion = get_completion_statistics(self.nodes)
        
        if use_cache:
            self._completion_cache = completion
            self._cache_timestamp = datetime.now()
        
        return completion
    
    def validate_integrity(self, use_cache: bool = True) -> List[str]:
        """Validar integridad del proyecto"""
        if use_cache and self._integrity_cache and self._is_cache_valid():
            return self._integrity_cache
        
        errors = validate_tree_integrity(self.nodes)
        
        # Validaciones adicionales específicas del proyecto
        if self.root_node_id and self.root_node_id not in self.nodes:
            errors.append("El nodo raíz especificado no existe")
        
        if not self.nodes:
            errors.append("El proyecto no tiene nodos")
        
        if use_cache:
            self._integrity_cache = errors
            self._cache_timestamp = datetime.now()
        
        return errors
    
    def is_valid(self) -> bool:
        """Verificar si el proyecto es válido"""
        return len(self.validate_integrity()) == 0
    
    # ==================================================================================
    # PERSISTENCIA Y SERIALIZACIÓN
    # ==================================================================================
    
    def to_dict(self, include_snapshots: bool = False) -> Dict[str, Any]:
        """
        Convertir proyecto a diccionario para serialización
        
        Args:
            include_snapshots: Si incluir historial de snapshots
            
        Returns:
            Diccionario con datos del proyecto
        """
        project_data = {
            "format_version": "4.0",
            "project_id": self.id,
            "metadata": self.metadata.to_dict(),
            "settings": self.settings.to_dict(),
            "root_node_id": self.root_node_id,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "export_timestamp": datetime.now().isoformat(),
            "statistics": self.get_statistics()
        }
        
        if include_snapshots:
            project_data["snapshots"] = [
                {
                    "id": snapshot.id,
                    "timestamp": snapshot.timestamp,
                    "description": snapshot.description,
                    "nodes_data": snapshot.nodes_data,
                    "metadata_snapshot": snapshot.metadata_snapshot
                }
                for snapshot in self.snapshots
            ]
            project_data["current_snapshot_index"] = self.current_snapshot_index
        
        return project_data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """
        Crear proyecto desde diccionario
        
        Args:
            data: Diccionario con datos del proyecto
            
        Returns:
            Instancia de Project
        """
        # Crear proyecto básico
        project = cls(
            project_id=data.get("project_id"),
            metadata=ProjectMetadata.from_dict(data.get("metadata", {})),
            settings=ProjectSettings.from_dict(data.get("settings", {}))
        )
        
        # Migrar datos si es necesario
        format_version = data.get("format_version", "1.0")
        nodes_data = data.get("nodes", {})
        
        if format_version < "4.0":
            logger.info(f"Migrando proyecto desde versión {format_version}")
            project.nodes = migrate_legacy_data(nodes_data)
        else:
            # Cargar nodos
            project.nodes = {}
            for node_id, node_data in nodes_data.items():
                project.nodes[node_id] = Node.from_dict(node_data)
        
        # Establecer nodo raíz
        project.root_node_id = data.get("root_node_id")
        
        # Cargar snapshots si están presentes
        if "snapshots" in data:
            snapshots_data = data["snapshots"]
            for snapshot_data in snapshots_data:
                snapshot = ProjectSnapshot(
                    id=snapshot_data["id"],
                    timestamp=snapshot_data["timestamp"],
                    description=snapshot_data["description"],
                    nodes_data=snapshot_data["nodes_data"],
                    metadata_snapshot=snapshot_data["metadata_snapshot"]
                )
                project.snapshots.append(snapshot)
            
            project.current_snapshot_index = data.get("current_snapshot_index", -1)
        
        project.is_loaded = True
        project._invalidate_cache()
        
        return project
    
    def save(self, file_path: Optional[str] = None, include_snapshots: bool = True) -> bool:
        """
        Guardar proyecto a archivo
        
        Args:
            file_path: Ruta del archivo (usa self.file_path si es None)
            include_snapshots: Si incluir historial
            
        Returns:
            True si se guardó correctamente
        """
        save_path = file_path or self.file_path
        if not save_path:
            logger.error("No se especificó ruta para guardar")
            return False
        
        try:
            # Actualizar timestamps
            self.metadata.modified_at = datetime.now().isoformat()
            
            # Serializar datos
            project_data = self.to_dict(include_snapshots=include_snapshots)
            
            # Guardar archivo
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            # Actualizar estado
            self.file_path = save_path
            self.is_modified = False
            self.last_save_time = datetime.now()
            
            logger.info(f"Proyecto guardado en: {save_path}")
            self._notify_change("project_saved", {"file_path": save_path})
            return True
            
        except Exception as e:
            logger.error(f"Error guardando proyecto: {e}")
            return False
    
    @classmethod
    def load(cls, file_path: str) -> Optional['Project']:
        """
        Cargar proyecto desde archivo
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Instancia de Project o None si hay error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = cls.from_dict(data)
            project.file_path = file_path
            project.metadata.last_opened_at = datetime.now().isoformat()
            
            logger.info(f"Proyecto cargado desde: {file_path}")
            return project
            
        except Exception as e:
            logger.error(f"Error cargando proyecto desde {file_path}: {e}")
            return None
    
    # ==================================================================================
    # UTILIDADES Y HELPERS
    # ==================================================================================
    
    def _mark_modified(self, description: str = "Cambio automático"):
        """Marcar proyecto como modificado y crear snapshot"""
        if not self.is_modified:
            self.is_modified = True
            self._notify_change("project_modified", {"description": description})
        
        # Crear snapshot si está habilitado
        if self.settings.enable_undo_redo:
            self.create_snapshot(description)
    
    def _invalidate_cache(self):
        """Invalidar cache de estadísticas"""
        self._stats_cache = None
        self._completion_cache = None
        self._integrity_cache = None
        self._cache_timestamp = None
    
    def _is_cache_valid(self, max_age_seconds: int = 30) -> bool:
        """Verificar si el cache es válido"""
        if not self._cache_timestamp:
            return False
        
        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age <= max_age_seconds
    
    def add_change_listener(self, listener: callable):
        """Agregar listener para cambios del proyecto"""
        if listener not in self._change_listeners:
            self._change_listeners.append(listener)
    
    def remove_change_listener(self, listener: callable):
        """Remover listener de cambios"""
        if listener in self._change_listeners:
            self._change_listeners.remove(listener)
    
    def _notify_change(self, event_type: str, data: Dict[str, Any]):
        """Notificar cambios a listeners"""
        for listener in self._change_listeners:
            try:
                listener(event_type, data)
            except Exception as e:
                logger.error