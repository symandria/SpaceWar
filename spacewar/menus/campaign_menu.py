from spacewar.config.constants import RANKS, RANK_XP, STATS
from spacewar.menus.menu_actions import MenuAction
from spacewar.components.race_configs import build_race_loadout
from spacewar.components.base import ComponentSlot


class CampaignMenu(MenuAction):
    def __call__(self):
        g = self.game
        return self._make_list(
            self._text("menu-campaign-title").format(**g.player_character),
            (self._text("menu-battle-setup"), BattleSetup(g)),
            (self._text("menu-player-setup"), PlayerSetup(g)),
            ("Ship Overview", ShipOverview(g)),
            (self._text("menu-view-statistics"), ViewStatistics(g)),
            (self._text("menu-save-character"), SaveCharacter(g)),
            (self._text("menu-return-main menu"),
             (ReturnToMainMenu(g) if not g.just_saved else MainMenuDirect(g))),
        )


class MainMenuDirect(MenuAction):
    def __call__(self):
        from spacewar.menus.main_menu import MainMenu
        return MainMenu(self.game)()


class ReturnToMainMenu(MenuAction):
    def __call__(self):
        from spacewar.menus.main_menu import MainMenu
        return self._make_list(
            self._text("warning-save"),
            (self._text("menu-yes-sure"), MainMenuDirect(self.game)),
            (self._text("menu-no-sure"), CampaignMenu(self.game)),
        )


class SaveCharacter(MenuAction):
    def __call__(self):
        g = self.game
        from spacewar.ui.text_entry import TextEntry
        default_name = g.player_character.get("savefile", g.player_character["name"])

        def callback(text=None):
            if not text:
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    g.text_manager.load("character-not-saved"), g.infofont,
                    g.display.get_width(), g.settings.foreground, g.settings.background)
                g.selection_list = CampaignMenu(g)()
                g.text_entry = None
                return
            save_char = dict(**g.player_character)
            save_char["battle-settings"] = g.battle_settings
            g.character_manager.save(save_char, text)
            g.player_character["savefile"] = text
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                g.text_manager.load("character-saved"), g.infofont,
                g.display.get_width(), g.settings.foreground, g.settings.background)
            g.just_saved = True
            g.selection_list = CampaignMenu(g)()
            g.text_entry = None

        g.text_entry = TextEntry(
            g.text_manager.load("save-character-prompt"), default_name, callback,
            g.infofont, g.settings.foreground, g.settings.background)
        return g.selection_list


class PlayerSetup(MenuAction):
    def __call__(self):
        g = self.game
        pc = g.player_character
        races = g.theme_loader.active_races
        race_display = self._text(
            pc["race"] if pc["race"] in races
            else "special-option-" + pc["race"])

        bonus_text = f"Bonus Points: {pc['bonus']}"

        g.selection_list = self._make_list(
            self._text("player-setup-title").format(
                formatted_rank=self._text("rank-" + pc["rank"]), **pc),
            (self._text("player-setup-name").format(pc["name"]),
             ChangeNameAction(g, "name", "player-setup-change name")),
            (self._text("player-setup-ship").format(pc["ship"]),
             ChangeNameAction(g, "ship", "player-setup-change ship")),
            (self._text("player-setup-race").format(race_display),
             ChangeRace(g)),
            (f"Shields: {pc['shields']}", SpendPoints(g, "shields")),
            (f"Weapon Power: {pc['weapon power']}", SpendPoints(g, "weapon power")),
            (f"Engine: {pc['engine']}", SpendPoints(g, "engine")),
            (bonus_text, PlayerSetup(g)),
            (self._text("menu-back"), CampaignMenu(g)),
        )
        return g.selection_list


