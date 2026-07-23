from enum import Enum
import random 
from random import Random
import numpy as np
import json
import os
from groq import Groq

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
    FOUl      = "FOUL"

class Phase(Enum):
    REGULATION = "REGULATION"
    FINISHED = "FINISHED"
    PENALTIES = "PENALTIES"


# --------------------
#Bonus
#---------------------
class Actions(Enum) :
    SUBSTITUTE = "SUBSTITUTE"
    CHANGE_FORMATION = "CHANGE_FORMATION"
    HOLD = "HOLD"
    ATTACK = "ATTACK"

ACTION_KEYWORDS = {
    "SUBSTITUTE": Actions.SUBSTITUTE,
    "CHANGE_FORMATION": Actions.CHANGE_FORMATION,
    "HOLD": Actions.HOLD,
    "ATTACK": Actions.ATTACK,
    "PUSH_ATTACK": Actions.ATTACK,
}

FORMATION_BUCKETS = [
    "5-3-2",
    "4-4-2" ,
    "3-4-3",
]

###

class Player():
    def __init__(self , name : str , position : Position , base_attack : int , base_def : int , stamina : float , subbed : bool = False):
        self.name = name
        self.position = position
        self.base_attack = base_attack
        self.base_def = base_def 
        self.stamina = stamina
        self.subbed = subbed
        self.yellow_card = False
        self.red_card = False
        self.injured = False

    
    def deplete_stamina(self , rate):
        #limits it to 10
        self.stamina = max(self.stamina - rate , 10) 

    def get_effective_attack(self):
        return (self.base_attack * (self.stamina / 100.0))
    
    def get_effective_defense(self):
        return (self.base_def * (self.stamina / 100.0))
    
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------  
class Team():
    def __init__(self , country_name : str , roster : list[Player] ,active_lineup : list[Player]
                 ,bench : list[Player] , substitution_remaining : int , automatic_sub : bool = False , formation = None) :
        self.country_name = country_name
        self.roster = roster
        self.active_lineup = active_lineup  
        self.bench = bench
        self.substitution_remaining = substitution_remaining
        self.automatic_sub = automatic_sub
        self.red_card_players = []
        self.formation = formation if formation else "4-4-2"
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

        # so that's the attribute that actually exists by the time we get here (was self.team_attack)
        self.effective_attack = (attack / len(attacking_players)) if attacking_players else 0

        if self.formation == "3-4-3" :
            self.effective_attack += 40
        elif self.formation == "4-4-2" :
            self.effective_attack += 20 
        
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

        self.effective_defense = (defense / len(defending_players)) if defending_players else 0

        if self.formation == "5-3-2":
            self.effective_defense += 40 

        return self.effective_defense
        

    # 
    def execute_substitution(self , player_out : Player , player_in : Player):
        if self.substitution_remaining > 0:
            #validates that the substitution is valid
            if player_out in self.active_lineup and player_out.subbed == False and player_in in self.bench:
                self.active_lineup.remove(player_out)
                self.bench.append(player_out)

                self.bench.remove(player_in)
                self.active_lineup.append(player_in)    

                self.substitution_remaining -= 1

                player_out.subbed = True
    
                self.update_stats()
                return True
            else:
                print("Invalid substitution. Player out must be currently active and player in must be on the bench")
                return False
        else :
            print("No substitutions remaining")
            return False
        
#---------------------------
    def Automatic_substitution(self):
        if len(self.bench) > 0 and self.substitution_remaining > 0 :
            #finds lowest stamina player then replaces with bench , i've set it to always be bench[0
            lowest_stamina_player = min(self.active_lineup , key = lambda player:player.stamina)
            #since it should be of same type [hopefully yy3ny]
            #to disable choosing a player that just got substituted , i'll also add a subbed flag to avoid subbing a player twice 
            suitable_players = [player for player in self.bench if player.position == lowest_stamina_player.position and player.stamina > lowest_stamina_player.stamina and player.subbed == False]

            # skip substitution if no suitable players are available
            if not suitable_players:
                return

            player_in = random.choice(suitable_players) #ofc we can also make it by highest defense if position is def , attack otherwise

            self.execute_substitution(lowest_stamina_player , player_in)

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

        if self.event_type is Event.FOUl :
            self.process_foul(self._player)

    #getters only , no setters 
    def process_foul(self , player_fouled : Player) :        
        injure_probability = random.random()
        if injure_probability< 0.3 : 
            player_fouled.injured = True
            # reduce stamina of fouled player
            player_fouled.stamina -= ((random.uniform(0.4 , 0.6)) * 30)

        if self.event_type is Event.FOUl :
            if player_fouled.injured :
                if self._player.yellow_card :
                    self._player.red_card = True 
                    
                    if self._player in self._team.active_lineup :
                        self._team.active_lineup.remove(self._player)
                    if self._player not in self._team.red_card_players :
                        self._team.red_card_players.append(self._player)
                    #hmmm don't know if i should add him to bench and add if condition for subbing that player has no red card
                else :
                    self._player.yellow_card = True


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
    def outcome_text(self) -> str:
        return self._outcome_text
        
    def to_string(self) -> str:
            return f"[{self._minute}'] {self._event_type.value}: {self._team.country_name}{self._player.name} - {self._outcome_text}"
    
