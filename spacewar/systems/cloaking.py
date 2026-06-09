class CloakingSystem:
    def apply(self, ships, sprite_lookup):
        for ship in ships:
            if not ship.active_cloak:
                continue
            if not ship.action:
                ship.cloak(True, sprite_lookup)
            else:
                ship.cloak(False, sprite_lookup)
