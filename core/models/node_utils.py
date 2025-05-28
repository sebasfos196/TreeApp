#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades y Helpers para TreeApp v4 Pro
Funciones de conveniencia, validadores y operaciones auxiliares para nodos
"""

from typing import Dict, List, Optional, Tuple, Any, Callable, Set
import re
import logging
from datetime import datetime
from collections import defaultdict, Counter

from .node import Node, NodeType, NodeStatus, EditorFields, NodeMetadata, INVALID_CHAR_PATTERN
from .clipboard import ClipboardData

logger = logging.getLogger(__name__)

# ==================================================================================
# FUNCIONES DE CREACIÓN DE NODOS
# ==================================================================================

def create_file_node(name: str, 
                    parent_id: Optional[str] = None,
                    markdown_content: str = "",
                    technical_notes: str = "",
                    code_content: str = "") -> Node:
    """
    Función de conveniencia para crear un nodo archivo
    
    Args:
        name: Nombre del archivo
        parent_id: ID del padre
        markdown_content: Contenido markdown inicial
        technical_notes: Notas técnicas iniciales
        code_content: Código inicial
        
    Returns:
        Nuevo nodo archivo
    """
    editor_fields = EditorFields(
        name=name,
        markdown_content=markdown_content or f"# {name}\n\nContenido del archivo...",
        technical_notes=technical_notes,
        code_content=code_content
    )
    
    return Node(
        name=name,
        node_type=NodeType.FILE,
        parent_id=parent_id,
        editor_fields=editor_fields
    )

def create_folder_node(name: str,
                      parent_id: Optional[str] = None,
                      technical_notes: str = "") -> Node:
    """
    Función de conveniencia para crear un nodo carpeta
    
    Args:
        name: Nombre de la carpeta
        parent_id: ID del padre
        technical_notes: Notas técnicas iniciales
        
    Returns:
        Nuevo nodo carpeta
    """
    editor_fields = EditorFields(
        name=name,
        markdown_content=f"# {name}\n\nDescripción de la carpeta...",
        technical_notes=technical_notes,
        code_content=""
    )
    
    return Node(
        name=name,
        node_type=NodeType.FOLDER,
        parent_id=parent_id,
        editor_fields=editor_fields
    )

def create_root_node(project_name: str = "Root") -> Node:
    """
    Crear nodo raíz del proyecto
    
    Args:
        project_name: Nombre del proyecto
        
    Returns:
        Nodo raíz
    """
    editor_fields = EditorFields(
        name=project_name,
        markdown_content=f"# {project_name}\n\nProyecto principal...",
        technical_notes="Carpeta raíz del proyecto",
        code_content=""
    )
    
    return Node(
        name=project_name,
        node_type=NodeType.FOLDER,
        node_id="root",
        editor_fields=editor_fields
    )

def create_template_node(template_type: str, name: str) -> Node:
    """
    Crear nodo basado en plantilla predefinida
    
    Args:
        template_type: Tipo de plantilla ("readme", "config", "script", etc.)
        name: Nombre del nodo
        
    Returns:
        Nodo basado en plantilla
    """
    templates = {
        "readme": {
            "markdown": f"# {name}\n\n## Descripción\n\n## Instalación\n\n## Uso\n\n",
            "notes": "Archivo README principal del proyecto"
        },
        "config": {
            "markdown": f"# {name}\n\nArchivo de configuración",
            "notes": "Configuración del proyecto",
            "code": "{\n  \"version\": \"1.0\",\n  \"name\": \"" + name + "\"\n}"
        },
        "script": {
            "markdown": f"# {name}\n\nScript de automatización",
            "notes": "Script para tareas automatizadas",
            "code": "#!/usr/bin/env python3\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()"
        },
        "documentation": {
            "markdown": f"# {name}\n\n## Índice\n\n## Secciones\n\n",
            "notes": "Documentación técnica"
        },
        "test": {
            "markdown": f"# Tests for {name}\n\n## Test Cases\n\n",
            "notes": "Archivo de pruebas unitarias",
            "code": "import unittest\n\nclass Test" + name.replace('.', '').replace(' ', '') + "(unittest.TestCase):\n    def test_example(self):\n        pass"
        },
        "api": {
            "markdown": f"# {name} API\n\n## Endpoints\n\n## Authentication\n\n",
            "notes": "Documentación de API",
            "code": "# API Routes\n# GET /api/v1/\n# POST /api/v1/"
        }
    }
    
    template = templates.get(template_type, templates["readme"])
    
    editor_fields = EditorFields(
        name=name,
        markdown_content=template.get("markdown", f"# {name}\n\n"),
        technical_notes=template.get("notes", ""),
        code_content=template.get("code", "")
    )
    
    # Determinar tipo de archivo basado en extensión
    node_type = NodeType.FILE if "." in name else NodeType.FOLDER
    
    node = Node(
        name=name,
        node_type=node_type,
        editor_fields=editor_fields
    )
    
    # Agregar tag de plantilla
    node.add_tag(f"plantilla-{template_type}")
    
    return node

# ==================================================================================
# VALIDADORES DE OPERACIONES
# ==================================================================================

def can_paste_nodes(clipboard_data: ClipboardData, 
                   target_parent_id: str,
                   nodes_registry: Dict[str, Node]) -> Tuple[bool, str]:
    """
    Verificar si se pueden pegar nodos en una ubicación
    
    Args:
        clipboard_data: Datos del portapapeles
        target_parent_id: ID del padre de destino
        nodes_registry: Registro de nodos
        
    Returns:
        Tupla (es_posible, mensaje_error)
    """
    if clipboard_data.is_empty():
        return False, "El portapapeles está vacío"
    
    if target_parent_id not in nodes_registry:
        return False, "El destino no existe"
    
    target_parent = nodes_registry[target_parent_id]
    if not target_parent.is_folder:
        return False, "El destino debe ser una carpeta"
    
    # Verificar que no se pegue un nodo dentro de sí mismo
    for node_id in clipboard_data.node_ids:
        if node_id not in nodes_registry:
            continue
        
        # Verificar si el destino es descendiente del nodo a pegar
        current_id = target_parent_id
        while current_id and current_id in nodes_registry:
            if current_id == node_id:
                return False, f"No se puede pegar el nodo {node_id} dentro de sí mismo"
            current_id = nodes_registry[current_id].parent_id
    
    return True, ""

def validate_node_move(node_id: str, 
                      target_parent_id: str,
                      nodes_registry: Dict[str, Node]) -> Tuple[bool, str]:
    """
    Validar si se puede mover un nodo a una nueva ubicación
    
    Args:
        node_id: ID del nodo a mover
        target_parent_id: ID del nuevo padre
        nodes_registry: Registro de nodos
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if node_id not in nodes_registry:
        return False, "El nodo no existe"
    
    if target_parent_id not in nodes_registry:
        return False, "El destino no existe"
    
    if node_id == target_parent_id:
        return False, "No se puede mover un nodo dentro de sí mismo"
    
    target_parent = nodes_registry[target_parent_id]
    if not target_parent.is_folder:
        return False, "El destino debe ser una carpeta"
    
    # Verificar que no se mueva a un descendiente
    current_id = target_parent_id
    while current_id and current_id in nodes_registry:
        if current_id == node_id:
            return False, "No se puede mover un nodo a sus descendientes"
        current_id = nodes_registry[current_id].parent_id
    
    return True, ""

