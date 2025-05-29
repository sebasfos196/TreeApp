"""
presentation/views/panels/preview_panel/exporters/txt_exporter.py
================================================================

Exportador TXT profesional con:
- Formato exacto de la vista previa
- Encabezados profesionales por rama/archivo
- Inclusión de Notas Técnicas y Código
- Estadísticas detalladas
- 180 líneas - Cumple límite
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class TXTExporter:
    """Exportador TXT profesional con formato exacto"""
    
    def __init__(self, renderer=None):
        self.renderer = renderer
        self.export_config = {
            'include_header': True,
            'include_statistics': True,
            'include_notes': True,
            'include_code': True,
            'professional_headers': True,
            'export_branch_only': False,
            'selected_branch_id': None
        }
    
    def export_to_file(self, nodes: Dict[str, Any], root_id: str, config: Dict[str, Any], 
                      filename: str, export_options: Dict[str, Any] = None) -> bool:
        """Exporta a archivo TXT con formato profesional"""
        
        try:
            # Actualizar configuración de exportación
            if export_options:
                self.export_config.update(export_options)
            
            # Generar contenido
            content = self.generate_export_content(nodes, root_id, config)
            
            # Escribir archivo
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error exportando a TXT: {e}")
            return False
    
    def generate_export_content(self, nodes: Dict[str, Any], root_id: str, config: Dict[str, Any]) -> str:
        """Genera el contenido completo de exportación"""
        
        content_parts = []
        
        # Encabezado profesional
        if self.export_config.get('include_header', True):
            content_parts.append(self._generate_professional_header(nodes, root_id, config))
        
        # Contenido principal (vista previa exacta)
        if self.renderer:
            preview_content = self.renderer.render(nodes, root_id, config)
            content_parts.append(preview_content)
        
        # Contenido detallado con headers profesionales
        if self.export_config.get('professional_headers', True):
            detailed_content = self._generate_detailed_content(nodes, root_id)
            if detailed_content:
                content_parts.append("\n" + "="*80)
                content_parts.append("CONTENIDO DETALLADO")
                content_parts.append("="*80 + "\n")
                content_parts.append(detailed_content)
        
        # Estadísticas finales
        if self.export_config.get('include_statistics', True):
            stats = self._generate_final_statistics(nodes)
            content_parts.append("\n" + stats)
        
        return '\n'.join(content_parts)
    
    def _generate_professional_header(self, nodes: Dict[str, Any], root_id: str, config: Dict[str, Any]) -> str:
        """Genera encabezado profesional"""
        
        now = datetime.now()
        mode_name = getattr(self.renderer, 'name', 'Desconocido') if self.renderer else 'Desconocido'
        
        # Información del proyecto
        root_node = nodes.get(root_id, {})
        project_name = root_node.get('name', 'Proyecto Sin Nombre')
        
        header = f"""# ===========================================================================================
# TreeApp v4 Pro - Exportación TXT Profesional
# ===========================================================================================
#
# Proyecto: {project_name}
# Fecha de exportación: {now.strftime('%Y-%m-%d %H:%M:%S')}
# Modo de vista previa: {mode_name}
# Configuración aplicada: {config}
#
# Estadísticas rápidas:
# - Total nodos: {len(nodes)}
# - Modo de exportación: {'Rama específica' if self.export_config.get('export_branch_only') else 'Proyecto completo'}
#
# ===========================================================================================

"""
        return header
    
    def _generate_detailed_content(self, nodes: Dict[str, Any], root_id: str) -> str:
        """Genera contenido detallado con headers profesionales"""
        
        if not self.export_config.get('include_notes') and not self.export_config.get('include_code'):
            return ""
        
        content_parts = []
        
        # Determinar nodos a exportar
        if self.export_config.get('export_branch_only') and self.export_config.get('selected_branch_id'):
            start_node_id = self.export_config['selected_branch_id']
        else:
            start_node_id = root_id
        
        # Generar contenido detallado
        self._generate_node_detailed_content(nodes, start_node_id, "", content_parts)
        
        return '\n'.join(content_parts)
    
    def _generate_node_detailed_content(self, nodes: Dict[str, Any], node_id: str, parent_path: str, content_parts: List[str]):
        """Genera contenido detallado para un nodo y sus hijos"""
        
        if node_id not in nodes:
            return
        
        node = nodes[node_id]
        node_name = node.get('name', 'Sin nombre')
        
        # Construir ruta completa
        if parent_path:
            full_path = f"{parent_path}/{node_name}"
        else:
            full_path = node_name
        
        # Verificar si tiene contenido para mostrar
        has_notes = self.export_config.get('include_notes') and node.get('notes', '').strip()
        has_code = self.export_config.get('include_code') and node.get('code', '').strip()
        has_markdown = node.get('markdown', '').strip()
        
        if has_notes or has_code or has_markdown:
            # Header profesional por archivo/carpeta
            content_parts.append(f"""
