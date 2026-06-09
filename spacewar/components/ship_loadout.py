from spacewar.components.base import ComponentSlot


class ShipLoadout:
    def __init__(self):
        self.components = {}

    def equip(self, component):
        self.components[component.slot] = component

    def get_component(self, slot):
        return self.components.get(slot)

    def get_stat(self, slot, stat_name, default=None):
        comp = self.components.get(slot)
        if comp is None:
            return default
        return comp.get(stat_name, default)

    def total_power_cost(self):
        return sum(c.power_cost for c in self.components.values()
                   if c.slot != ComponentSlot.POWER_SOURCE)

    def power_budget(self):
        ps = self.components.get(ComponentSlot.POWER_SOURCE)
        if ps is None:
            return 0
        return ps.get("power_provided", 0)

    def is_valid(self):
        return self.total_power_cost() <= self.power_budget()

    def can_equip(self, component):
        current = self.components.get(component.slot)
        old_cost = current.power_cost if current else 0
        new_total = self.total_power_cost() - old_cost + component.power_cost
        budget = self.power_budget()
        if component.slot == ComponentSlot.POWER_SOURCE:
            budget = component.get("power_provided", 0)
            new_total = self.total_power_cost()
        return new_total <= budget

    def get_weapon(self, slot_num):
        slot = ComponentSlot.WEAPON_1 if slot_num == 1 else ComponentSlot.WEAPON_2
        return self.components.get(slot)

    def has_special(self, ability_type):
        special = self.components.get(ComponentSlot.SPECIAL)
        if special is None:
            return False
        return special.get("ability_type") == ability_type

    def __iter__(self):
        return iter(self.components.values())
