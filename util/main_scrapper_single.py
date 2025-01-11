from Recent_match_scrapper import get_multiple_matches_stats
from Meta_scrapper import get_meta_stats
from Leaderboard_scrapper import scrape_leaderboards
from connection_check import check_connection
from helper import merge_stats, filter_leaderboard, get_player_list
from Player_scrapper import get_multiple_player_stats, get_player_stats
from feature_eng import create_champion_features
from Weekly_meta_scrapper import get_weekly_meta
import pandas as pd

#meta_stats = get_meta_stats()                       #save to meta_stats.csv
#weekly_meta_stats = get_weekly_meta()               #save to weekly_meta_stats.csv

# Sample data
data = {
    'username': ['Agurin #EUW', 'Afflictive #藍月なくる', 'washed úp #EUW', 'NS Jiwoo #KR1', 'Ben10 #203'],
    'region': ['euw', 'na', 'euw', 'kr', 'vn']
}

# Create DataFrame
player_df = pd.DataFrame(data)


player_stats = get_multiple_player_stats(player_df)    #save to player_stats.csv
recent_stats = get_multiple_matches_stats(player_df)   #save to recent_stats.csv
merged_stats = merge_stats(recent_stats, player_stats)          #save to player_stats_merged.csv

#feature engineering
training_features = create_champion_features(merged_player_stats=merged_stats, debug=None, consider_team_comp=True, test_mode=False)   #save to feature_eng_stats.csv