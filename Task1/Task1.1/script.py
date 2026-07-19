import yaml

# matches processing 
def process_match(teams_data , team1,team2,team1_goals,team2_goals) :
    #
    teams_data[team1]["P"] += 1 
    teams_data[team2]["P"] += 1

    #
    teams_data[team1]["GF"] += team1_goals
    teams_data[team2]["GF"] += team2_goals

    #
    teams_data[team1]["GA"] += team2_goals
    teams_data[team2]["GA"] += team1_goals

    #
    teams_data[team1]["GD"] = (teams_data[team1]["GF"] - teams_data[team1]["GA"])
    teams_data[team2]["GD"] = (teams_data[team2]["GF"] - teams_data[team2]["GA"])

    # draw 
    if team1_goals == team2_goals :
        teams_data[team1]["Pts"] += 1
        teams_data[team2]["Pts"] += 1
        teams_data[team1]["D"] += 1
        teams_data[team2]["D"] += 1

        winner = None
        return winner

    # winner
    winner = team1 if team1_goals > team2_goals else team2
    teams_data[winner]["W"] += 1
    teams_data[winner]["Pts"] += 3

    return winner

## data updating 
def update_data(teams_data , matches):
    results = []
    for match in matches :
        first_team  = match[0]
        second_team = match[1]

        # keep re-prompting for THIS match only until we get a valid score,
        # instead of recursing over the whole matches list again
        while True :
            result = input(f"Enter the match's score(X-Y) for {first_team} vs {second_team} : ")

            #allowing the user to just press enter indicating 0-0
            if result.strip() == "" :
                result = "0-0"

            # split + int conversion both happen inside the try now, so a
            # non-numeric score (e.g. "a-b") is caught instead of crashing
            try :
                team1_goals , team2_goals = result.split("-")
                team1_goals = int(team1_goals)
                team2_goals = int(team2_goals)

            # recursion so the function runs again instead of breaking
            except :
                print("Enter the result correctly as [team1_goals-team2_goals] , goals separated by -")
                continue

            # reject negative goals (also catches malformed input like "-1-2"
            # that would otherwise split into extra/garbage pieces)
            if team1_goals < 0 or team2_goals < 0 :
                print("Goals can't be negative, try again")
                continue

            # valid input, stop asking for this match
            break

        # updates the list of winners to apply the Head-to-Head rule in case of a tie in points
        winner = process_match(teams_data,first_team, second_team , team1_goals , team2_goals) 
        results.append((first_team, second_team, team1_goals, team2_goals))

    return results

## final standings
def print_standings(teams_data) :
    for team, stats in (teams_data.items() if isinstance(teams_data, dict) else teams_data):
        #formatting it in wanted format if not 0 , otherwise keep it a normal int 
        stats["GD"] = f"{stats['GD']:+d}" if stats["GD"] != 0 else "0"
        print(f"{team} : {stats}")

#----------------
##  tie breaking 
#----------------
def getting_teams_in_draws(teams_names,teams_data) :
    # storing list of points
    points = [teams_data[team]["Pts"] for team in teams_data]
    
    
    # storing draws in a directory by indices 
    draws_indices = {}
    for index , point in enumerate(points) :
        if point not in draws_indices :
            draws_indices[point] = [index]
        else : 
            draws_indices[point].append(index)
    
    # keeps duplicated values only , values that appear at one index only are unique
    draws_indices = {point: indices for point, indices in draws_indices.items() if len(indices) > 1}

    teams_in_draw = []

    for indices in draws_indices.values():
        current_draw = []

        for index in indices:
            current_draw.append(teams_names[index])

        teams_in_draw.append(current_draw)

    return teams_in_draw

def head2head(team1, team2, match_results):
    for t1, t2, g1, g2 in match_results:
        if {t1, t2} == {team1, team2}:
            if g1 == g2:
                return None
            first_team_won = g1 > g2
            return t1 if first_team_won == (t1 == team1) else t2
    return None

def sorting_teams(teams_names, teams_data, matches, match_results) :
    sorted_teams = sorted(
        teams_data.items(),
        key = lambda team: team[1]["Pts"],
        reverse= True
    )

    teams_in_draw = getting_teams_in_draws(teams_names, teams_data)
    print_standings(sorted_teams)
    
    for draw in teams_in_draw :
        if len(draw) == 2 :
            winner = head2head(draw[0], draw[1], match_results)
            if winner :
                print(f"{winner} ranked higher on head-to-head")
            else :
                print(f"{draw[0]} and {draw[1]} still tied, fall back to goal difference")

        else :
            #highest goals
            draw.sort(key = lambda t : teams_data[t]["GF"], reverse=True)
            print("Tied group ranked by goals scored:", draw)


def main() :
    # importing the matches from thte yaml 
    with open('worldcup.yaml' , 'r') as file :
        worldcup_data = yaml.safe_load(file)

    teams_names = worldcup_data["teams"]
    matches = worldcup_data["matches"]

    #building the directory for each team, can be done by a parent class with attributes 
    teams_data = {}
    for team in teams_names :
        initial_data = {"P" : 0 , "W" : 0 , "D" : 0 , "L" : 0 , "GF" : 0 , "GA" : 0 , "GD" : 0 , "Pts" : 0}
        teams_data[team] = initial_data
    
    match_results = update_data(teams_data , matches)


    sorting_teams(teams_names , teams_data , matches, match_results)

main()