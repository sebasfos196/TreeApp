# application/commands/node/create_node_command.py
"""
Comando para crear nodos en TreeApp v4 Pro.
"""
from dataclasses import dataclass
from typing import Optional
from domain.node.node_entity import Node, NodeType, NodeStatus
from domain.validation import NodeValidator
from application.commands.command_bus import Command, CommandHandler, CommandResult


@dataclass
class CreateNodeCommand(Command):
    """Comando para crear un nuevo nodo."""
    name: str
    node_type: NodeType
    parent_id: Optional[str] = None
    markdown_short: str = ""
    explanation: str = ""
    code: str = ""
    status: NodeStatus = NodeStatus.NONE
    
    def execute(self) -> CommandResult:
        """Implementación requerida por Command abstracto."""
        # Este método no se usa porque usamos CommandHandler
        # Pero es requerido por la clase abstracta
        return CommandResult(success=False, error="Use CommandBus.execute() instead")


class CreateNodeCommandHandler(CommandHandler):
    """Manejador del comando CreateNode."""
    
    def __init__(self, node_repository):
        self._node_repository = node_repository
    
    def handle(self, command: CreateNodeCommand) -> CommandResult:
        """Manejar creación de nodo."""
        try:
            # Validar nombre
            NodeValidator.validate_name(command.name)
            
            # Crear nodo
            node = Node(
                name=command.name,
                node_type=command.node_type,
                parent_id=command.parent_id,
                markdown_short=command.markdown_short,
                explanation=command.explanation,
                code=command.code,
                status=command.status
            )
            
            # Validar nodo completo
            NodeValidator.validate_node(node)
            
            # Guardar en repositorio
            saved_node = self._node_repository.save(node)
            
            return CommandResult(success=True, data=saved_node)
            
        except Exception as e:
            return CommandResult(success=False, error=str(e))