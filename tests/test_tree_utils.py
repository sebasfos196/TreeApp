# tests/test_tree_utils.py
"""
Tests unitarios para tree_utils - funciones puras.
"""
import unittest
from presentation.views.panels.tree_panel.tree_utils import NodeValidator, FlatIcons, FileTemplateGenerator


class TestNodeValidator(unittest.TestCase):
    """Tests para validación de nombres de nodos."""
    
    def test_valid_names(self):
        """Probar nombres válidos."""
        valid_names = ["archivo.txt", "carpeta", "mi_proyecto", "test123"]
        
        for name in valid_names:
            is_valid, error_msg = NodeValidator.validate_name(name)
            self.assertTrue(is_valid, f"'{name}' debería ser válido: {error_msg}")
    
    def test_invalid_names(self):
        """Probar nombres inválidos."""
        invalid_names = ["", "   ", "archivo<test", "CON", "a" * 256]
        
        for name in invalid_names:
            is_valid, error_msg = NodeValidator.validate_name(name)
            self.assertFalse(is_valid, f"'{name}' debería ser inválido")
            self.assertIsInstance(error_msg, str)
            self.assertTrue(len(error_msg) > 0)
    
    def test_forbidden_characters(self):
        """Probar caracteres prohibidos."""
        forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        
        for char in forbidden_chars:
            name = f"archivo{char}test"
            is_valid, error_msg = NodeValidator.validate_name(name)
            self.assertFalse(is_valid, f"Nombre con '{char}' debería ser inválido")


class TestFlatIcons(unittest.TestCase):
    """Tests para iconos por extensión."""
    
    def test_known_extensions(self):
        """Probar extensiones conocidas."""
        test_cases = [
            ("archivo.py", "🐍"),
            ("script.js", "📜"),
            ("documento.md", "📝"),
            ("config.json", "⚙️"),
            ("imagen.png", "🖼️")
        ]
        
        for filename, expected_icon in test_cases:
            icon = FlatIcons.get_file_icon(filename)
            self.assertEqual(icon, expected_icon, f"Icono para {filename} incorrecto")
    
    def test_unknown_extension(self):
        """Probar extensión desconocida."""
        icon = FlatIcons.get_file_icon("archivo.xyz")
        self.assertEqual(icon, FlatIcons.FILE)
    
    def test_no_extension(self):
        """Probar archivo sin extensión."""
        icon = FlatIcons.get_file_icon("archivo")
        self.assertEqual(icon, FlatIcons.FILE)


class TestFileTemplateGenerator(unittest.TestCase):
    """Tests para generador de plantillas."""
    
    def test_python_template(self):
        """Probar plantilla Python."""
        template = FileTemplateGenerator.generate_template("test.py")
        
        self.assertIn("#!/usr/bin/env python3", template)
        self.assertIn("def main():", template)
        self.assertIn("if __name__ == \"__main__\":", template)
    
    def test_javascript_template(self):
        """Probar plantilla JavaScript."""
        template = FileTemplateGenerator.generate_template("test.js")
        
        self.assertIn("console.log", template)
        self.assertIn("function main()", template)
    
    def test_unknown_extension_template(self):
        """Probar plantilla para extensión desconocida."""
        template = FileTemplateGenerator.generate_template("test.xyz")
        
        self.assertIn("# Contenido de test.xyz", template)
        self.assertIn("TreeCreator", template)


# tests/test_renderers.py
"""
Tests unitarios para renderers de vista previa.
"""
import unittest
from unittest.mock import Mock, MagicMock
from domain.node.node_entity import Node, NodeType, NodeStatus
from presentation.views.panels.preview_panel.renderers.classic_renderer import ClassicRenderer


class TestClassicRenderer(unittest.TestCase):
    """Tests para ClassicRenderer."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.mock_repository = Mock()
        self.renderer = ClassicRenderer(self.mock_repository)
        
        # Crear nodos de prueba
        self.root_node = Node("Root", NodeType.FOLDER)
        self.root_node.node_id = "root_1"
        self.root_node.status = NodeStatus.IN_PROGRESS
        self.root_node.markdown_short = "# Proyecto Raíz"
        
        self.child_node = Node("archivo.py", NodeType.FILE)
        self.child_node.node_id = "file_1"
        self.child_node.status = NodeStatus.COMPLETED
        self.child_node.markdown_short = "# Script principal"
    
    def test_render_empty_project(self):
        """Probar renderizado de proyecto vacío."""
        result = self.renderer.render([], {})
        self.assertEqual(result, "📂 Sin contenido")
    
    def test_render_single_root(self):
        """Probar renderizado con un solo nodo raíz."""
        self.mock_repository.find_children.return_value = []
        
        config = {
            'indent_spaces': 4,
            'show_icons': True,
            'show_status': True,
            'show_markdown': True,
            'markdown_max_length': 50,
            'max_depth': 10
        }
        
        result = self.renderer.render([self.root_node], config)
        
        self.assertIn("📁 Root", result)
        self.assertIn("⬜", result)  # Estado IN_PROGRESS
        self.assertIn("# Proyecto Raíz", result)
    
    def test_render_with_children(self):
        """Probar renderizado con nodos hijos."""
        self.mock_repository.find_children.side_effect = lambda node_id: [self.child_node] if node_id == "root_1" else []
        
        config = {
            'indent_spaces': 2,
            'show_icons': True,
            'show_status': True,
            'show_markdown': True,
            'markdown_max_length': 20,
            'max_depth': 10
        }
        
        result = self.renderer.render([self.root_node], config)
        lines = result.split('\n')
        
        # Verificar que hay al menos 2 líneas (padre e hijo)
        self.assertGreaterEqual(len(lines), 2)
        
        # Verificar indentación del hijo
        child_line = lines[1]
        self.assertTrue(child_line.startswith('  '))  # 2 espacios de indentación


if __name__ == '__main__':
    # Ejecutar tests
    unittest.main()
    
    # Para ejecutar tests específicos:
    # python -m pytest tests/test_tree_utils.py::TestNodeValidator::test_valid_names -v