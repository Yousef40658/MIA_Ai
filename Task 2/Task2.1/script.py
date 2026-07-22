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






