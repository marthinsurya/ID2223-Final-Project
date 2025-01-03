from Recent_match_scrapper import get_matches_stats
from Meta_scrapper import get_meta_stats
from helper import merge_stats
from Player_scrapper import get_player_stats

recent_stats = get_matches_stats("kr", "민철이여친구함-0415")
player_stats = get_player_stats("kr", "민철이여친구함-0415")
#meta_stats = get_meta_stats()

merged_stats = merge_stats(recent_stats, player_stats)