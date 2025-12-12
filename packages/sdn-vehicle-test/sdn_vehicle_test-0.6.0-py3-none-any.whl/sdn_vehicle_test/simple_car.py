"""SimpleCar class implementation."""

import uuid
from typing import Optional


class SimpleCar:
    """
    Represents a simplified car that uses a string identifier instead of a GUID.
    """

    def __init__(
        self,
        make: str,
        model: str,
        year: int,
        id: Optional[str] = None
    ):
        """
        Initializes a new instance of the SimpleCar class.

        Args:
            make: The make of the car.
            model: The model of the car.
            year: The year the car was made.
            id: The string identifier for the car. If None or empty, a new UUID string is generated.
        """
        self._id = str(uuid.uuid4()) if not id or id.strip() == '' else id
        self._make = make
        self._model = model
        self._year = year
        self._is_running = False

    @property
    def id(self) -> str:
        """Gets the string identifier for the car."""
        return self._id

    @property
    def make(self) -> str:
        """Gets the make of the car."""
        return self._make

    @property
    def model(self) -> str:
        """Gets the model of the car."""
        return self._model

    @property
    def year(self) -> int:
        """Gets the year the car was made."""
        return self._year

    @property
    def wheels(self) -> int:
        """Gets the number of wheels on the car."""
        return 4

    @property
    def is_running(self) -> bool:
        """Gets a value indicating whether the car is currently running (started)."""
        return self._is_running

    def start(self) -> None:
        """Starts the car."""
        self._is_running = True

    def stop(self) -> None:
        """Stops the car."""
        self._is_running = False

    def __str__(self) -> str:
        """
        Returns a string that represents the current car.

        Returns:
            A string containing the year, make, model and type ("SimpleCar").
        """
        return f"{self._year} {self._make} {self._model} (SimpleCar)"