def validate_node_name(name: str, 
                      parent_id: Optional[str],
                      nodes_registry: Dict[str, Node],
                      exclude_node_id: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validar si un nombre de nodo es válido y único en su contexto
    
    Args:
        name: Nombre a validar
        parent_id: ID del padre
        nodes_registry: Registro de nodos
        exclude_node_id: ID del nodo a excluir de la validación (para renombrado)
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not name or not name.strip():
        return False, "El nombre no puede estar vacío"
    
    # Verificar caracteres inválidos
    if INVALID_CHAR_PATTERN.search(name):
        return False, "El nombre contiene caracteres no válidos: <>:\"/\\|?*"
    
    # Verificar longitud
    if len(name) > 255:
        return False, "El nombre es demasiado largo (máximo 255 caracteres)"
    
    # Verificar unicidad entre hermanos
    siblings = get_sibling_nodes(parent_id, nodes_registry)
    for sibling in siblings:
        if sibling.id != exclude_node_id and sibling.name.lower() == name.lower():
            return False, f"Ya existe un elemento con el nombre '{name}'"
    
    return True, ""

def get_sibling_nodes(parent_id: Optional[str], nodes_registry: Dict[str, Node]) -> List[Node]:
    """
    Obtener nodos hermanos de un padre específico
    
    Args:
        parent_id: ID del padre (None para nodos raíz)
        nodes_registry: Registro de nodos
        
    Returns:
        Lista de nodos hermanos
    """
    siblings = []
    for node in nodes_registry.values():
        if node.parent_id == parent_id:
            siblings.append(node)
    return siblings

# ==================================================================================
# RESOLUCIÓN DE CONFLICTOS
# ==================================================================================

def resolve_name_conflicts(names: List[str], 
                          existing_names: Set[str],
                          strategy: str = "append_number") -> List[str]:
    """
    Resolver conflictos de nombres automáticamente
    
    Args:
        names: Lista de nombres a resolver
        existing_names: Set de nombres existentes
        strategy: Estrategia de resolución ("append_number", "prepend_number", "timestamp")
        
    Returns:
        Lista de nombres sin conflictos
    """
    resolved_names = []
    used_names = existing_names.copy()
    
    for name in names:
        if name not in used_names:
            resolved_names.append(name)
            used_names.add(name)
        else:
            resolved_name = _resolve_single_name_conflict(name, used_names, strategy)
            resolved_names.append(resolved_name)
            used_names.add(resolved_name)
    
    return resolved_names

def _resolve_single_name_conflict(name: str, used_names: Set[str], strategy: str) -> str:
    """Resolver conflicto de un nombre individual"""
    if strategy == "append_number":
        base_name, extension = _split_name_extension(name)
        counter = 1
        while True:
            candidate = f"{base_name} ({counter}){extension}"
            if candidate not in used_names:
                return candidate
            counter += 1
            if counter > 1000:  # Prevenir bucle infinito
                break
    
    elif strategy == "prepend_number":
        counter = 1
        while True:
            candidate = f"({counter}) {name}"
            if candidate not in used_names:
                return candidate
            counter += 1
            if counter > 1000:
                break
    
    elif strategy == "timestamp":
        import time
        timestamp = str(int(time.time()))
        base_name, extension = _split_name_extension(name)
        return f"{base_name}_{timestamp}{extension}"
    
    # Fallback
    import uuid
    base_name, extension = _split_name_extension(name)
    return f"{base_name}_{str(uuid.uuid4())[:8]}{extension}"

def _split_name_extension(name: str) -> Tuple[str, str]:
    """Separar nombre y extensión"""
    if '.' in name and not name.startswith('.'):
        parts = name.rsplit('.', 1)
        return parts[0], f".{parts[1]}"
    return name, ""

def resolve_path_conflicts(paths: List[str], 
                          nodes_registry: Dict[str, Node]) -> Dict[str, str]:
    """
    Resolver conflictos de rutas completas
    
    Args:
        paths: Lista de rutas a verificar
        nodes_registry: Registro de nodos
        
    Returns:
        Diccionario con {ruta_original: ruta_resuelta}
    """
    existing_paths = set()
    for node in nodes_registry.values():
        path = node.get_full_path(nodes_registry)
        existing_paths.add(path.lower())
    
    resolved_paths = {}
    for path in paths:
        if path.lower() not in existing_paths:
            resolved_paths[path] = path
        else:
            # Resolver conflicto de ruta
            resolved_path = _resolve_path_conflict(path, existing_paths)
            resolved_paths[path] = resolved_path
            existing_paths.add(resolved_path.lower())
    
    return resolved_paths

def _resolve_path_conflict(path: str, existing_paths: Set[str]) -> str:
    """Resolver conflicto de una ruta específica"""
    parts = path.split('/')
    if parts:
        # Modificar el último componente
        last_part = parts[-1]
        base_name, extension = _split_name_extension(last_part)
        
        counter = 1
        while True:
            new_last_part = f"{base_name} ({counter}){extension}"
            new_path = '/'.join(parts[:-1] + [new_last_part])
            if new_path.lower() not in existing_paths:
                return new_path
            counter += 1
            if counter > 1000:
                break
    
    # Fallback
    import time
    return f"{path}_{int(time.time())}"

# ==================================================================================
# BÚSQUEDA Y FILTRADO
# ==================================================================================

def find_nodes_by_criteria(nodes_registry: Dict[str, Node],
                          name_pattern: Optional[str] = None,
                          node_type: Optional[NodeType] = None,
                          status: Optional[NodeStatus] = None,
                          tags: Optional[List[str]] = None,
                          content_pattern: Optional[str] = None,
                          case_sensitive: bool = False) -> List[Node]:
    """
    Buscar nodos por múltiples criterios
    
    Args:
        nodes_registry: Registro de nodos
        name_pattern: Patrón para buscar en el nombre (regex opcional)
        node_type: Tipo de nodo a filtrar
        status: Estado a filtrar
        tags: Lista de tags que debe tener
        content_pattern: Patrón para buscar en contenido markdown
        case_sensitive: Si la búsqueda es sensible a mayúsculas
        
    Returns:
        Lista de nodos que cumplen los criterios
    """
    matching_nodes = []
    
    # Compilar patrones regex si es necesario
    name_regex = None
    content_regex = None
    
    if name_pattern:
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            name_regex = re.compile(name_pattern, flags)
        except re.error:
            # Si no es regex válido, usar búsqueda literal
            name_pattern_lower = name_pattern if case_sensitive else name_pattern.lower()
    
    if content_pattern:
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            content_regex = re.compile(content_pattern, flags)
        except re.error:
            content_pattern_lower = content_pattern if case_sensitive else content_pattern.lower()
    
    for node in nodes_registry.values():
        # Filtro por nombre
        if name_pattern:
            if name_regex:
                if not name_regex.search(node.name):
                    continue
            else:
                node_name = node.name if case_sensitive else node.name.lower()
                if name_pattern_lower not in node_name:
                    continue
        
        # Filtro por tipo
        if node_type and node.type != node_type:
            continue
        
        # Filtro por estado
        if status and node.status != status:
            continue
        
        # Filtro por tags
        if tags:
            if not all(tag in node.metadata.tags for tag in tags):
                continue
        
        # Filtro por contenido
        if content_pattern:
            content = node.editor_fields.markdown_content
            if content_regex:
                if not content_regex.search(content):
                    continue
            else:
                content_search = content if case_sensitive else content.lower()
                if content_pattern_lower not in content_search:
                    continue
        
        matching_nodes.append(node)
    
    return matching_nodes

def filter_nodes_by_predicate(nodes_registry: Dict[str, Node],
                             predicate: Callable[[Node], bool]) -> List[Node]:
    """
    Filtrar nodos usando un predicado personalizado
    
    Args:
        nodes_registry: Registro de nodos
        predicate: Función que retorna True para nodos que deben incluirse
        
    Returns:
        Lista de nodos filtrados
    """
    filtered_nodes = []
    for node in nodes_registry.values():
        try:
            if predicate(node):
                filtered_nodes.append(node)
        except Exception as e:
            logger.warning(f"Error aplicando predicado a nodo {node.id}: {e}")
    
    return filtered_nodes

def get_nodes_by_depth(nodes_registry: Dict[str, Node],
                      max_depth: Optional[int] = None,
                      root_id: Optional[str] = None) -> Dict[int, List[Node]]:
    """
    Organizar nodos por profundidad en el árbol
    
    Args:
        nodes_registry: Registro de nodos
        max_depth: Profundidad máxima (None para ilimitado)
        root_id: ID del nodo raíz (None para usar raíces del árbol)
        
    Returns:
        Diccionario {profundidad: [nodos]}
    """
    nodes_by_depth = defaultdict(list)
    
    # Encontrar nodos raíz si no se especifica
    if root_id is None:
        root_nodes = [node for node in nodes_registry.values() if node.parent_id is None]
    else:
        root_nodes = [nodes_registry[root_id]] if root_id in nodes_registry else []
    
    # BFS para calcular profundidades
    queue = [(node, 0) for node in root_nodes]
    
    while queue:
        node, depth = queue.pop(0)
        
        # Verificar límite de profundidad
        if max_depth is not None and depth > max_depth:
            continue
        
        nodes_by_depth[depth].append(node)
        
        # Agregar hijos a la cola
        for child_id in node.children_ids:
            if child_id in nodes_registry:
                queue.append((nodes_registry[child_id], depth + 1))
    
    return dict(nodes_by_depth)

# ==================================================================================
# ESTADÍSTICAS Y ANÁLISIS
# ==================================================================================

def calculate_node_statistics(nodes_registry: Dict[str, Node]) -> Dict[str, Any]:
    """
    Calcular estadísticas completas del árbol de nodos
    
    Args:
        nodes_registry: Registro de nodos
        
    Returns:
        Diccionario con estadísticas detalladas
    """
    stats = {
        "total_nodes": len(nodes_registry),
        "files": 0,
        "folders": 0,
        "by_status": defaultdict(int),
        "by_tags": Counter(),
        "depth_stats": {},
        "content_stats": {},
        "size_stats": {},
        "modification_stats": {}
    }
    
    # Estadísticas básicas
    for node in nodes_registry.values():
        if node.is_file:
            stats["files"] += 1
        else:
            stats["folders"] += 1
        
        # Por estado
        stats["by_status"][node.status.value] += 1
        
        # Por tags
        for tag in node.metadata.tags:
            stats["by_tags"][tag] += 1
    
    # Estadísticas de profundidad
    depth_info = get_nodes_by_depth(nodes_registry)
    stats["depth_stats"] = {
        "max_depth": max(depth_info.keys()) if depth_info else 0,
        "avg_depth": sum(d * len(nodes) for d, nodes in depth_info.items()) / len(nodes_registry) if nodes_registry else 0,
        "nodes_by_depth": {d: len(nodes) for d, nodes in depth_info.items()}
    }
    
    # Estadísticas de contenido
    total_markdown_chars = 0
    total_code_chars = 0
    total_notes_chars = 0
    
    for node in nodes_registry.values():
        total_markdown_chars += len(node.editor_fields.markdown_content)
        total_code_chars += len(node.editor_fields.code_content)
        total_notes_chars += len(node.editor_fields.technical_notes)
    
    stats["content_stats"] = {
        "total_markdown_chars": total_markdown_chars,
        "total_code_chars": total_code_chars,
        "total_notes_chars": total_notes_chars,
        "avg_markdown_per_node": total_markdown_chars / len(nodes_registry) if nodes_registry else 0,
        "avg_code_per_node": total_code_chars / len(nodes_registry) if nodes_registry else 0,
        "avg_notes_per_node": total_notes_chars / len(nodes_registry) if nodes_registry else 0
    }
    
    # Estadísticas de modificación
    if nodes_registry:
        modification_times = []
        for node in nodes_registry.values():
            try:
                mod_time = datetime.fromisoformat(node.metadata.modified_at)
                modification_times.append(mod_time)
            except:
                pass
        
        if modification_times:
            stats["modification_stats"] = {
                "oldest_modification": min(modification_times).isoformat(),
                "newest_modification": max(modification_times).isoformat(),
                "total_with_modifications": len(modification_times)
            }
    
    return stats

def get_completion_statistics(nodes_registry: Dict[str, Node]) -> Dict[str, Any]:
    """
    Calcular estadísticas específicas de completitud
    
    Args:
        nodes_registry: Registro de nodos
        
    Returns:
        Diccionario con estadísticas de completitud
    """
    files_only = [node for node in nodes_registry.values() if node.is_file]
    total_files = len(files_only)
    
    if total_files == 0:
        return {
            "total_files": 0,
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "no_status": 0,
            "completion_percentage": 0,
            "progress_percentage": 0
        }
    
    completed = sum(1 for node in files_only if node.status == NodeStatus.COMPLETED)
    in_progress = sum(1 for node in files_only if node.status == NodeStatus.IN_PROGRESS)
    pending = sum(1 for node in files_only if node.status == NodeStatus.PENDING)
    no_status = sum(1 for node in files_only if node.status == NodeStatus.NONE)
    
    # Calcular porcentajes
    completion_percentage = (completed / total_files) * 100
    progress_percentage = ((completed + in_progress) / total_files) * 100
    
    return {
        "total_files": total_files,
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "no_status": no_status,
        "completion_percentage": round(completion_percentage, 1),
        "progress_percentage": round(progress_percentage, 1)
    }

# ==================================================================================
# EXPORTACIÓN Y PREPARACIÓN DE DATOS
# ==================================================================================

def prepare_nodes_for_export(nodes_registry: Dict[str, Node],
                            root_id: Optional[str] = None,
                            include_metadata: bool = True,
                            flatten_structure: bool = False) -> List[Dict[str, Any]]:
    """
    Preparar nodos para exportación
    
    Args:
        nodes_registry: Registro de nodos
        root_id: ID del nodo raíz (None para exportar todo)
        include_metadata: Si incluir metadatos completos
        flatten_structure: Si aplanar la estructura jerárquica
        
    Returns:
        Lista de diccionarios con datos de nodos preparados
    """
    export_data = []
    
    # Determinar nodos a exportar
    if root_id and root_id in nodes_registry:
        nodes_to_export = _get_subtree_nodes(root_id, nodes_registry)
    else:
        nodes_to_export = list(nodes_registry.values())
    
    # Ordenar por jerarquía si no se aplana
    if not flatten_structure:
        nodes_to_export = _sort_nodes_hierarchically(nodes_to_export, nodes_registry)
    
    for node in nodes_to_export:
        node_data = {
            "id": node.id,
            "name": node.name,
            "type": node.type.value,
            "status": node.status.value,
            "parent_id": node.parent_id,
            "path": node.get_full_path(nodes_registry),
            "editor_fields": node.editor_fields.to_dict()
        }
        
        if include_metadata:
            node_data["metadata"] = node.metadata.to_dict()
            node_data["children_count"] = len(node.children_ids)
            node_data["depth"] = len(node.get_path_components(nodes_registry)) - 1
        
        export_data.append(node_data)
    
    return export_data

def _get_subtree_nodes(root_id: str, nodes_registry: Dict[str, Node]) -> List[Node]:
    """Obtener todos los nodos de un subárbol"""
    subtree_nodes = []
    queue = [root_id]
    
    while queue:
        node_id = queue.pop(0)
        if node_id in nodes_registry:
            node = nodes_registry[node_id]
            subtree_nodes.append(node)
            queue.extend(node.children_ids)
    
    return subtree_nodes

def _sort_nodes_hierarchically(nodes: List[Node], nodes_registry: Dict[str, Node]) -> List[Node]:
    """Ordenar nodos manteniendo jerarquía (padres antes que hijos)"""
    # Crear mapeo de profundidad
    depth_map = {}
    for node in nodes:
        depth_map[node.id] = len(node.get_path_components(nodes_registry))
    
    # Ordenar por profundidad y luego por nombre
    return sorted(nodes, key=lambda n: (depth_map.get(n.id, 0), n.name.lower()))

def generate_node_summary(nodes_registry: Dict[str, Node],
                         include_stats: bool = True,
                         include_structure: bool = True) -> str:
    """
    Generar resumen textual del árbol de nodos
    
    Args:
        nodes_registry: Registro de nodos
        include_stats: Si incluir estadísticas
        include_structure: Si incluir estructura básica
        
    Returns:
        Texto con resumen del proyecto
    """
    lines = []
    
    # Encabezado
    lines.append("=" * 60)
    lines.append("RESUMEN DEL PROYECTO")
    lines.append("=" * 60)
    lines.append("")
    
    # Estadísticas generales
    if include_stats:
        stats = calculate_node_statistics(nodes_registry)
        completion = get_completion_statistics(nodes_registry)
        
        lines.append("📊 ESTADÍSTICAS GENERALES:")
        lines.append(f"   Total de nodos: {stats['total_nodes']}")
        lines.append(f"   Archivos: {stats['files']}")
        lines.append(f"   Carpetas: {stats['folders']}")
        lines.append(f"   Profundidad máxima: {stats['depth_stats']['max_depth']}")
        lines.append("")
        
        lines.append("✅ ESTADO DE COMPLETITUD:")
        lines.append(f"   Completados: {completion['completed']}")
        lines.append(f"   En progreso: {completion['in_progress']}")
        lines.append(f"   Pendientes: {completion['pending']}")
        lines.append(f"   Progreso total: {completion['completion_percentage']}%")
        lines.append("")
        
        # Tags más comunes
        if stats['by_tags']:
            lines.append("🏷️ TAGS MÁS USADOS:")
            for tag, count in stats['by_tags'].most_common(5):
                lines.append(f"   #{tag}: {count} veces")
            lines.append("")
    
    # Estructura básica
    if include_structure:
        lines.append("🌳 ESTRUCTURA DEL PROYECTO:")
        
        # Encontrar nodos raíz
        root_nodes = [node for node in nodes_registry.values() if node.parent_id is None]
        
        for root in root_nodes:
            lines.extend(_generate_tree_structure_lines(root, nodes_registry, max_depth=3))
        
        lines.append("")
    
    # Información de contenido
    if include_stats and nodes_registry:
        content_stats = stats['content_stats']
        lines.append("📝 CONTENIDO:")
        lines.append(f"   Total caracteres markdown: {content_stats['total_markdown_chars']:,}")
        lines.append(f"   Total caracteres código: {content_stats['total_code_chars']:,}")
        lines.append(f"   Total caracteres notas: {content_stats['total_notes_chars']:,}")
        lines.append("")
    
    # Timestamp
    lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)
    
    return "\n".join(lines)

