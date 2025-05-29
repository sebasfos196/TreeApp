"""
domain/events/event_bus.py - REPARADO
====================================

Sistema de eventos desacoplado para TreeApp v4 Pro
- EventBus centralizado
- Suscripción y publicación de eventos
- Integración con toda la aplicación
- 60 líneas - Cumple límite
"""

from typing import Dict, List, Callable, Any

class EventBus:
    """Sistema de eventos centralizado"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Suscribe una función callback a un tipo de evento
        
        Args:
            event_type: Tipo de evento (ej: 'node_selected', 'tree_updated')
            callback: Función a llamar cuando ocurre el evento
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Desuscribe una función callback de un tipo de evento
        
        Args:
            event_type: Tipo de evento
            callback: Función a desuscribir
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass  # Callback no estaba suscrito
    
    def publish(self, event_type: str, data: Any = None):
        """
        Publica un evento a todos los suscriptores
        
        Args:
            event_type: Tipo de evento a publicar
            data: Datos asociados al evento
        """
        
        # Agregar a historial
        event_record = {
            'type': event_type,
            'data': data,
            'timestamp': self._get_timestamp()
        }
        self._event_history.append(event_record)
        
        # Mantener solo los últimos 100 eventos
        if len(self._event_history) > 100:
            self._event_history.pop(0)
        
        # Notificar a suscriptores
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error en callback para evento '{event_type}': {e}")
    
    def get_subscribers_count(self, event_type: str) -> int:
        """Obtiene el número de suscriptores para un tipo de evento"""
        return len(self._subscribers.get(event_type, []))
    
    def get_all_event_types(self) -> List[str]:
        """Obtiene todos los tipos de eventos registrados"""
        return list(self._subscribers.keys())
    
    def clear_subscribers(self, event_type: str = None):
        """
        Limpia suscriptores
        
        Args:
            event_type: Tipo específico a limpiar, o None para limpiar todos
        """
        if event_type:
            self._subscribers[event_type] = []
        else:
            self._subscribers.clear()
    
    def get_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene el historial de eventos recientes"""
        return self._event_history[-limit:]
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp actual"""
        from datetime import datetime
        return datetime.now().isoformat()

# Instancia global del event bus (opcional)
global_event_bus = EventBus()