from dataclasses import dataclass


@dataclass
class Waypoint:
    X: int
    Y: int
    Z: int
    yaw: int
    tolerance: int
