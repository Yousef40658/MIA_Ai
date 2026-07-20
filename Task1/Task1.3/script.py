from enum import Enum
import random 
from random import Random
class Position(Enum):
    FORWARD = "FORWARD"
    MIDFIELDER = "MIDFIELDER"
    DEFENDER = "DEFENDER"
    GOALKEEPER = "GOALKEEPER"

class Event(Enum) :
    GOAL = "GOAL"
    SUBSTITUTION = "SUBSTITUTION"
    HALF_TIME = "HALF_TIME"
    FULL_TIME = "FULL_TIME"

class Phase(Enum):
    REGULATION = "REGULATION"
    FINISHED = "FINISHED"
    PENALTIES = "PENALTIES"

class Player():
    def __init__(self , name : str , position : Position , base_attack : int , base_def : int , stamina : float):
        self.name = name
        self.position = position
        self.base_attack = base_attack
        self.base_def = base_def 
        self.stamina = stamina
    
    def deplete_stamina(self , rate):
        self.stamina -= rate
        #limits it to 10
        self.stamina = max(self.stamina , 10) 

    def get_effective_attack(self):
        return (self.base_attack * (self.stamina / 100.0))
    
    def get_effective_defense(self):
        return (self.base_def * (self.stamina / 100.0))
    
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------  
class Team():
    def __init__(self , country_name : str , roster : list[Player] ,active_lineup : list[Player]
                 ,bench : list[Player] , substitution_remaining : int) :
        self.country_name = country_name
        self.roster = roster
        self.active_lineup = active_lineup  
        self.bench = bench
        self.substitution_remaining = substitution_remaining

        #since those values are constant until a substitution is made  or stamina decreases, its safe to use them here
        #now we're initializing the attack and defense stats hmm lets build a cleaner update_stats
        self.update_stats()


    # updates attack and defense stats based on the current active lineup and their stamina, must be called for every stamina change or every substitution 
    def update_stats(self):
        self.get_aggregate_attack()
        self.get_effective_attack()
        self.get_aggregate_defense()
        self.get_effective_defense()

    #attack stats
    def get_aggregate_attack(self):
        self.team_total_attack = 0
        for player in self.active_lineup:
            self.team_total_attack += player.get_effective_attack()
        return self.team_total_attack
        
    def get_effective_attack(self):
        #specify attacking players only(midfield and forwards)
        attacking_players = [player for player in self.active_lineup if player.position in [Position.FORWARD , Position.MIDFIELDER]]
        
        attack  = 0 
        for player in attacking_players:
            attack += player.get_effective_attack()

        self.effective_attack = self.team_attack / len(attacking_players)
        return self.effective_attack
    

    # defense stats
    def get_aggregate_defense(self):
        self.team_total_defense = 0
        for player in self.active_lineup:
            self.team_total_defense += player.get_effective_defense()
        return self.team_total_defense
    
    def get_effective_defense(self):
        #specify defending players only(defenders and goalkeepers)
        defending_players = [player for player in self.active_lineup if player.position in [Position.DEFENDER , Position.GOALKEEPER]]
    
        defense  = 0 
        for player in defending_players:
            defense += player.get_effective_defense()

        self.effective_defense = self.team_defense / len(defending_players)
        return self.effective_defense
        

    # 
    def execute_substitution(self , player_out : Player , player_in : Player):
        if self.substitution_remaining > 0:
            #validates that the substitution is valid
            if player_out in self.active_lineup and player_in in self.bench:
                self.active_lineup.remove(player_out)
                self.bench.append(player_out)

                self.bench.remove(player_in)
                self.active_lineup.append(player_in)    

                self.substitution_remaining -= 1

    
                self.update_stats()
                return True
            else:
                print("Invalid substitution. Player out must be currently active and player in must be on the bench")
                return False
        else :
            print("No substitutions remaining")
            return False
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MatchEvent():
    def __init__(self , event_id : str , event_type : Event , minute : float , team : Team , player : Player,
                 outcome_text : str) :
        self._event_id = event_id
        self._event_type = event_type
        self._minute = minute
        self._team = team
        self._player = player
        self._outcome_text = outcome_text

    #getters only , no setters 
    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def event_type(self) -> Event:
        return self._event_type

    @property
    def minute(self) -> int:
        return self._minute

    @property
    def team(self) -> "Team":
        return self._team

    @property
    def player(self) -> "Player":
        return self._player

    @property
    def outcome_text(self) -> str:
        return self._outcome_text
        
    def to_string(self) -> str:
            return f"[{self._minute}'] {self._event_type.value}: {self._team}{self.player} - {self._outcome_text}"
    
#------------------------------------------------------------------------------------------------------------------
class Match():
        def __init__(self , home_team : Team,away_team : Team , home_score : int , away_score: int , 
                    time_line : list[MatchEvent], phase : Phase , current_minute : int = 0):
            self.home_team = home_team
            self.away_team = away_team
            self.home_score = home_score
            self.away_score = away_score
            self.current_minute = current_minute
            self.time_line = time_line
            self.phase = phase
            self.base_decay = 0.5 # stamina decay rate per minute
        
        def run_minute_tick(self):
            self.current_minute += 1    
            if self.current_minute <= 90 :
                self.phase = Phase.REGULATION
                self.winner = None
            else :
                self.phase = Phase.FINISHED
                self.winner = self.home_team if self.home_score > self.away_score else self.away_team if self.away_score > self.home_score else None
                print (f"Match finished. Final score: {self.home_team.country_name} {self.home_score} - {self.away_score} {self.away_team.country_name}. Winner: {self.winner.country_name if self.winner else 'Draw'}")
                return  #
        
            #reduces stamina by base_decay every minute , i've already constrained it inside the player method 
            for player in self.home_team.active_lineup:
                player.deplete_stamina(self.base_decay)
            
            for player in self.away_team.active_lineup:
                player.deplete_stamina(self.base_decay)

            # home team chance to attempt a goal, i don't get the 
            if random.random() < 0.1 :
                self.process_goal_attempts(self.home_team , self.away_team)
            # away team chance to attempt a goal
            if random.random() < 0.1 :
                self.process_goal_attempts(self.away_team , self.home_team)


        def process_goal_attempts(self , attacking_team : Team , defending_team : Team) :
            # calculate attack and defense states for both teams
            attacking_team.update_stats()
            defending_team.update_stats()

            if (attacking_team.effective_attack * random.uniform(0.75 , 1.25)) > (defending_team.effective_defense * random.uniform(0.8 , 1.20)) :
                # goal scored
                self.home_score += 1 if attacking_team == self.home_team else 0
                self.away_score += 1 if attacking_team == self.away_team else 0

                # create a goal event and add it to the timeline
                goal_event = MatchEvent(event_id=f"goal_{self.current_minute}", 
                                        event_type=Event.GOAL, 
                                        minute=self.current_minute, 
                                        team=attacking_team, 
                                        player="name",  #i don't football players names o.o
                                        outcome_text="Goal scored!")
                self.time_line.append(goal_event)
