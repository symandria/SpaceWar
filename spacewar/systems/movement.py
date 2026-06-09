class MovementSystem:
    def update(self, ships, remaining_frames):
        for ship in ships:
            if ship.move_target:
                ship.interpolate_toward(ship.move_target, remaining_frames)