def _generate_tree_structure_lines(node: Node, 
                                 nodes_registry: Dict[str, Node],
                                 prefix: str = "",
                                 max_depth: int = 3,
                                 current_depth: int = 0) -> List[str]:
    """Generar líneas de estructura de árbol para el resumen"""
    lines = []
    
    if current_depth > max_depth:
        return lines
    
    # Icono y nombre
    icon = "📁" if node.is_folder else "📄"
    status = f" {node.status.value}" if node.status != NodeStatus.NONE else ""
    
    lines.append(f"{prefix}{icon} {node.name}{status}")
    
    # Procesar hijos (máximo 5 por nivel para mantener resumen conciso)
    children = [nodes_registry[child_id] for child_id in node.children_ids[:5] 
               if child_id in nodes_registry]
    
    for i, child in enumerate(children):
        is_last = i == len(children) - 1
        child_prefix = prefix + ("   " if is_last else "│  ")
        lines.extend(_generate_tree_structure_lines(
            child, nodes_registry, child_prefix, max_depth, current_depth + 1
        ))
    
    # Indicar si hay más hijos
    if len(node.children_ids) > 5:
        lines.append(f"{prefix}   ... y {len(node.children_ids) - 5} más")
    
    return lines

# ==================================================================================
# DEBUGGING Y VALIDACIÓN DE INTEGRIDAD
# ==================================================================================

