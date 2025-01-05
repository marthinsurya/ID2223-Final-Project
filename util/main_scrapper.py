from Recent_match_scrapper import get_multiple_matches_stats
from Meta_scrapper import get_meta_stats
from Leaderboard_scrapper import scrape_leaderboards
from connection_check import check_connection
from helper import merge_stats, filter_leaderboard, get_player_list
from Player_scrapper import get_multiple_player_stats
from feature_eng import create_champion_features
from Weekly_meta_scrapper import get_weekly_meta
import pandas as pd


#check_connection(region="euw", summoner="Szygenda #EUW")

#meta_stats = get_meta_stats()                       #save to meta_stats.csv
#weekly_meta_stats = get_weekly_meta()               #save to weekly_meta_stats.csv

#leaderboard = scrape_leaderboards(                #save to leaderboard_data.csv
#    regions=["kr", "euw", "vn", "na"],  
#    pages_per_region=5
#)

#filtered_lb = filter_leaderboard(                 #save to lb_filtered.csv   
#        df=leaderboard,
#        tiers=["CHALLENGER"]
#    )

#player_list = get_player_list(filtered_lb)             
#player_list = get_player_list()               # without arg, it will read from lb_filtered.csv

#player_stats = get_multiple_player_stats(player_list)    #save to player_stats.csv
#recent_stats = get_multiple_matches_stats(player_list)   #save to recent_stats.csv

#recent_stats = pd.read_csv("util/data/recent_matches_checkpoint.csv")
#player_stats = pd.read_csv("util/data/player_stats.csv")
#merged_stats = merge_stats(recent_stats, player_stats)          #save to player_stats_merged.csv


#feature engineering
merged_stats = pd.read_csv("util/data/player_stats_merged_2025-01-05.csv")
training_features = create_champion_features(merged_player_stats=merged_stats, debug=None, consider_team_comp=True, test_mode=False)   #save to feature_eng_stats.csv