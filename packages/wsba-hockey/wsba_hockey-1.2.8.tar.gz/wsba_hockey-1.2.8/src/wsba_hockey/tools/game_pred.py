import joblib
import os
import pandas as pd
import numpy as np
import xgboost as xgb
import scipy.sparse as sp
import wsba_hockey.wsba_main as wsba
import wsba_hockey.tools.scraping as scraping
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve, auc

### GAME PREDICTION MODEL FUNCTIONS ###
# Provided in this file are functions vital to the game prediction model in the WSBA Hockey Python package. #

## GLOBAL VARIABLES ##
dir = os.path.dirname(os.path.realpath(__file__))
roster_path = os.path.join(dir,'rosters\\nhl_rosters.csv')
schedule_path = os.path.join(dir,'schedule/schedule.csv')

def prep_game_data(pbp):
    #Prepare schedule data for model development given full-season pbp

    #Calculate necessary team stats (by game) for the prediction model
    #The model will evaluate based on three different qualities for valid EV, PP, and SH strength 
    dfs = []
    for strength in [['5v5'],['5v4'],['4v5']]:
        team_games = wsba.nhl_calculate_stats(pbp,'team',[2,3],strength,True)
        team_games['Year'] = team_games['Season'].str[0:4].astype(int)
        dfs.append(team_games)

    #Place the games in order and create sums for 
    df = pd.concat(dfs).sort_values(by=['Year','Game'])