def validate_tree_integrity(nodes_registry: Dict[str, Node]) -> List[str]:
    """
    Validar la integridad completa del árbol de nodos
    
    Args:
        nodes_registry: Registro de nodos
        
    Returns:
        Lista de errores encontrados (vacía si todo está bien)
    """
    errors = []
    
    # 1. Validar referencias padre-hijo
    for node_id, node in nodes_registry.items():
        # Verificar que el padre existe
        if node.parent_id and node.parent_id not in nodes_registry:
            errors.append(f"Nodo {node_id} tiene padre inexistente: {node.parent_id}")
        
        # Verificar que los hijos existen
        for child_id in node.children_ids:
            if child_id not in nodes_registry:
                errors.append(f"Nodo {node_id} tiene hijo inexistente: {child_id}")
        
        # Verificar reciprocidad padre-hijo
        if node.parent_id and node.parent_id in nodes_registry:
            parent = nodes_registry[node.parent_id]
            if node_id not in parent.children_ids:
                errors.append(f"Nodo {node_id} no está en la lista de hijos de su padre {node.parent_id}")
    
    # 2. Verificar que no hay ciclos
    for node_id in nodes_registry:
        if _has_cycle(node_id, nodes_registry):
            errors.append(f"Detectado ciclo en el árbol que incluye el nodo {node_id}")
    
    # 3. Validar que las carpetas no tienen archivos como padres
    for node in nodes_registry.values():
        if node.parent_id and node.parent_id in nodes_registry:
            parent = nodes_registry[node.parent_id]
            if parent.is_file:
                errors.append(f"Nodo {node.id} tiene un archivo como padre: {node.parent_id}")
    
    # 4. Validar unicidad de nombres entre hermanos
    siblings_by_parent = defaultdict(list)
    for node in nodes_registry.values():
        siblings_by_parent[node.parent_id].append(node)
    
    for parent_id, siblings in siblings_by_parent.items():
        names = [node.name.lower() for node in siblings]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            errors.append(f"Nombres duplicados entre hermanos de {parent_id}: {set(duplicates)}")
    
    # 5. Validar IDs únicos
    if len(set(nodes_registry.keys())) != len(nodes_registry):
        errors.append("Se encontraron IDs duplicados en el registro")
    
    # 6. Validar datos individuales de nodos
    for node_id, node in nodes_registry.items():
        node_errors = node.validate()
        for error in node_errors:
            errors.append(f"Nodo {node_id}: {error}")
    
    return errors

