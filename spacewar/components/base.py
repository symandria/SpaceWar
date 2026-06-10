from enum import Enum


class ComponentSlot(Enum):
    ENGINE = "engine"
    SENSORS = "sensors"
    SHIELDS = "shields"
    HULL = "hull"
    WEAPON_1 = "weapon_1"
    WEAPON_2 = "weapon_2"
    SPECIAL = "special"
    SPECIAL_2 = "special_2"
    TRACTOR = "tractor"
    POWER_SOURCE = "power_source"
    STEALTH = "stealth"


class Component:
    def __init__(self, slot, name, power_cost, **stats):
        self.slot = slot
        self.name = name
        self.power_cost = power_cost
        self.stats = stats

    def get(self, stat_name, default=None):
        return self.stats.get(stat_name, default)

    def __repr__(self):
        return f"Component({self.slot.value}, {self.name!r})"
