from spacewar.components.base import ComponentSlot
from spacewar.menus.menu_actions import MenuAction


SLOT_ORDER = [
    ComponentSlot.ENGINE,
    ComponentSlot.SENSORS,
    ComponentSlot.SHIELDS,
    ComponentSlot.HULL,
    ComponentSlot.WEAPON_1,
    ComponentSlot.WEAPON_2,
    ComponentSlot.SPECIAL,
    ComponentSlot.STEALTH,
    ComponentSlot.POWER_SOURCE,
]

SLOT_LABELS = {
    ComponentSlot.ENGINE: "Engine",
    ComponentSlot.SENSORS: "Sensors",
    ComponentSlot.SHIELDS: "Shields",
    ComponentSlot.HULL: "Hull",
    ComponentSlot.WEAPON_1: "Weapon 1",
    ComponentSlot.WEAPON_2: "Weapon 2",
    ComponentSlot.SPECIAL: "Special",
    ComponentSlot.STEALTH: "Stealth",
    ComponentSlot.POWER_SOURCE: "Power",
}


class ViewComponents(MenuAction):
    def __call__(self):
        g = self.game
        player = g.battle.player if g.battle and g.battle.player else None
        if not player:
            return self._make_list("No Ship", ("Back", _back(g)))

        loadout = player.loadout
        buttons = []
        for slot in SLOT_ORDER:
            comp = loadout.get_component(slot)
            label = SLOT_LABELS.get(slot, slot.value)
            if comp:
                name = comp.name
                text = f"{label}: {name}"
            else:
                text = f"{label}: Empty"
            buttons.append((text, ViewSlotDetail(g, slot)))

        power_text = f"Power: {loadout.total_power_cost()}/{loadout.power_budget()}"
        buttons.append((power_text, _back(g)))
        buttons.append(("Back", _back(g)))
        return self._make_list("Ship Components", *buttons)


class ViewSlotDetail(MenuAction):
    def __init__(self, game, slot):
        super().__init__(game)
        self.slot = slot

    def __call__(self):
        g = self.game
        player = g.battle.player if g.battle and g.battle.player else None
        if not player:
            return ViewComponents(g)()

        comp = player.loadout.get_component(self.slot)
        label = SLOT_LABELS.get(self.slot, self.slot.value)
        if not comp:
            return self._make_list(f"{label}: Empty", ("Back", ViewComponents(g)))

        lines = [f"{label}: {comp.name}"]
        lines.append(f"Power Cost: {comp.power_cost}")
        for key, value in comp.stats.items():
            display_key = key.replace("_", " ").title()
            lines.append(f"  {display_key}: {value}")

        title = "\n".join(lines)
        return self._make_list(title, ("Back", ViewComponents(g)))


def _back(game):
    class BackAction(MenuAction):
        def __call__(self):
            return None
    return BackAction(game)