def _has_cycle(start_node_id: str, nodes_registry: Dict[str, Node], visited: Set[str] = None) -> bool:
    """Detectar ciclos en el árbol usando DFS"""
    if visited is None:
        visited = set()
    
    if start_node_id in visited:
        return True
    
    if start_node_id not in nodes_registry:
        return False
    
    visited.add(start_node_id)
    node = nodes_registry[start_node_id]
    
    # Verificar ciclos hacia arriba (padre)
    if node.parent_id and _has_cycle(node.parent_id, nodes_registry, visited.copy()):
        return True
    
    # Verificar ciclos hacia abajo (hijos)
    for child_id in node.children_ids:
        if _has_cycle(child_id, nodes_registry, visited.copy()):
            return True
    
    return False

def print_tree_structure(nodes_registry: Dict[str, Node],
                        root_id: Optional[str] = None,
                        max_depth: Optional[int] = None,
                        show_ids: bool = False,
                        show_status: bool = True,
                        show_metadata: bool = False) -> str:
    """
    Generar representación textual del árbol para debugging
    
    Args:
        nodes_registry: Registro de nodos
        root_id: ID del nodo raíz (None para mostrar todos los raíces)
        max_depth: Profundidad máxima a mostrar
        show_ids: Si mostrar IDs de nodos
        show_status: Si mostrar estados
        show_metadata: Si mostrar metadatos básicos
        
    Returns:
        Representación textual del árbol
    """
    lines = []
    
    # Encontrar nodos raíz
    if root_id and root_id in nodes_registry:
        root_nodes = [nodes_registry[root_id]]
    else:
        root_nodes = [node for node in nodes_registry.values() if node.parent_id is None]
    
    if not root_nodes:
        return "Árbol vacío o sin nodos raíz válidos"
    
    for i, root_node in enumerate(root_nodes):
        if i > 0:
            lines.append("")  # Separador entre árboles
        
        lines.extend(_print_node_recursive(
            root_node, nodes_registry, "", True, max_depth, 0,
            show_ids, show_status, show_metadata
        ))
    
    return "\n".join(lines)

