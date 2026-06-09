from spacewar.components.base import ComponentSlot


class ComponentRegistry:
    def __init__(self):
        self._components = {slot: [] for slot in ComponentSlot}

    def register(self, component):
        self._components[component.slot].append(component)

    def get_available(self, slot):
        return list(self._components[slot])

    def get_by_name(self, slot, name):
        for comp in self._components[slot]:
            if comp.name == name:
                return comp
        return None
