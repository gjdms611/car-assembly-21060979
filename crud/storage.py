import json
import os

DEFAULT_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "cars.json")


def load_cars(path=DEFAULT_DATA_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cars(cars, path=DEFAULT_DATA_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
