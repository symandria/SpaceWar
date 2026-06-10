from spacewar.roguelike.inventory import Inventory
from spacewar.roguelike.sector_map import SectorMap
from spacewar.roguelike.encounters import (
    generate_battle_config, generate_shop_inventory, generate_event,
    NodeType, ENVIRONMENTS,
)
from spacewar.roguelike.loot import generate_battle_loot, generate_salvage_loot, apply_loot
from spacewar.components.race_configs import build_race_loadout
from spacewar.components.base import ComponentSlot


class Run:
    def __init__(self, race, weapon_power=10):
        self.race = race
        self.weapon_power = weapon_power
        self.loadout = build_race_loadout(race)
        self.inventory = Inventory()
        self.sector_map = SectorMap()
        self.current_tier = 1
        self.max_tier = 3
        self.hull = self.loadout.get_stat(ComponentSlot.HULL, "strength", 50)
        self.max_hull = self.hull
        self.shields = self.loadout.get_stat(ComponentSlot.SHIELDS, "strength", 100)
        self.max_shields = self.shields
        self.battles_won = 0
        self.total_kills = 0
        self.alive = True
        self.victory = False

        self.sector_map.generate(self.current_tier)

    def advance_tier(self):
        if self.current_tier < self.max_tier:
            self.current_tier += 1
            self.sector_map.generate(self.current_tier)
            return True
        else:
            self.victory = True
            return False

    def apply_battle_results(self, player_won, enemies_killed, player_hull, player_shields):
        # Matches Ship.is_dead(): hull 0 is still alive, below 0 is destroyed.
        self.hull = max(player_hull, 0)
        if player_hull < 0:
            self.shields = 0
            self.alive = False
            return None
        # Shields recharge between nodes; hull damage persists.
        self.shields = self.max_shields

        self.battles_won += 1 if player_won else 0
        self.total_kills += enemies_killed

        loot = generate_battle_loot(self.current_tier, enemies_killed, player_won)
        apply_loot(loot, self.inventory)
        return loot

    def rest(self):
        heal_hull = self.max_hull // 4
        heal_shields = self.max_shields // 2
        old_hull = self.hull
        old_shields = self.shields
        self.hull = min(self.hull + heal_hull, self.max_hull)
        self.shields = min(self.shields + heal_shields, self.max_shields)
        return self.hull - old_hull, self.shields - old_shields

    def apply_repair(self):
        self.hull = self.max_hull
        self.shields = self.max_shields

    def heal_partial(self, hull_amount, shield_amount):
        self.hull = min(self.hull + hull_amount, self.max_hull)
        self.shields = min(self.shields + shield_amount, self.max_shields)

    def take_hull_damage(self, amount):
        self.hull -= amount
        if self.hull < 0:
            self.hull = 0
            self.alive = False

    def equip_component(self, component):
        if not self.loadout.can_equip(component):
            return False
        old = self.loadout.get_component(component.slot)
        if old:
            self.inventory.add_component(old)
        self.loadout.equip(component)
        self.inventory.remove_component(component)
        self._refresh_max_stats()
        return True

    def _refresh_max_stats(self):
        self.max_hull = self.loadout.get_stat(ComponentSlot.HULL, "strength", 50)
        self.max_shields = self.loadout.get_stat(ComponentSlot.SHIELDS, "strength", 100)
        self.hull = min(self.hull, self.max_hull)
        self.shields = min(self.shields, self.max_shields)

    def get_status_text(self):
        tier_names = {1: "Frontier", 2: "Warzone", 3: "Core"}
        tier_name = tier_names.get(self.current_tier, f"Tier {self.current_tier}")
        hull_bar = self._bar(self.hull, self.max_hull, 10)
        shield_bar = self._bar(self.shields, self.max_shields, 10)
        lines = [
            f"--- {tier_name} (Tier {self.current_tier}/{self.max_tier}) ---",
            f"Hull:    [{hull_bar}] {self.hull}/{self.max_hull}",
            f"Shields: [{shield_bar}] {self.shields}/{self.max_shields}",
            f"Scrap: {self.inventory.scrap}",
        ]
        mats = self.inventory.materials
        mat_parts = [f"{v} {k}" for k, v in mats.items() if v > 0]
        if mat_parts:
            lines.append(" | ".join(mat_parts))
        return "\n".join(lines)

    def _bar(self, current, maximum, width):
        if maximum <= 0:
            return "." * width
        filled = int(width * max(0, current) / maximum)
        return "#" * filled + "." * (width - filled)