def _print_node_recursive(node: Node,
                         nodes_registry: Dict[str, Node],
                         prefix: str,
                         is_last: bool,
                         max_depth: Optional[int],
                         current_depth: int,
                         show_ids: bool,
                         show_status: bool,
                         show_metadata: bool) -> List[str]:
    """Imprimir nodo recursivamente para debugging"""
    lines = []
    
    # Verificar límite de profundidad
    if max_depth is not None and current_depth > max_depth:
        return lines
    
    # Construir línea del nodo
    connector = "└── " if is_last else "├── "
    icon = "📁" if node.is_folder else "📄"
    
    line_parts = [f"{prefix}{connector}{icon} {node.name}"]
    
    if show_status and node.status != NodeStatus.NONE:
        line_parts.append(f" {node.status.value}")
    
    if show_ids:
        line_parts.append(f" (ID: {node.id})")
    
    if show_metadata:
        metadata_parts = []
        if node.metadata.tags:
            metadata_parts.append(f"tags: {','.join(node.metadata.tags[:3])}")
        if node.metadata.priority != 0:
            metadata_parts.append(f"priority: {node.metadata.priority}")
        if metadata_parts:
            line_parts.append(f" [{'; '.join(metadata_parts)}]")
    
    lines.append("".join(line_parts))
    
    # Procesar hijos
    children = [nodes_registry[child_id] for child_id in node.children_ids 
               if child_id in nodes_registry]
    
    for i, child in enumerate(children):
        child_is_last = i == len(children) - 1
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        lines.extend(_print_node_recursive(
            child, nodes_registry, child_prefix, child_is_last,
            max_depth, current_depth + 1, show_ids, show_status, show_metadata
        ))
    
    return lines

