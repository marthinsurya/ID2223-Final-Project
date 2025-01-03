from Recent_match_scrapper import get_matches_stats
from Meta_scrapper import get_meta_stats
from Leaderboard_scrapper import scrape_leaderboards
from connection_check import check_connection
from helper import merge_stats, filter_leaderboard
from Player_scrapper import get_player_stats

leaderboard = scrape_leaderboards(
    regions=["kr", "euw", "vn", "na"],  
    pages_per_region=5
)

filtered_lb = filter_leaderboard(
        df=leaderboard,
        tiers=["CHALLENGER"]
    )

#check_connection(region="euw", summoner="Szygenda #EUW")

meta_stats = get_meta_stats()

recent_stats = get_matches_stats("kr", "민철이여친구함-0415")
player_stats = get_player_stats("kr", "민철이여친구함-0415")


merged_stats = merge_stats(recent_stats, player_stats)