# initial plan

## Data Exploring
### Basic Structure
43500 sample over 75 features 
Positions are Defender 
Midfielder
Forward
Goalkeeper 
data is spread across 998 unique players 

there is no null values , outliers are relatively low to the n of samples 

player_rating the target have multiple zero values when minutes played = 0 , i guess we don't need this data ? we can put a simple if conidition for the prediction that if mins played = 0 then rating = 0 
#### Useless Features[pre cov matrix]
ID , name ,team , nationality [not sure will check cov matrix] ,jersey_n , club_name ,match_id , match_date ,stadium , city ,opponent_team,tournament_stage,match_result(maybe players who win often have more value but i don't know),goals_team or we can keep them because winning teams usually get a higher score rating ?
goals_opponent may matter if the GK is the main GK for his national team


- we'll use position to determine the features that affects their rating 

#### Features Combining 
we'll try first with a tree based model, see if it'll decide correctly that if it's in this position we should look at those featuers and it fails guess i'll find a way to hardcode it 
##### Defense 
crosses,successful_crosses,tackles,interceptions,clearances,blocks,aerial_duels_won,aerial_duels_lost,recoveries,defensive_actions
distance_covered_km,sprint_distance_km,top_speed_kmh
accelerations,decelerations,defensive_contribution
possession_impact,

##### Attack
preferred_foot , minutes_played,goals,assists,shots,shots_on_target,expected_goals_xg,expected_assists_xa,key_passes,successful_passes,total_passes,pass_accuracy,dribbles_attempted,successful_dribbles
offsides maybe 
distance_covered_km,sprint_distance_km,top_speed_kmh
accelerations,decelerations,
offensive_contribution,



##### GoalKeeping 
,saves,save_percentage,punches,clean_sheet,goals_conceded,penalty_saves


### Correlation 
i'll replace things with < 0.9 correlation to give more time for tunning if it took alot of time. but i know that tree models don't suffer 
minutes played : distance_covered_km , sprint_distance_km ,i'll write code for that no need to manually inspect this hard
but we'll first drop useless and change the type of needed cols 
note -> removing this 0 minutes played completely changed the minutes played correlation which makes sense because they were at 0.0 for so many rows
there are now high variance in the data kinda so we'll stick to keeping them all first 

preferred foot should be 0 , 1 
okay data typings is correct , no need for parsing 

## Data Cleaning


## Trying most promising model
[https://medium.com/@samiraalipour/understanding-and-handling-skewness-in-machine-6e8fc8b15382]
since there are some skewness levels i've never seen before data is highly non-normally distributed, we can fix this skewing and use parametric or linear models

### https://www.kaggle.com/discussions/questions-and-answers/539888
found this comment , rather than normalizing , i'll first try models that work with skewed data 
 

https://medium.com/@jangdaehan1/regression-under-non-normality-advanced-insights-into-supervised-learning-1ea900719b36 , we may try that out of curiosity too 




## Hyperparameter search to fine tune 
### without fine tuninng
execluding perfomenance col i got ,values are very very low if the col is used since it explains 92% of the variance.
guess its a leakage because if you've rating is just performance translated ?
randomforest : Mean CV MSE : 0.3806 (+/- 0.0059) 
lightbgm : Mean CV MSE: 0.3791 (+/- 0.0061)
xgboost : Mean CV MSE : 0.3792 (+/- 0.0059)
catboost : Mean CV MSE 0.3772 (+/- 0.0057)


https://www.kaggle.com/discussions/questions-and-answers/468487 , https://dev.to/iemsaad/optimizing-machine-learning-models-comparing-grid-search-randomized-search-and-optuna-4hnf
both suggest using grid search instead of optuna for small datasets since it moves through all combinations it's gauranteed given realistic upper and lower limit to find maximum accuracy 

starting with catboost 


performance isn't a leakage 
randomforest : Mean CV MSE 0.1348 (+/- 0.0037)
lightbgm : Mean CV MSE: 0.0732 (+/- 0.0005)
xgboost : Mean CV MSE (XGB): 0.0738 (+/- 0.0004)
catboost : Mean CV MSE 0.0729 (+/- 0.0004)

trying with a model for each position 


trying with per_play_minute featuers 
made catboost 0.0728 and XGbppst -.0737 
created script_2.ipynb to optuna with new features using CPU while the GPU grid searches 

### optuna run 1 
        model = CatBoostRegressor(
            iterations=5000,
            task_type='CPU',
            random_seed=42,
            verbose=False,
            early_stopping_rounds=50,
            **params
        )

Best MSE: 0.07278531534629813
Best RMSE: 0.2697875374184251
Best params: {'depth': 6, 'learning_rate': 0.010007132386538472, 'l2_leaf_reg': 1.3630467109604305, 'min_data_in_leaf': 32, 'random_strength': 1.699987960279682, 'bagging_temperature': 0.8333129955129245, 'border_count': 254}
hmmmm not good enough , aiming for < 0.05 

runnning extended optuna catboost run also converged to the same range , think its the noise in the data so i'll reexplore and reclean first and i'm also thinking of testing without the low correlated featuers 
will check general integrity of some rows with checking that n of attempted is always >= to number of achived , wins are set correctly

with removed low features i still got the same values exactly , so as expected they didn't matter becuase we're using trees

## XAI 
https://youtube.com/playlist?list=PLqDyyww9y-1SwNZ-6CmvfXDAOdLS7yUQ4&si=ZTYJGvsa4tAqLy4V[firrst and 4th vid]
https://shap.readthedocs.io/en/latest/example_notebooks/tabular_examples/tree_based_models/Understanding%20Tree%20SHAP%20for%20Simple%20Models.html
### Interpretable x Explainable
interpretable models are models that are easily understandable , you can explain the model choice or simply have an equation like normal regressions. a line with slope and interception so by easily looking at this equation you realize why the model make such prediction 

### Explainable ML
models that aren't understandable easily like neural networks with inner hidden layers or 
TreeSHAP is used with tree-based models

- mean |shap| gets skewed by outliers just like any mean, so check median/trimmed mean too before trusting it

- there may be an imbalance so we can use XAI for each position , we also can use those to set the cols for each position and try this multiple model approach again 

- if going interventional, background dataset needs to actually represent the data, not accidentally oversample the tail or the mode

### https://medium.com/data-science/kernelshap-vs-treeshap-e00f3b3a27db
treeSHAP is much faster , used only for tree based algorithms which meet our xgboost , catboost
![alt text](image.png) ~ there is extremely large time difference between both and both are of the same accuracy
KernalSHAP treats the model as a blackbox and try to fit via weighted least squares -monte carlo estimator-
while treeSHAP exploits the fact of actual tree structure 
Interventional treeSHAP is slower but still much faster than 


### difference between Interventional and path-dependent 
shaply works by answering the questions 'if we didn't know feature x , what value would fill in for it"
path-dependent : uses the known features to guess the missing one, so with highly correlated features it'll be like they are exactly replaced or most of the weight will be given to the its highly correlated twin 

Interventional : when a feature is missing , it searches through the background dataset and replaces it's value with a value of the dataset , does this multiple times then averages those readings
to answer the question of how much does knowing feature x rather than assuming it's the avg value helps the model 
for example if you swap the feature with 8000 other values and you still got the same prediction and you still got answer close to your actual answer that means that this value doesn't matter match for the target 

uses background dataset , cleanly isolates each feature's own effect even with high correlation 

![alt text](image-1.png)
performance_score          0.503368
consistency_score          0.028934
market_value_eur           0.024280
pressure_resistance        0.020855
defensive_contribution     0.007955
result_w                   0.007136
fouls_committed            0.005938
offensive_contribution     0.005415
goals_overperformance      0.005067
creativity_score           0.004717
assist_overperformance     0.004488
successful_passes_per90    0.004163
possession_impact          0.003777
goal_difference            0.002840
total_passes               0.002666
dtype: float64

performance_score share of total SHAP magnitude: 74.7%


lets try with non cleaned data maybe we're dropping some important features 
still a very big difference
performance_score         0.510489
market_value_eur          0.030927
consistency_score         0.029413
pressure_resistance       0.020821
defensive_contribution    0.009652
goals                     0.008351
result_W                  0.008266
assists                   0.006912
possession_impact         0.006675
creativity_score          0.006364
offensive_contribution    0.006141
fouls_committed           0.005685
total_passes              0.005095
successful_passes         0.002514
goals_team                0.001687
dtype: float64

performance_score share of total SHAP magnitude: 74.6%

lets try the extreme outlier from before
performance_score          0.503864
market_value_eur           0.027410
pressure_resistance        0.025678
consistency_score          0.023270
offensive_contribution     0.007252
defensive_contribution     0.007238
result_w                   0.007131
goals                      0.006715
assists                    0.004889
fouls_committed            0.003706
creativity_score           0.003229
result_l                   0.003122
successful_passes_per90    0.002791
total_passes               0.002311
possession_impact          0.002300
dtype: float64

performance_score share of total SHAP magnitude: 77.0%
didn't matter , it acutally made it worse which makes sense because some outliers were representative 