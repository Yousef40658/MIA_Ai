# built using Claude 
# i also made it fix buggy lines in script.py but i've written the structure and plan myself
"""
Simulates one full match minute-by-minute so you can see the engine in action.
Requires football_engine.py (with the three patches above) in the same folder.
"""
import random

from script import (
    Position, Phase, Actions, Player, Team, Match, MatchAi
)


def build_squad(country, formation, subs=3):
    lineup = [
        Player("GK-" + country, Position.GOALKEEPER, base_attack=20, base_def=85, stamina=100),
        Player("DF1-" + country, Position.DEFENDER, base_attack=30, base_def=75, stamina=100),
        Player("DF2-" + country, Position.DEFENDER, base_attack=30, base_def=78, stamina=100),
        Player("DF3-" + country, Position.DEFENDER, base_attack=25, base_def=80, stamina=100),
        Player("MF1-" + country, Position.MIDFIELDER, base_attack=70, base_def=55, stamina=100),
        Player("MF2-" + country, Position.MIDFIELDER, base_attack=68, base_def=60, stamina=100),
        Player("MF3-" + country, Position.MIDFIELDER, base_attack=72, base_def=50, stamina=100),
        Player("FW1-" + country, Position.FORWARD, base_attack=85, base_def=25, stamina=100),
        Player("FW2-" + country, Position.FORWARD, base_attack=82, base_def=20, stamina=100),
        Player("DF4-" + country, Position.DEFENDER, base_attack=28, base_def=76, stamina=100),
        Player("MF4-" + country, Position.MIDFIELDER, base_attack=65, base_def=58, stamina=100),
    ]
    bench = [
        Player("SUB-GK-" + country, Position.GOALKEEPER, base_attack=18, base_def=80, stamina=100),
        Player("SUB-DF-" + country, Position.DEFENDER, base_attack=27, base_def=79, stamina=100),
        Player("SUB-MF-" + country, Position.MIDFIELDER, base_attack=74, base_def=52, stamina=100),
        Player("SUB-FW-" + country, Position.FORWARD, base_attack=88, base_def=18, stamina=100),
    ]
    # split off 5 of these into the bench so active_lineup has 6 to start (matches the fixture in tests);
    # feel free to adjust for a "real" 11 vs 4 bench setup:
    active = lineup[:6]
    extra_bench = lineup[6:]
    return Team(
        country_name=country,
        roster=lineup + bench,
        active_lineup=active,
        bench=extra_bench + bench,
        substitution_remaining=subs,
        formation=formation,
        automatic_sub=True,
    )


class DummyModel:
    """Stand-in for an LLM: picks a weighted-random action so match.py runs
    without needing an actual model wired up. Swap this for a real model object
    if you have one (must expose .generate_content(prompt).text)."""

    def generate_content(self, prompt):
        choice = random.choices(
            ["SUBSTITUTE", "CHANGE_FORMATION", "HOLD", "ATTACK"],
            weights=[0.15, 0.1, 0.35, 0.4],
        )[0]
        return type("Resp", (), {"text": choice})()


def print_lineup(team):
    print(f"\n{team.country_name} ({team.formation}) starting XI:")
    for p in team.active_lineup:
        print(f"  {p.position.value:<11} {p.name:<15} ATK {p.base_attack:>3}  DEF {p.base_def:>3}")
    print(f"  Bench: {[p.name for p in team.bench]}\n")


def run_simulation():
    home = build_squad("Egyptia", formation="4-4-2")
    away = build_squad("Nordland", formation="5-3-2")

    match = Match(home_team=home, away_team=away)

    home_ai = MatchAi(model=DummyModel(), controlled_team=home, decision_log=[], match=match, risk_tolerance=0.5)
    away_ai = MatchAi(model=DummyModel(), controlled_team=away, decision_log=[], match=match, risk_tolerance=0.5)

    print_lineup(home)
    print_lineup(away)

    last_reported_score = (0, 0)

    while match.phase != Phase.FINISHED:
        match.run_minute_tick()

        # let each AI make a decision every ~15 in-game minutes
        if match.current_minute % 15 == 0 and match.phase == Phase.REGULATION:
            for ai in (home_ai, away_ai):
                action = ai.decide_action(match)
                ai.apply_decision(action)
                print(f"[{match.current_minute}'] {ai.controlled_team.country_name} AI decided: {action.value}")

        current_score = (match.home_score, match.away_score)
        if current_score != last_reported_score:
            print(f"[{match.current_minute}'] GOAL! {home.country_name} {match.home_score} - "
                  f"{match.away_score} {away.country_name}")
            last_reported_score = current_score

        if match.current_minute > 200:  # safety valve against any residual infinite loop
            print("Safety break: stopping simulation after 200 ticks.")
            break

    print("\n--- FINAL ---")
    print(f"{home.country_name} {match.home_score} - {match.away_score} {away.country_name}")
    if match.phase == Phase.PENALTIES or (match.home_score == match.away_score and match.winner):
        print(f"Decided on penalties. Winner: {match.winner.country_name}")
    elif match.winner:
        print(f"Winner: {match.winner.country_name}")
    else:
        print("Match drawn.")

    print("\nTimeline:")
    for event in match.time_line:
        print(" ", event.to_string())

    print("\nRed-carded players:")
    for team in (home, away):
        for p in team.red_card_players:
            print(f"  {team.country_name}: {p.name}")


if __name__ == "__main__":
    run_simulation()