#------------------------------------------------------------------------------------------------------------------
class Match():
        def __init__(self , home_team : Team,away_team : Team , home_score : int = 0 , away_score: int = 0 , 
                     time_line : list[MatchEvent] = None, phase : Phase = Phase.REGULATION , current_minute : int = 0 ):
            self.home_team = home_team
            self.away_team = away_team
            self.home_score = home_score
            self.away_score = away_score
            self.current_minute = current_minute
            self.time_line = time_line if time_line is not None else []
            self.phase = phase
            self.base_decay = 0.5 # stamina decay rate per minute
            self.winner = None

        
        def run_minute_tick(self):
            #while in the 90 minutes keep running normally
            self.current_minute += 1    
            if self.current_minute <= 90 :
                self.phase = Phase.REGULATION
                self.winner = None
                if self.home_team.automatic_sub:
                    self.home_team.Automatic_substitution()
                if self.away_team.automatic_sub:
                    self.away_team.Automatic_substitution()

            # if time exceeds 90 minutes and the score is tied, transition to penalties
            elif self.phase != Phase.FINISHED and self.home_score == self.away_score:
                    self.phase = Phase.PENALTIES
                    self.penalty_shootout(self.home_team, self.away_team)
                    # transition to finished phase after penalties
                    self.phase = Phase.FINISHED
                    return
            
            # if time exceeds 90 minutes and the score is not tied, transition to finished phase
            elif self.phase != Phase.FINISHED:
                    self.winner = self.home_team if self.home_score > self.away_score else self.away_team
                    self.phase = Phase.FINISHED
                    print(f"Match finished: {self.home_team.country_name} {self.home_score} - {self.away_score} {self.away_team.country_name}. Winner: {self.winner.country_name if self.winner else 'Draw'}")
                    return

            else :
                return  #If the match is already finished, time ticking does nothing 

            #


            #reduces stamina by base_decay every minute , i've already constrained it inside the player method 
            for team in [self.home_team, self.away_team]:
                for player in team.active_lineup[:]:   # iterate over a copy
                    player.deplete_stamina(self.base_decay)

                    if player.red_card:
                        if player in team.active_lineup :
                            team.active_lineup.remove(player)
                        if player not in team.red_card_players :
                            team.red_card_players.append(player)

            # home team chance to attempt a goal, i don't get the 
            if random.random() < 0.1 :
                self.process_goal_attempts(self.home_team , self.away_team , random.choice(self.home_team.active_lineup))
            # away team chance to attempt a goal
            if random.random() < 0.1 :
                self.process_goal_attempts(self.away_team , self.home_team , random.choice(self.away_team.active_lineup))


        def process_goal_attempts(self , attacking_team : Team , defending_team : Team , scoring_player : Player) :
            # calculate attack and defense states for both teams
            attacking_team.update_stats()
            defending_team.update_stats()

            attack_factor = random.uniform(0.4 , 0.8)
            defense_factor = random.uniform(0.6,1.0) #guess scoring should be harder ._. but i don't watch football

            if ( attack_factor * attacking_team.effective_attack * random.uniform(0.75 , 1.25)) > ( defense_factor * defending_team.effective_defense * random.uniform(0.8 , 1.20)) :
                # goal scored
                self.home_score += 1 if attacking_team == self.home_team else 0
                self.away_score += 1 if attacking_team == self.away_team else 0

                # create a goal event and add it to the timeline
                goal_event = MatchEvent(event_id=f"goal_{self.current_minute}", 
                                        event_type=Event.GOAL, 
                                        minute=self.current_minute, 
                                        team=attacking_team, 
                                        player= scoring_player,  #i don't football players names o.o
                                        outcome_text="Goal scored!")
                self.time_line.append(goal_event)


        def penalty_shootout(self, team1 , team2):
            # Simulate a penalty shootout
            team1_score = 0
            team2_score = 0
            for i in range(5):
                if random.random() < 0.75:  # 75% chance to score
                    team1_score += 1
                if random.random() < 0.75:
                    team2_score += 1

            #determine the winner from the first 5 shoots
            if team1_score > team2_score:
                self.winner = team1
            elif team2_score > team1_score:
                self.winner = team2

            # if the first five shoots results in a draw , keep shooting until one team wins
            else:
                while team1_score == team2_score:
                    if random.random() < 0.75:
                        team1_score += 1
                    if random.random() < 0.75:
                        team2_score += 1
                    if team1_score > team2_score:
                        self.winner = team1
                    elif team2_score > team1_score:
                        self.winner = team2



