from enum import IntEnum


class CarType(IntEnum):
    SEDAN = 1
    SUV = 2
    TRUCK = 3


CAR_TYPE_LABEL = {
    CarType.SEDAN: "Sedan",
    CarType.SUV: "SUV",
    CarType.TRUCK: "Truck",
}