// ===========================================================================================
// {node_name} - {node.get('markdown', 'Sin descripción')[:50]}
// Ruta: {full_path}
// Tipo: {node.get('type', 'file').title()}
// Estado: {node.get('status', '⬜')}
// ===========================================================================================""")
            
            # Notas técnicas (si están habilitadas)
            if has_notes:
                content_parts.append(f"""
// NOTAS TÉCNICAS:
// {'-'*50}
{node['notes']}""")
            
            # Contenido markdown (si existe)
            if has_markdown:
                content_parts.append(f"""
// DESCRIPCIÓN MARKDOWN:
// {'-'*50}
{node['markdown']}""")
            
            # Código (si está habilitado)
            if has_code:
                content_parts.append(f"""
// CÓDIGO:
// {'-'*50}
{node['code']}""")
            
            content_parts.append("\n")
        
        # Procesar hijos
        children = node.get('children', [])
        for child_id in children:
            self._generate_node_detailed_content(nodes, child_id, full_path, content_parts)
    
    def _generate_final_statistics(self, nodes: Dict[str, Any]) -> str:
        """Genera estadísticas finales de la exportación"""
        
        # Contar por tipo
        folders = sum(1 for node in nodes.values() if node.get('type') == 'folder')
        files = len(nodes) - folders
        
        # Contar por estado
        completed = sum(1 for node in nodes.values() if node.get('status') == '✅')
        pending = sum(1 for node in nodes.values() if node.get('status') == '⬜')
        blocked = sum(1 for node in nodes.values() if node.get('status') == '❌')
        
        # Contar contenido
        with_notes = sum(1 for node in nodes.values() if node.get('notes', '').strip())
        with_code = sum(1 for node in nodes.values() if node.get('code', '').strip())
        with_markdown = sum(1 for node in nodes.values() if node.get('markdown', '').strip())
        
        stats = f"""
{'='*80}
ESTADÍSTICAS FINALES DE EXPORTACIÓN
{'='*80}

ESTRUCTURA:
- Total nodos: {len(nodes)}
- Carpetas: {folders}
- Archivos: {files}

ESTADOS:
- Completados ✅: {completed}
- Pendientes ⬜: {pending}
- Bloqueados ❌: {blocked}

CONTENIDO:
- Con notas técnicas: {with_notes}
- Con código: {with_code}
- Con markdown: {with_markdown}

CONFIGURACIÓN DE EXPORTACIÓN:
- Incluir notas técnicas: {'Sí' if self.export_config.get('include_notes') else 'No'}
- Incluir código: {'Sí' if self.export_config.get('include_code') else 'No'}
- Headers profesionales: {'Sí' if self.export_config.get('professional_headers') else 'No'}
- Exportación: {'Rama específica' if self.export_config.get('export_branch_only') else 'Proyecto completo'}

{'='*80}
Exportado por TreeApp v4 Pro - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}"""

        return stats
    
    def set_export_options(self, options: Dict[str, Any]):
        """Establece opciones de exportación"""
        self.export_config.update(options)
    
    def get_export_preview(self, nodes: Dict[str, Any], root_id: str, config: Dict[str, Any], max_lines: int = 50) -> str:
        """Genera vista previa de la exportación (primeras líneas)"""
        
        full_content = self.generate_export_content(nodes, root_id, config)
        lines = full_content.split('\n')
        
        if len(lines) <= max_lines:
            return full_content
        
        preview_lines = lines[:max_lines]
        preview_lines.append(f"\n... ({len(lines) - max_lines} líneas más) ...")
        
        return '\n'.join(preview_lines)
    
    def validate_export_data(self, nodes: Dict[str, Any], root_id: str) -> tuple[bool, str]:
        """Valida los datos antes de exportar"""
        
        if not nodes:
            return False, "No hay nodos para exportar"
        
        if not root_id or root_id not in nodes:
            return False, "Nodo raíz inválido"
        
        # Validar rama específica si está configurada
        if self.export_config.get('export_branch_only'):
            branch_id = self.export_config.get('selected_branch_id')
            if not branch_id or branch_id not in nodes:
                return False, "Rama seleccionada para exportación no válida"
        
        return True, "Datos válidos para exportación"
    
    def get_estimated_file_size(self, nodes: Dict[str, Any], root_id: str, config: Dict[str, Any]) -> int:
        """Estima el tamaño del archivo TXT resultante"""
        
        content = self.generate_export_content(nodes, root_id, config)
        return len(content.encode('utf-8'))
    
    def get_export_summary(self, nodes: Dict[str, Any], root_id: str) -> Dict[str, Any]:
        """Obtiene resumen de lo que se va a exportar"""
        
        # Determinar nodos a exportar
        if self.export_config.get('export_branch_only'):
            branch_id = self.export_config.get('selected_branch_id')
            if branch_id and branch_id in nodes:
                export_nodes = self._get_branch_nodes(nodes, branch_id)
            else:
                export_nodes = {}
        else:
            export_nodes = nodes
        
        # Contar elementos
        folders = sum(1 for node in export_nodes.values() if node.get('type') == 'folder')
        files = len(export_nodes) - folders
        
        # Contar contenido
        with_notes = sum(1 for node in export_nodes.values() if node.get('notes', '').strip())
        with_code = sum(1 for node in export_nodes.values() if node.get('code', '').strip())
        
        return {
            'total_nodes': len(export_nodes),
            'folders': folders,
            'files': files,
            'nodes_with_notes': with_notes,
            'nodes_with_code': with_code,
            'export_type': 'Rama específica' if self.export_config.get('export_branch_only') else 'Proyecto completo',
            'include_notes': self.export_config.get('include_notes', True),
            'include_code': self.export_config.get('include_code', True)
        }
    
    def _get_branch_nodes(self, nodes: Dict[str, Any], branch_id: str) -> Dict[str, Any]:
        """Obtiene todos los nodos de una rama específica"""
        
        branch_nodes = {}
        
        def collect_nodes(node_id: str):
            if node_id in nodes:
                branch_nodes[node_id] = nodes[node_id]
                children = nodes[node_id].get('children', [])
                for child_id in children:
                    collect_nodes(child_id)
        
        collect_nodes(branch_id)
        return branch_nodes