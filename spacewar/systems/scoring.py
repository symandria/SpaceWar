from spacewar.config.constants import RANKS, RANK_XP, RANK_PROMOTE


class ScoringSystem:
    def calculate_results(self, ships, dead_list, match_stats, team_game,
                          home_player, instant_action, player_character,
                          text_manager):
        non_sentries = [s for s in ships if s.type != "sentry"]
        game_over = (
            len(non_sentries) <= 1 or
            (team_game and not any(
                s.type != "sentry" and s.type != ships[0].type for s in ships))
        )
        if not game_over:
            return None, False

        winner = None
        if home_player and home_player in ships:
            winner, text_key = home_player, "after-battle-report-player"
        elif non_sentries:
            winner, text_key = non_sentries[0], "after-battle-report-other"
        else:
            text_key = "after-battle-report-draw"

        if winner:
            winning_faction = text_manager.load("faction-name-" + winner.type)
            quote = text_manager.load("victory-quote-" + winner.type)
        else:
            winning_faction = text_manager.load("no-faction")
            theme = text_manager.active_theme
            quote = text_manager.load("draw-quote-" + theme)

        text = text_manager.load(text_key).format(
            winning_faction=winning_faction, quote=quote)

        winning_team = []
        if team_game and non_sentries:
            for ship in ships + dead_list:
                if ship.type == non_sentries[0].type:
                    winning_team.append(ship)
        elif non_sentries:
            winning_team = non_sentries[:]

        for ship in ships + dead_list[::-1]:
            stats = match_stats[ship]
            vic = 0
            rank_bonus = 0
            if ship in winning_team:
                vic = 500 // len(winning_team)
                s_rank = RANKS.index(ship.rank)
                for other in match_stats:
                    if other in winning_team:
                        continue
                    o_rank = RANKS.index(other.rank)
                    if o_rank > s_rank:
                        rank_bonus += 100 * (o_rank - s_rank)
            dam = stats["damage"] * 2
            teamdam = stats["teamdamage"] * 2
            extras = ""
            if ship == home_player:
                extras = text_manager.load("extras-you")
            elif ship.human:
                extras = text_manager.load("extras-human")
            if ship not in ships:
                extras += text_manager.load("extras-dead")
            match_stats[ship]["total"] = total = dam + teamdam + vic + rank_bonus
            rank_text = text_manager.load("rank-" + ship.rank) if ship.rank else ""
            stat_key = "statistics-sentry" if ship.type == "sentry" else "statistics-ship"
            text += "\n" + text_manager.load(stat_key).format(
                name=ship.name, rank=rank_text, captain=ship.captain,
                extras=extras, dam=dam, teamdam=teamdam, vic=vic,
                rank_bonus=rank_bonus, total=total)

        if not instant_action and home_player:
            stats = match_stats[home_player]
            for stat in stats:
                if stat in ("damage", "teamdamage", "victory", "rank", "total"):
                    continue
                player_character[stat] += stats[stat]
            player_character["average points"] = (
                player_character["average points"] * player_character["games played"] +
                stats["total"]
            ) / (player_character["games played"] + 1)
            player_character["average shields"] = (
                player_character["average shields"] * player_character["games played"] +
                home_player.shields
            ) / (player_character["games played"] + 1)
            player_character["games played"] += 1
            player_character["xp"] += stats["total"]
            bonus = 0
            while player_character["rank"] in RANK_XP and \
                    player_character["xp"] > RANK_XP[player_character["rank"]]:
                bonus += 5
                player_character["rank"] = RANK_PROMOTE[player_character["rank"]]
            if bonus:
                text += "\n\n" + text_manager.load("promotion").format(
                    rank=text_manager.load("rank-" + player_character["rank"]),
                    bonus=bonus)
                player_character["bonus"] += bonus

        return text, True

    @staticmethod
    def init_player_stats(player, races, has_sentry):
        stats = {
            "damage": 0, "teamdamage": 0, "victory": 0, "rank": 0,
            "phasers shot": 0, "phasers hit": 0,
            "torpedoes shot": 0, "torpedoes hit": 0,
        }
        if has_sentry:
            stats["kills-sentry"] = 0
        for race in races:
            stats["kills-" + race] = 0
        return stats

    @staticmethod
    def init_ai_stats():
        return {"damage": 0, "teamdamage": 0, "victory": 0, "rank": 0}