class ShipOverview(MenuAction):
    def __call__(self):
        g = self.game
        pc = g.player_character
        race = pc["race"]
        races = g.theme_loader.active_races
        specials_map = g.theme_loader.get_special_options()
        if race in specials_map and isinstance(specials_map[race], (list, tuple)):
            race = specials_map[race][0]

        loadout = build_race_loadout(race)
        wp = pc["weapon power"]

        lines = [f"=== {race.title()} ==="]
        lines.append(f"Shields: {pc['shields']} | Hull: {loadout.get_stat(ComponentSlot.HULL, 'strength', 50)}")
        lines.append(f"Weapon Power: {wp}")

        eng = loadout.get_component(ComponentSlot.ENGINE)
        if eng:
            lines.append(f"Engine: Spd {pc['engine']} "
                        f"Accel {eng.get('acceleration', 2)} "
                        f"Turn {eng.get('turning_degrees', 90)}deg")

        sens = loadout.get_component(ComponentSlot.SENSORS)
        if sens:
            lines.append(f"Sensors: {sens.get('vision_forward', 10)}F "
                        f"/ {sens.get('vision_backward', 5)}R")

        from spacewar.systems.weapons import WeaponType, WEAPON_STATS
        for slot_num, slot in [(1, ComponentSlot.WEAPON_1), (2, ComponentSlot.WEAPON_2)]:
            comp = loadout.get_component(slot)
            if comp:
                wtype_str = comp.get("weapon_type", "?")
                try:
                    wt = WeaponType(wtype_str)
                    stats = WEAPON_STATS[wt]
                    dmg = stats["damage_per_hit"](wp) * stats["hits"]
                    name = stats["display_name"]
                except (ValueError, KeyError):
                    name = wtype_str.replace("_", " ").title()
                    dmg = "?"
                lines.append(f"W{slot_num}: {name} dmg:{dmg} rng:{comp.get('weapon_range', 0)}")

        sh = loadout.get_component(ComponentSlot.SHIELDS)
        if sh:
            parts = [f"Regen: {sh.get('passive_regen', 5)}/turn"]
            dr = sh.get('active_dr', 0)
            if dr > 0:
                parts.append(f"DR: {dr}%")
            lines.append(" | ".join(parts))

        special = loadout.get_component(ComponentSlot.SPECIAL)
        if special and special.get("ability_type"):
            lines.append(f"Special: {special.name}")

        st = loadout.get_component(ComponentSlot.STEALTH)
        if st and st.get('active_cloak'):
            lines.append("Cloaking: Active")

        title = "\n".join(lines)
        return self._make_list(
            title,
            ("Components", ViewComponentsFromCampaign(g, race)),
            (self._text("menu-back"), CampaignMenu(g)),
        )


class ViewWeapons(MenuAction):
    def __init__(self, game, race):
        super().__init__(game)
        self.race = race

    def __call__(self):
        g = self.game
        loadout = build_race_loadout(self.race)
        wp = g.player_character["weapon power"]

        lines = [f"Weapons (WP: {wp})"]
        for slot_num, slot in [(1, ComponentSlot.WEAPON_1), (2, ComponentSlot.WEAPON_2)]:
            comp = loadout.get_component(slot)
            if comp:
                wtype = comp.get("weapon_type", "unknown")
                wrange = comp.get("weapon_range", 15)
                from spacewar.systems.weapons import WeaponType, WEAPON_STATS
                try:
                    wt = WeaponType(wtype)
                    stats = WEAPON_STATS[wt]
                    dmg = stats["damage_per_hit"](wp) * stats["hits"]
                    name = stats["display_name"]
                    lines.append(f"  Slot {slot_num}: {name}")
                    lines.append(f"    Damage: {dmg} | Range: {wrange}")
                except (ValueError, KeyError):
                    lines.append(f"  Slot {slot_num}: {wtype.title()}")

        special = loadout.get_component(ComponentSlot.SPECIAL)
        if special and special.get("ability_type"):
            atype = special.get("ability_type")
            lines.append(f"\nSpecial: {special.name}")
            if atype == "teleportation":
                lines.append(f"  Range: {special.get('teleport_range', 10)}")
                lines.append(f"  Recharge: {special.get('recharge', 3)} turns")

        title = "\n".join(lines)
        return self._make_list(title, (self._text("menu-back"), ShipOverview(g)))


class ViewComponentsFromCampaign(MenuAction):
    def __init__(self, game, race):
        super().__init__(game)
        self.race = race

    def __call__(self):
        g = self.game
        loadout = build_race_loadout(self.race)

        from spacewar.menus.component_menu import SLOT_ORDER, SLOT_LABELS
        buttons = []
        for slot in SLOT_ORDER:
            comp = loadout.get_component(slot)
            label = SLOT_LABELS.get(slot, slot.value)
            if comp:
                buttons.append((f"{label}: {comp.name}", ViewSlotFromCampaign(g, self.race, slot)))
            else:
                buttons.append((f"{label}: Empty", ViewComponentsFromCampaign(g, self.race)))

        power_text = f"Power: {loadout.total_power_cost()}/{loadout.power_budget()}"
        buttons.append((power_text, ViewComponentsFromCampaign(g, self.race)))
        buttons.append(("Back", ShipOverview(g)))
        return self._make_list("Components", *buttons)


