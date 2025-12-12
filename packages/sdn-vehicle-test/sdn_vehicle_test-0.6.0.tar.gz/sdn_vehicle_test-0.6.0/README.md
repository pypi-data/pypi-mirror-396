# sdn-vehicle-test

Simple vehicle abstractions with a synchronous in-memory repository.

## Install
```bash
pip install sdn-vehicle-test
```

## Usage
```python
from sdn_vehicle_test import SimpleCar, InMemorySimpleCarRepository

repo = InMemorySimpleCarRepository()
car = SimpleCar('BMW', 'M3', 2023)
repo.add(car)

all_cars = repo.get_all()
print(f"Total cars: {len(all_cars)}")
```

