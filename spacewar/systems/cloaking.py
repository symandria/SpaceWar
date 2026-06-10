class CloakingSystem:
    """Cloak is an active power: the "cloak" action toggles it. Taking
    any other action drops the cloak; doing nothing maintains it."""

    def apply(self, ships, sprite_lookup):
        for ship in ships:
            if not ship.active_cloak:
                continue
            if ship.action == "cloak":
                ship.cloak(not ship.cloaked, sprite_lookup)
            elif ship.action is not None and ship.cloaked:
                ship.cloak(False, sprite_lookup)