class ViewSlotFromCampaign(MenuAction):
    def __init__(self, game, race, slot):
        super().__init__(game)
        self.race = race
        self.slot = slot

    def __call__(self):
        g = self.game
        loadout = build_race_loadout(self.race)
        comp = loadout.get_component(self.slot)
        from spacewar.menus.component_menu import SLOT_LABELS
        label = SLOT_LABELS.get(self.slot, self.slot.value)

        if not comp:
            return self._make_list(f"{label}: Empty",
                                   ("Back", ViewComponentsFromCampaign(g, self.race)))

        lines = [f"{label}: {comp.name}", f"Power Cost: {comp.power_cost}"]
        for key, value in comp.stats.items():
            display_key = key.replace("_", " ").title()
            if callable(value):
                continue
            lines.append(f"  {display_key}: {value}")

        title = "\n".join(lines)
        return self._make_list(title, ("Back", ViewComponentsFromCampaign(g, self.race)))


class ChangeNameAction(MenuAction):
    def __init__(self, game, field, prompt_tag):
        super().__init__(game)
        self.field = field
        self.prompt_tag = prompt_tag

    def __call__(self):
        g = self.game
        from spacewar.ui.text_entry import TextEntry

        def callback(text=None):
            if text:
                g.player_character[self.field] = text
                g.just_saved = False
            g.selection_list = PlayerSetup(g)()
            g.text_entry = None

        g.text_entry = TextEntry(
            self._text(self.prompt_tag), g.player_character[self.field], callback,
            g.infofont, g.settings.foreground, g.settings.background)
        return g.selection_list


class ChangeRace(MenuAction):
    def __call__(self):
        g = self.game
        races = g.theme_loader.active_races
        buttons = [(self._text(race), SetRace(g, race)) for race in races]
        specials = g.theme_loader.get_special_options()
        for key in specials:
            if key != "sentry" and isinstance(specials[key], (list, tuple)):
                buttons.append((self._text("special-option-" + key), SetRace(g, key)))
        return self._make_list(self._text("player-setup-choose race"), *buttons)


class SetRace(MenuAction):
    def __init__(self, game, race):
        super().__init__(game)
        self.race = race

    def __call__(self):
        self.game.player_character["race"] = self.race
        self.game.just_saved = False
        return PlayerSetup(self.game)()


class SpendPoints(MenuAction):
    def __init__(self, game, stat):
        super().__init__(game)
        self.stat = stat

    def __call__(self):
        g = self.game
        pc = g.player_character
        data = STATS[self.stat]
        buttons = []
        if pc["bonus"] and pc[self.stat] < data["max"]:
            buttons.append((
                self._text("stat-increase").format(data["step"], pc[self.stat] + data["step"]),
                IncreaseStat(g, self.stat),
            ))
        if pc[self.stat] > data["min"]:
            buttons.append((
                self._text("stat-decrease").format(data["step"], pc[self.stat] - data["step"]),
                DecreaseStat(g, self.stat),
            ))
        buttons.append((self._text("menu-return-player setup"), PlayerSetup(g)))

        stat_label = self.stat.title()
        return self._make_list(
            f"{stat_label}: {pc[self.stat]}  (Bonus: {pc['bonus']})",
            *buttons,
        )


class IncreaseStat(MenuAction):
    def __init__(self, game, stat):
        super().__init__(game)
        self.stat = stat

    def __call__(self):
        data = STATS[self.stat]
        self.game.player_character["bonus"] -= 1
        self.game.player_character[self.stat] += data["step"]
        self.game.just_saved = False
        return SpendPoints(self.game, self.stat)()


class DecreaseStat(MenuAction):
    def __init__(self, game, stat):
        super().__init__(game)
        self.stat = stat

    def __call__(self):
        data = STATS[self.stat]
        self.game.player_character["bonus"] += 1
        self.game.player_character[self.stat] -= data["step"]
        self.game.just_saved = False
        return SpendPoints(self.game, self.stat)()


