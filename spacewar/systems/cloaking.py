class CloakingSystem:
    def apply(self, ships, sprite_lookup):
        for ship in ships:
            if (not ship.action and "cloaking" in ship.specials) or \
                    "cloaking_always" in ship.specials:
                ship.cloak(True, sprite_lookup)
            elif ship.action and "cloaking" in ship.specials:
                ship.cloak(False, sprite_lookup)
