class RegenerationSystem:
    def setup_regen_flag(self, ship):
        if ship.passive_regen > 0:
            ship.regen = ship.passive_regen

    def apply_end_of_turn(self, ships):
        for ship in ships:
            if ship.is_dead():
                continue
            ship.move_target = None
            if ship.regen:
                ship.shields = min(ship.shields + ship.regen, ship.max_shields)
                ship.regen = 0
