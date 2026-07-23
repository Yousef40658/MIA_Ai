import pandas as pd 
import matplotlib as plt 
import os 
import numpy as np
from data_explorer_class import DataExplorer
from data_cleaning_class import DataCleaner
#- some of the functions or lines can be squeezed by using kwargs to also improve generality but i thought keeping it task specific would make it easier to implement and readable

class FootballAnalysis():
    def __init__(self , clean = False):
        #loading data
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.load_dataframes()

        #doesn't clean automatically , in case of exploring the data first for integrity  
        self.clean = clean
        if self.clean:
             self.clean_data_frames()
             self.cleaned = True
             
        

    def load_dataframes(self):
            self.former_names_path = self.__building_csv_path("former_names")
            self.goal_scorers_path = self.__building_csv_path("goalscorers")
            self.results_path      = self.__building_csv_path("results")
            self.shootouts_path    = self.__building_csv_path("shootouts")

            self.df_results      = self.__read_csv(self.results_path)
            self.df_former_names = self.__read_csv(self.former_names_path)
            self.df_goal_scorers = self.__read_csv(self.goal_scorers_path)
            self.df_shootouts    = self.__read_csv(self.shootouts_path)

    def __building_csv_path(self , csv_name):
        return os.path.join(self.script_dir , f"{csv_name}.csv")

    def __read_csv(self, path) :
        df = pd.read_csv(path, on_bad_lines='skip').replace(r'"', '', regex=True)
        df.columns = df.columns.str.strip()
        return df

    def exploring_dataframes(self):
        #data exploring --i've built this class in previous work--
        #i like to explore the data first before looking even at the task, then i inspect it again after seeing the task
        results_exp      = DataExplorer(self.results_path)
        former_names_exp = DataExplorer(self.former_names_path) 
        goal_scorers_exp = DataExplorer(self.goal_scorers_path)
        shootouts_exp    = DataExplorer(self.shootouts_path)

        self.__explore_csv(results_exp)
        self.__explore_csv(former_names_exp)
        self.__explore_csv(goal_scorers_exp)
        self.__explore_csv(shootouts_exp)

    def __explore_csv(exp : DataExplorer):
        exp.basic_structure()
        exp.values_inspection()
        exp.check_outliers()
        exp.get_duplicates()
        exp.check_for_skewness()
        exp.get_correlations()

    def clean_data_frames(self):
            self.__map_former_names(self.df_results, self.df_former_names)
            self.__map_former_names(self.df_goal_scorers,  self.df_former_names)
            self.__map_former_names(self.df_shootouts, self.df_former_names)

            #
            self.df_results      = DataCleaner(self.df_results).clean_df()
            self.df_shootouts    = DataCleaner(self.df_shootouts).clean_df()
            self.df_goal_scorers = DataCleaner(self.df_goal_scorers).clean_df()

            self.cleaned = True

    #renaming the countries using former names.csv, i looked at mapping method using dict(zip), as i read its faster because its factorized 
    #but the data here is date-dependent
    def __map_former_names(self ,df : pd.DataFrame , mapping_csv : pd.DataFrame):
        for current , former , start_date , end_date in mapping_csv.itertuples(index= False , name= None):
            mask = (df["date"] >= start_date) & (df["date"] <= end_date)#masking the interval only to make it faster
            df.loc[mask , "home_team"]= df.loc[mask, "home_team"].replace(former, current)
            df.loc[mask , "away_team"]= df.loc[mask, "away_team"].replace(former, current)

    def top_10_performers(self):
        if not self.cleaned :
             self.clean_data_frames()
             self.cleaned = True
        ## 2.11 Top 10 national teams with most goals 
        # df_goal_scorers.groupby("team" , as_index= Falsewhat )
        teams_ranking = (
                self.df_goal_scorers["team"].value_counts().reset_index().head(10)
            )

        scorers_ranking = (
                self.df_goal_scorers["scorer"].value_counts().reset_index().head(10)
            )

        print(teams_ranking) #didn't know germany was that strong
        print(scorers_ranking) 

    def top_10_efficiency(self):
        if not self.cleaned :
             self.clean_data_frames()
             self.cleaned = True

        scenarios = [ 
                 self.df_results["home_score"] > self.df_results["away_score"],
                 self.df_results["home_score"] ==self.df_results["away_score"],
                 self.df_results["home_score"] < self.df_results["away_score"]
             ]
         
        home_pts = [3 , 1 , 0]
        away_pts = [0 , 1 , 3]
         
        self.df_results["home_pts"] = np.select(condlist= scenarios , choicelist= home_pts)
        self.df_results["away_pts"] = np.select(condlist= scenarios , choicelist= away_pts)  
         
        # print (df_results.head(10))
        self.df_results["home_efficiency"] = self.df_results["home_pts"] + self.df_results["home_score"]
        self.df_results["away_efficiency"] = self.df_results["away_pts"] + self.df_results["away_score"]
         
        #i was thinking of using groupby over home and away then summing ones with similar team but found df.concat
        #creating dfs with team and efficiency cols
        home_df = self.df_results[["home_team", "home_efficiency","home_pts"]].rename(columns= {"home_team" : "team" , "home_efficiency" : "efficiency" , "home_pts" :"pts"})
        away_df = self.df_results[["away_team", "away_efficiency","away_pts"]].rename(columns= {"away_team" : "team" , "home_efficiency" : "efficiency" , "away_pts" :"pts"})
         
        team = pd.concat([home_df, away_df] , ignore_index= True) #stacks them vertically 
         
        efficiency_ranking = (
                team.groupby("team")["efficiency"].sum().round(2)
                .sort_values(ascending= False).reset_index().head(10)
             )
         
        pts_ranking = (
                team.groupby("team")["pts"].sum().round(0)
                .sort_values(ascending= False).reset_index().head(10)
             )

        print (f"{pts_ranking} \n" )
        print (efficiency_ranking)
         









def main() :  
     football_analysis = FootballAnalysis(clean= True)
     football_analysis.top_10_performers()
     football_analysis.top_10_efficiency()
    

main()