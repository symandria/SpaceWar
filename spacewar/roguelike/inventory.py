class Inventory:
    def __init__(self):
        self.scrap = 0
        self.components = []
        self.materials = {"common": 0, "uncommon": 0, "rare": 0}

    def add_scrap(self, amount):
        self.scrap += amount

    def spend_scrap(self, amount):
        if self.scrap >= amount:
            self.scrap -= amount
            return True
        return False

    def add_material(self, tier, amount=1):
        if tier in self.materials:
            self.materials[tier] += amount

    def has_materials(self, tier, amount=1):
        return self.materials.get(tier, 0) >= amount

    def spend_material(self, tier, amount=1):
        if self.has_materials(tier, amount):
            self.materials[tier] -= amount
            return True
        return False

    def add_component(self, component):
        self.components.append(component)

    def remove_component(self, component):
        if component in self.components:
            self.components.remove(component)
            return True
        return False

    def get_components_for_slot(self, slot):
        return [c for c in self.components if c.slot == slot]

    def to_dict(self):
        return {
            "scrap": self.scrap,
            "materials": dict(self.materials),
            "components": [
                {"slot": c.slot.value, "name": c.name, "power_cost": c.power_cost,
                 "stats": {k: v for k, v in c.stats.items() if not callable(v)}}
                for c in self.components
            ],
        }

    @classmethod
    def from_dict(cls, data):
        inv = cls()
        inv.scrap = data.get("scrap", 0)
        inv.materials = data.get("materials", {"common": 0, "uncommon": 0, "rare": 0})
        return inv