# ==================================================================================
# UTILIDADES DE CONVERSIÓN Y MIGRACIÓN
# ==================================================================================

def migrate_legacy_data(legacy_data: Dict[str, Any]) -> Dict[str, Node]:
    """
    Migrar datos de versiones anteriores al formato actual
    
    Args:
        legacy_data: Datos en formato anterior
        
    Returns:
        Diccionario de nodos migrados
    """
    migrated_nodes = {}
    
    for node_id, node_data in legacy_data.items():
        try:
            # Migrar campos faltantes
            if "editor_fields" not in node_data:
                # Crear editor_fields desde datos legacy
                editor_fields_data = {
                    "name": node_data.get("name", ""),
                    "markdown_content": node_data.get("content", ""),
                    "technical_notes": node_data.get("description", ""),
                    "code_content": ""
                }
                node_data["editor_fields"] = editor_fields_data
            
            if "metadata" not in node_data:
                # Crear metadata básico
                metadata_data = {
                    "tags": node_data.get("tags", []),
                    "created_at": node_data.get("created", datetime.now().isoformat()),
                    "modified_at": node_data.get("modified", datetime.now().isoformat())
                }
                node_data["metadata"] = metadata_data
            
            # Migrar estados legacy
            if "status" in node_data:
                status_mapping = {
                    "done": "✅",
                    "todo": "❌", 
                    "doing": "⬜",
                    "🕓": "⬜"  # Migrar reloj a cuadrado
                }
                old_status = node_data["status"]
                if old_status in status_mapping:
                    node_data["status"] = status_mapping[old_status]
            
            # Crear nodo desde datos migrados
            migrated_node = Node.from_dict(node_data)
            migrated_nodes[node_id] = migrated_node
            
        except Exception as e:
            logger.error(f"Error migrando nodo {node_id}: {e}")
            # Crear nodo básico como fallback
            fallback_node = create_file_node(
                name=node_data.get("name", f"nodo_{node_id}"),
                markdown_content=node_data.get("content", "")
            )
            fallback_node.id = node_id
            migrated_nodes[node_id] = fallback_node
    
    # Validar integridad después de migración
    errors = validate_tree_integrity(migrated_nodes)
    if errors:
        logger.warning(f"Errores de integridad después de migración: {len(errors)}")
        for error in errors[:5]:  # Mostrar solo los primeros 5
            logger.warning(f"  - {error}")
    
    return migrated_nodes

