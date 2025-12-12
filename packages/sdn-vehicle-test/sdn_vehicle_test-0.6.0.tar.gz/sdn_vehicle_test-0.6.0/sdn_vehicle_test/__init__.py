"""Simple vehicle abstractions with a synchronous in-memory repository."""

from .simple_car import SimpleCar
from .in_memory_simple_car_repository import InMemorySimpleCarRepository

__version__ = "0.6.0"
__all__ = ["SimpleCar", "InMemorySimpleCarRepository"]

