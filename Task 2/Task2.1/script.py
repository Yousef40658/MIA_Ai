import pandas as pd 
import matplotlib as plt 
import os 
from data_explorer_class import DataExplorer


#loading data
script_dir = os.path.dirname(os.path.abspath(__file__))

def building_csv_path(csv_name : str):
    return os.path.join(script_dir , f"{csv_name}.csv")

def read_csv(path) :
    return pd.read_csv(path , on_bad_lines= 'skip').replace(r'"', '' , regex= True)

former_names_path = building_csv_path("former_names")
goal_scorers_path = building_csv_path("goalscorers")
results_path      = building_csv_path("results")
shootouts_path    = building_csv_path("shootouts")

df_results      = read_csv(results_path)
df_former_names = read_csv(former_names_path)
df_goal_scorers = read_csv(goal_scorers_path)
df_shootouts    = read_csv(shootouts_path)

#data exploring --i've built this class in previous work--
#i like to explore the data first before looking even at the task, then i inspect it again after seeing the task

results_exp      = DataExplorer(results_path)
former_names_exp = DataExplorer(former_names_path) 
goal_scorers_exp = DataExplorer(goal_scorers_path)
shootouts_exp    = DataExplorer(shootouts_path)

def explore_csv(exp : DataExplorer):
    exp.basic_structure()
    exp.values_inspection()
    exp.check_outliers()
    exp.get_duplicates()
    exp.check_for_skewness()
    exp.get_correlations()

#------------------------------------------------
# explore_csv(results_exp)

#49520 matches is very reliable for data extraction 
#mean home score is 1,75 while mean away score is 1.18, makes sense that teams at home have better chances,is it due to confidence or some laser shit like egypt vs senegal  
#until the 99 percentile, data is kinda realistic.maximum home score and maximum away score are weird tho 31 and 21
#only 2 NULL values :O  and 0 duplicated cols -> makes us sure that no match was entered twice[date differs]
#data is severely skewed , std is close to mean and there is about 1.5% outliers , hmm so 1.5% of the matches end with more than 7 goals 
#more than i expected anyway 
#weak correlation between both teams scores , but it being negative indicates that when the other team scores more.
#the other team tends to score less [since it's very weak its negligible but i would say it represents 'morals']
#-------------------------------------------------


#--------------------------------------------------
# explore_csv(former_names_exp)
#okay so this will be used to map them to their current name to get accurate results
#--------------------------------------------------

#------------------------------
# explore_csv(goal_scorers_exp)
#half the goals occur between the 28m and 73m, with the fastest goal at 1 minute and the most clutch goal at 122m
#99% goals occur between the 90 minute mark, makes extra sense because not all matches have extra time 
#there are some null values regarding the minute
#own goals are almost 2% of football galls (7pipy M.hany)
#some of the goals are duplicated , i've searched in google and its very few players that scored 2 goals in the same minute. with most of them in the premier league not wc
#so this part of the data need to be removed
#very small skewness , distribution of goals is symmetric so there is no tendency of goals in general happening early or late[maybe different stratiges balance out]
#penalities make up for 6.82 of the goals
#----------------------------------------------

explore_csv(shootouts_exp)
# 683 shootouts making about 1.4% of total matches
# most first shooter information is missing 
# egypt is the most frequent winner of shootout, would be useful to study if it's due to us winning there or us reaching it far more than others | Bayes'