def export_to_simple_dict(nodes_registry: Dict[str, Node]) -> Dict[str, Any]:
    """
    Exportar nodos a formato de diccionario simple para serialización
    
    Args:
        nodes_registry: Registro de nodos
        
    Returns:
        Diccionario simple serializable
    """
    export_data = {
        "version": "4.0",
        "exported_at": datetime.now().isoformat(),
        "total_nodes": len(nodes_registry),
        "nodes": {}
    }
    
    for node_id, node in nodes_registry.items():
        export_data["nodes"][node_id] = node.to_dict()
    
    # Agregar estadísticas
    stats = calculate_node_statistics(nodes_registry)
    export_data["statistics"] = stats
    
    return export_data

def import_from_simple_dict(import_data: Dict[str, Any]) -> Dict[str, Node]:
    """
    Importar nodos desde formato de diccionario simple
    
    Args:
        import_data: Datos a importar
        
    Returns:
        Diccionario de nodos importados
    """
    imported_nodes = {}
    
    nodes_data = import_data.get("nodes", {})
    
    for node_id, node_data in nodes_data.items():
        try:
            imported_node = Node.from_dict(node_data)
            imported_nodes[node_id] = imported_node
        except Exception as e:
            logger.error(f"Error importando nodo {node_id}: {e}")
    
    # Validar integridad
    errors = validate_tree_integrity(imported_nodes)
    if errors:
        logger.warning(f"Errores de integridad en importación: {len(errors)}")
    
    return imported_nodes

# ==================================================================================
# UTILIDADES DE TESTING Y DESARROLLO
# ==================================================================================

def create_sample_tree(size: str = "medium") -> Dict[str, Node]:
    """
    Crear árbol de muestra para testing
    
    Args:
        size: Tamaño del árbol ("small", "medium", "large")
        
    Returns:
        Diccionario con nodos de muestra
    """
    nodes = {}
    
    # Crear nodo raíz
    root = create_root_node("Proyecto de Muestra")
    nodes[root.id] = root
    
    if size == "small":
        # Estructura pequeña
        src = create_folder_node("src", root.id, "Código fuente principal")
        docs = create_folder_node("docs", root.id, "Documentación")
        main_file = create_file_node("main.py", src.id, "# Main\n\nArchivo principal", "Punto de entrada")
        
        nodes.update({src.id: src, docs.id: docs, main_file.id: main_file})
        
        # Establecer relaciones
        root.children_ids = [src.id, docs.id]
        src.children_ids = [main_file.id]
        
    elif size == "large":
        # Estructura grande para testing de performance
        for i in range(10):
            folder = create_folder_node(f"modulo_{i}", root.id)
            nodes[folder.id] = folder
            root.children_ids.append(folder.id)
            
            for j in range(5):
                subfolder = create_folder_node(f"sub_{j}", folder.id)
                nodes[subfolder.id] = subfolder
                folder.children_ids.append(subfolder.id)
                
                for k in range(3):
                    file_node = create_file_node(f"archivo_{k}.py", subfolder.id)
                    file_node.status = NodeStatus.COMPLETED if k == 0 else NodeStatus.PENDING
                    nodes[file_node.id] = file_node
                    subfolder.children_ids.append(file_node.id)
    
    else:  # medium
        # Estructura mediana realista
        folders = ["src", "tests", "docs", "config", "scripts"]
        for folder_name in folders:
            folder = create_folder_node(folder_name, root.id)
            nodes[folder.id] = folder
            root.children_ids.append(folder.id)
            
            # Añadir algunos archivos
            if folder_name == "src":
                files = ["main.py", "utils.py", "models.py"]
                for file_name in files:
                    file_node = create_file_node(file_name, folder.id)
                    file_node.add_tag(f"modulo-{file_name.split('.')[0]}")
                    nodes[file_node.id] = file_node
                    folder.children_ids.append(file_node.id)
    
    return nodes

def benchmark_operations(nodes_registry: Dict[str, Node], iterations: int = 100) -> Dict[str, float]:
    """
    Benchmark de operaciones comunes para testing de performance
    
    Args:
        nodes_registry: Registro de nodos
        iterations: Número de iteraciones
        
    Returns:
        Diccionario con tiempos de ejecución
    """
    import time
    
    results = {}
    
    # Benchmark búsqueda
    start_time = time.time()
    for _ in range(iterations):
        find_nodes_by_criteria(nodes_registry, name_pattern=".*\\.py")
    results["search_by_pattern"] = (time.time() - start_time) / iterations
    
    # Benchmark estadísticas
    start_time = time.time()
    for _ in range(iterations):
        calculate_node_statistics(nodes_registry)
    results["calculate_statistics"] = (time.time() - start_time) / iterations
    
    # Benchmark validación de integridad
    start_time = time.time()
    for _ in range(iterations):
        validate_tree_integrity(nodes_registry)
    results["validate_integrity"] = (time.time() - start_time) / iterations
    
    # Benchmark serialización
    start_time = time.time()
    for _ in range(iterations):
        export_to_simple_dict(nodes_registry)
    results["serialize_to_dict"] = (time.time() - start_time) / iterations
    
    return results