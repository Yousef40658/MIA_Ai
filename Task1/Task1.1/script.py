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
        result = input(f"Enter the match's score(X-Y) for {first_team} vs {second_team} : ")

        #allowing the user to just press enter indicating 0-0
        if result.strip() == "" :
            result = "0-0"
     
        try :
            team1_goals , team2_goals = result.split("-")
        
        # recursion so the function runs again instead of breaking
        except :
            print("Enter the result correctly as [team1_goals-team2_goals] , goals separated by -")
            update_data(teams_data, matches)
        
        ## 
        team1_goals = int(team1_goals)
        team2_goals = int(team2_goals)

        # updates the list of winners to apply the Head-to-Head rule in case of a tie in points
        result = process_match(teams_data,first_team, second_team , team1_goals , team2_goals) 
        results.append(result)

    return results

## final standings
def print_standings(teams_data) :
    for team in teams_data :
        #formatting it in wanted format if not 0 , otherwise keep it a normal int 
        teams_data[team]["GD"] = f"{teams_data[team]['GD']:+d}" if teams_data[team]["GD"] != 0 else "0"
        print(f"{team} : {teams_data[team]}")





##  tie breaking 
def head_to_head(teams_names,teams_data) :
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
        for index in indices:
            teams_in_draw.append(teams_names[index])
    
    print (teams_in_draw)

            



    





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

    results = update_data(teams_data , matches)
    print_standings(teams_data)
    
    print(results)
    head_to_head(teams_names,teams_data)




    



main()
        
     