class MatchAi():
    def __init__(self, controlled_team: Team, decision_log: list, match: Match,
                 risk_tolerance: float = 0.5, model_name: str = "llama-3.3-70b-versatile",
                 api_key: str = None):
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self.model_name = model_name
        self.controlled_team = controlled_team
        self.decision_log = decision_log
        self.risk_tolerance = risk_tolerance
        self.state = None
        self.match = match

    
    def observe_state(self ,match : Match) :
        home = True if self.controlled_team == match.home_team else False
        stamina_levels = {}
        for player in self.controlled_team.active_lineup:
            stamina_levels[player.name] = player.stamina
            
        self.state = {
            "minute" : match.current_minute,
            "phase"  : match.phase.value,
            "team_score" : match.home_score if home else match.away_score,
            "against_score" : match.away_score if home else match.home_score,
            "stamina_levels" :  stamina_levels,
            "subs_remaining" : self.controlled_team.substitution_remaining,
            'risk_tolerance' : self.risk_tolerance
        }

        return self.state
    
    def decide_action(self , match):
        #option to feed the match as an argument to use the method , otherwise fallback to the object's match
        if match is None :
            match = self.match

        #call observe_state first to udpate the self.state vector
        self.observe_state(match)

        raw = self._call_model(self._build_prompt())
        action = ACTION_KEYWORDS.get(raw.strip().upper(), Actions.HOLD)
        self.decision_log.append({"minute": match.current_minute, "action": action.value, "reason": raw.strip()})
        return action


    def apply_decision(self, action: Actions, match=None):
        if match is None:
            match = self.match
        team = self.controlled_team

        if action == Actions.SUBSTITUTE:
            if not team.bench:
                return
            player_out = min(team.active_lineup, key=lambda p: p.stamina)
            candidates = [p for p in team.bench if p.position == player_out.position and not p.subbed]
            if not candidates:
                return
            player_in = max(candidates, key=lambda p: p.base_attack + p.base_def)
            team.execute_substitution(player_out, player_in)

        elif action == Actions.CHANGE_FORMATION:
            formations = FORMATION_BUCKETS
            current = getattr(team, "formation", "4-4-2")
            team.formation = formations[(formations.index(current) + 1) % len(formations)]
            team.update_stats()

        elif action == Actions.HOLD:
            self.risk_tolerance = max(0.0, self.risk_tolerance - 0.2)

        elif action == Actions.ATTACK:
            self.risk_tolerance = min(1.0, self.risk_tolerance + 0.2)

    #building prompt in llama style, made "cowboy prompt" write it 
    def _build_prompt(self):
        return ("You are an AI football coach controlling one team mid-match.\n"
            f"Current state:\n{json.dumps(self.state, indent=2)}\n\n"
            "Choose exactly one action: SUBSTITUTE, CHANGE_FORMATION, HOLD, ATTACK.\n"
            "Respond with ONLY that single word, nothing else."
        )

    
    def _call_model(self, prompt: str) -> str:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a concise football match AI coach. Reply with exactly one word."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=8,
                    temperature=0.3,
                )
                return response.choices[0].message.content
            except Exception as e:
                # network hiccup / rate limit / bad key -> fail safe to HOLD
                print(f"Groq call failed: {e}")
                return "HOLD"