class ViewStatistics(MenuAction):
    def __call__(self):
        g = self.game
        pc = g.player_character
        next_xp = (repr(RANK_XP[pc["rank"]] - pc["xp"])
                    if pc["rank"] in RANK_XP else self._text("n/a"))
        phaser_pct = ("0%" if pc["phasers shot"] == 0
                      else "{0:.2%}".format(pc["phasers hit"] / pc["phasers shot"]))
        torpedo_pct = ("0%" if pc["torpedoes shot"] == 0
                       else "{0:.2%}".format(pc["torpedoes hit"] / pc["torpedoes shot"]))
        text = self._text("player-statistics").format(
            next=next_xp, phaser_percent=phaser_pct,
            torpedo_percent=torpedo_pct, **pc)
        races = g.theme_loader.active_races
        text += "\n" + self._text("kill-count-prefix")
        race_list = races + (("sentry",) if g.theme_loader.has_sentry() else ())
        killstats = [
            (self._text(race) + ": ", pc["kills-" + race])
            for race in race_list
        ]
        col1 = killstats[:len(killstats) // 2]
        col2 = killstats[len(killstats) // 2:]
        if len(killstats) % 2:
            col1.insert(0, None)
            col2.insert(0, killstats[-1])
        else:
            text += "\n"
        widths = [
            len(self._text("kill-count-prefix")) - 7 if col1[0] is None else 0,
            0,
        ]
        for name in col1:
            if name is None:
                continue
            if len(name[0]) > widths[0]:
                widths[0] = len(name[0])
        for name in col2:
            if len(name[0]) > widths[1]:
                widths[1] = len(name[0])
        widths[0] += 7 - (widths[0]) % 8
        for left, right in zip(col1, col2):
            if left is not None:
                left_name, value = left
                text += left_name.rjust(widths[0]) + repr(value)
            right_name, value = right
            text += "\t" + right_name.rjust(widths[1]) + repr(value) + "\n"
        text = text[:-1]
        return self._make_list(
            text,
            (self._text("menu-stats-reset"), ResetConfirm(g)),
            (self._text("menu-back"), CampaignMenu(g)),
        )


class ResetConfirm(MenuAction):
    def __call__(self):
        return self._make_list(
            self._text("menu-stats-reset-confirm"),
            (self._text("menu-yes"), ResetStats(self.game)),
            (self._text("menu-no"), ViewStatistics(self.game)),
        )


class ResetStats(MenuAction):
    def __call__(self):
        pc = self.game.player_character
        for stat in ("games played", "phasers shot", "phasers hit",
                     "torpedoes shot", "torpedoes hit",
                     "average points", "average shields"):
            pc[stat] = 0
        for stat in [k for k in pc if k.startswith("kills-")]:
            pc[stat] = 0
        self.game.just_saved = False
        return CampaignMenu(self.game)()


class BattleSetup(MenuAction):
    def __call__(self):
        g = self.game
        races = g.theme_loader.active_races
        slots = []
        for slot_num in range(1, 4):
            data = g.battle_settings[slot_num]
            if data == "sentry":
                text = self._text("special-option-sentry")
            elif data:
                text = "{0} - {1}".format(
                    self._text("rank-" + data[0]),
                    self._text(data[1] if data[1] in races
                               else "special-option-" + data[1]))
            else:
                text = self._text("menu-empty-slot")
            slots.append((text, ChangeAISetting(g, slot_num)))

        return self._make_list(
            self._text("battle-setup-title"),
            (self._text(
                "battle-setup-team battle-on" if g.battle_settings[0]
                else "battle-setup-team battle-off"),
             ToggleTeam(g)),
            slots[0], slots[1], slots[2],
            (self._text("menu-fight"), StartBattle(g)),
            (self._text("menu-back"), CampaignMenu(g)),
        )


class ToggleTeam(MenuAction):
    def __call__(self):
        self.game.battle_settings[0] = not self.game.battle_settings[0]
        self.game.just_saved = False
        return BattleSetup(self.game)()


class ChangeAISetting(MenuAction):
    def __init__(self, game, num):
        super().__init__(game)
        self.num = num

    def __call__(self):
        g = self.game
        data = g.battle_settings[self.num]
        if data:
            if data == "sentry":
                return self._make_list(
                    self._text("menu-slot").format(self.num) +
                    self._text("special-option-sentry"),
                    (self._text("menu-remove-sentry"), RemoveAI(g, self.num)),
                    (self._text("menu-back"), BattleSetup(g)),
                )
            else:
                races = g.theme_loader.active_races
                return self._make_list(
                    self._text("menu-slot-ai").format(self.num) +
                    "{0} - {1}".format(
                        self._text("rank-" + data[0]),
                        self._text(data[1] if data[1] in races
                                   else "special-option-" + data[1])),
                    (self._text("menu-change-rank"), ChangeAIRank(g, self.num)),
                    (self._text("menu-change-race"), ChangeAIRace(g, self.num)),
                    (self._text("menu-remove-ai"), RemoveAI(g, self.num)),
                    (self._text("menu-back"), BattleSetup(g)),
                )
        else:
            buttons = [(self._text("menu-fill-slot"), AddAI(g, self.num))]
            if self.num > 1:
                buttons.append(
                    (self._text("menu-add-sentry"), AddSentry(g, self.num)))
            buttons.append((self._text("menu-back"), BattleSetup(g)))
            return self._make_list(
                self._text("menu-slot").format(self.num) +
                self._text("menu-empty-slot"),
                *buttons,
            )


class AddAI(MenuAction):
    def __init__(self, game, num):
        super().__init__(game)
        self.num = num

    def __call__(self):
        self.game.battle_settings[self.num] = (RANKS[0], "random")
        self.game.just_saved = False
        return ChangeAISetting(self.game, self.num)()


class AddSentry(MenuAction):
    def __init__(self, game, num):
        super().__init__(game)
        self.num = num

    def __call__(self):
        self.game.battle_settings[self.num] = "sentry"
        self.game.just_saved = False
        return ChangeAISetting(self.game, self.num)()


class RemoveAI(MenuAction):
    def __init__(self, game, num):
        super().__init__(game)
        self.num = num

    def __call__(self):
        self.game.battle_settings[self.num] = None
        self.game.just_saved = False
        return ChangeAISetting(self.game, self.num)()


class ChangeAIRank(MenuAction):
    def __init__(self, game, num):
        super().__init__(game)
        self.num = num

    def __call__(self):
        g = self.game
        buttons = [
            (self._text("rank-" + rank), SetAIRank(g, self.num, rank))
            for rank in RANKS
        ]
        return self._make_list(self._text("menu-choose rank"), *buttons)


class SetAIRank(MenuAction):
    def __init__(self, game, num, rank):
        super().__init__(game)
        self.num = num
        self.rank = rank

    def __call__(self):
        self.game.battle_settings[self.num] = (
            self.rank, self.game.battle_settings[self.num][1])
        self.game.just_saved = False
        return ChangeAISetting(self.game, self.num)()


class ChangeAIRace(MenuAction):
    def __init__(self, game, num):
        super().__init__(game)
        self.num = num

    def __call__(self):
        g = self.game
        races = g.theme_loader.active_races
        buttons = [(self._text(race), SetAIRace(g, self.num, race)) for race in races]
        specials = g.theme_loader.get_special_options()
        for key in specials:
            if key != "sentry" and isinstance(specials[key], (list, tuple)):
                buttons.append((
                    self._text("special-option-" + key),
                    SetAIRace(g, self.num, key),
                ))
        return self._make_list(self._text("menu-choose race"), *buttons)


class SetAIRace(MenuAction):
    def __init__(self, game, num, race):
        super().__init__(game)
        self.num = num
        self.race = race

    def __call__(self):
        self.game.battle_settings[self.num] = (
            self.game.battle_settings[self.num][0], self.race)
        self.game.just_saved = False
        return ChangeAISetting(self.game, self.num)()


class _ViewComponentsFromMenu(MenuAction):
    def __call__(self):
        from spacewar.menus.component_menu import ViewComponents
        return ViewComponents(self.game)()


class StartBattle(MenuAction):
    def __call__(self):
        g = self.game
        if not any(ai and ai != "sentry" for ai in g.battle_settings[1:]):
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                self._text("no-players"), g.infofont,
                g.display.get_width(), g.settings.foreground, g.settings.background)
            return g.selection_list
        g.start_campaign_battle()
        return None
