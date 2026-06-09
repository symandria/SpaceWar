class RegenerationSystem:
    def setup_regen_flag(self, ship):
        if not ship.action and "regeneration" in ship.specials:
            ship.regen = 5

    def apply_end_of_turn(self, ships):
        for ship in ships:
            if ship.shields < 0:
                continue
            ship.move_target = None
            if not ship.action and \
                    ("regen_5" in ship.specials or "regen_15" in ship.specials):
                ship.regen = ship.regen + (ship.max_shields // 20)
            if not ship.action and \
                    ("regen_10" in ship.specials or "regen_15" in ship.specials):
                ship.regen = ship.regen + (ship.max_shields // 10)
            if "regen_5_always" in ship.specials or "regen_15_always" in ship.specials:
                ship.regen = ship.regen + (ship.max_shields // 20)
            if "regen_10_always" in ship.specials or "regen_15_always" in ship.specials:
                ship.regen = ship.regen + (ship.max_shields // 10)
            if ship.regen:
                ship.shields = min(ship.shields + ship.regen, ship.max_shields)
                ship.regen = 0
