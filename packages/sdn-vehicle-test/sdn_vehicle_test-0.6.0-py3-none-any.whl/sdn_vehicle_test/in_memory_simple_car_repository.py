"""InMemorySimpleCarRepository class implementation."""

from threading import Lock
from typing import Optional, List
from .simple_car import SimpleCar


class InMemorySimpleCarRepository:
    """
    An in-memory, thread-safe repository that stores only SimpleCar instances using a string identifier.
    """

    def __init__(self):
        """
        Initializes a new instance of the InMemorySimpleCarRepository class
        and seeds it with five sample simple cars.
        """
        self._store: dict[str, SimpleCar] = {}
        self._lock = Lock()

        samples = [
            SimpleCar('Toyota', 'Corolla', 2018, '0'),
            SimpleCar('Tesla', 'Model 3', 2021, '1'),
            SimpleCar('Ford', 'Mustang', 1967, '2'),
            SimpleCar('Honda', 'Civic', 2015, '3'),
            SimpleCar('Chevrolet', 'Camaro', 2020, '4')
        ]

        for car in samples:
            self.add(car)

    def add(self, car: SimpleCar) -> None:
        """
        Adds a new simple car to the repository.

        Args:
            car: The simple car to add.

        Raises:
            ValueError: If car is None or a car with the same id already exists.
        """
        if car is None:
            raise ValueError('car cannot be None')

        with self._lock:
            if car.id in self._store:
                raise ValueError(f'SimpleCar with Id {car.id} already exists.')
            self._store[car.id] = car

    def get(self, id: str) -> Optional[SimpleCar]:
        """
        Gets a simple car by its string identifier.

        Args:
            id: The simple car identifier.

        Returns:
            The SimpleCar if found; otherwise None.

        Raises:
            ValueError: If id is None or whitespace.
        """
        if not id or id.strip() == '':
            raise ValueError('id cannot be None or whitespace')

        with self._lock:
            return self._store.get(id)

    def get_all(self) -> List[SimpleCar]:
        """
        Returns all simple cars in the repository.

        Returns:
            A list of SimpleCar.
        """
        with self._lock:
            return list(self._store.values())

    def update(self, car: SimpleCar) -> bool:
        """
        Updates an existing simple car in the repository.

        Args:
            car: The simple car with updated data.

        Returns:
            True if the car was updated; otherwise False (not found).

        Raises:
            ValueError: If car is None.
        """
        if car is None:
            raise ValueError('car cannot be None')

        with self._lock:
            if car.id not in self._store:
                return False
            self._store[car.id] = car
            return True

    def delete(self, id: str) -> bool:
        """
        Deletes a simple car by its string identifier.

        Args:
            id: The simple car identifier.

        Returns:
            True if the car was removed; otherwise False.

        Raises:
            ValueError: If id is None or whitespace.
        """
        if not id or id.strip() == '':
            raise ValueError('id cannot be None or whitespace')

        with self._lock:
            if id in self._store:
                del self._store[id]
                return True
            return False

