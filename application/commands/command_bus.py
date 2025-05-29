# application/commands/command_bus.py
"""
Bus de comandos para TreeApp v4 Pro.
Maneja la ejecución de comandos de forma centralizada.
"""
from typing import Dict, Type, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Resultado de ejecución de un comando."""
    success: bool
    data: Any = None
    error: str = None


class Command(ABC):
    """Comando base abstracto."""
    
    @abstractmethod
    def execute(self) -> CommandResult:
        """Ejecutar el comando."""
        pass


class CommandHandler(ABC):
    """Manejador de comando base."""
    
    @abstractmethod
    def handle(self, command: Command) -> CommandResult:
        """Manejar un comando específico."""
        pass


class CommandBus:
    """Bus centralizado de comandos."""
    
    def __init__(self):
        self._handlers: Dict[Type[Command], CommandHandler] = {}
    
    def register_handler(self, command_type: Type[Command], handler: CommandHandler) -> None:
        """Registrar manejador para un tipo de comando."""
        self._handlers[command_type] = handler
    
    def execute(self, command: Command) -> CommandResult:
        """Ejecutar un comando."""
        command_type = type(command)
        
        if command_type not in self._handlers:
            return CommandResult(
                success=False,
                error=f"No hay manejador registrado para {command_type.__name__}"
            )
        
        try:
            # Ejecutar comando
            result = self._handlers[command_type].handle(command)
            return result
            
        except Exception as e:
            return CommandResult(success=False, error=str(e))


# Instancia global del command bus
_command_bus = CommandBus()


def get_command_bus() -> CommandBus:
    """Obtener la instancia global del command bus."""
    return _command_bus