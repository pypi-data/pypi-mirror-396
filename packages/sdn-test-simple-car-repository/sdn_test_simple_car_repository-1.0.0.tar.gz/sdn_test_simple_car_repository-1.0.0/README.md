# sdn-test-simple-car-repository

Simple vehicle in memory repository.

## Install
```bash
pip install sdn-test-simple-car-repository
```

## Usage
```python
from sdn_test_simple_car_repository import InMemorySimpleCarRepository
from sdn_test_simple_car import SimpleCar

repo = InMemorySimpleCarRepository()
car = SimpleCar('BMW', 'M3', 2023)
repo.add(car)

all_cars = repo.get_all()
print(f"Total cars: {len(all_cars)}")
```

