import pandas as pd
import os
from Recent_match_scrapper import get_matches_stats
from helper import merge_stats, filter_leaderboard
from Player_scrapper import get_player_stats

recent_stats = get_matches_stats("kr", "민철이여친구함-0415")
player_stats = get_player_stats("kr", "민철이여친구함-0415")


merged_stats = merge_stats(recent_stats, player_stats)

def create_champion_features(df, timestamp="2025-01-03 04:28:18", scraper_user="marthinsurya"):
    """
    Create champion-specific columns with weighted scores.
    
    Args:
        df (DataFrame): Input DataFrame
        timestamp (str): Current timestamp
        scraper_user (str): Current user's login
        
    Returns:
        DataFrame: Processed DataFrame with champion-specific columns
    """
    # Define weights for temporal importance
    weights = {
        'recent': 0.4,  # Last few games
        'weekly': 0.3,  # Last 7 days
        'season': 0.2,  # Current season
        'mastery': 0.1  # All-time
    }
    
    # Initialize new DataFrame for champion features
    champion_features = pd.DataFrame()
    
    # Copy identification columns
    champion_features['player_id'] = df['player_id']
    champion_features['region'] = df['region']
    champion_features['timestamp'] = timestamp
    champion_features['scraper_user'] = scraper_user
    
    # Process each champion's data
    def calculate_champion_score(row, champion):
        score = 0
        
        # Recent performance (from most_champ_1/2/3)
        for i in range(1, 4):
            if row[f'most_champ_{i}'] == champion:
                score += weights['recent'] * (
                    (float(row[f'WR_{i}']) if pd.notna(row[f'WR_{i}']) else 0) * 0.6 +
                    (float(row[f'KDA_{i}']) if pd.notna(row[f'KDA_{i}']) else 0) * 0.4
                )
                
        # Weekly performance (from 7d_champ_1/2/3)
        for i in range(1, 4):
            if row[f'7d_champ_{i}'] == champion:
                score += weights['weekly'] * (
                    (float(row[f'7d_WR_{i}']) if pd.notna(row[f'7d_WR_{i}']) else 0)
                )
                
        # Season performance (from season_champ_1-7)
        for i in range(1, 8):
            if row[f'season_champ_{i}'] == champion:
                wr = float(str(row[f'wr_{i}']).rstrip('%')) / 100 if pd.notna(row[f'wr_{i}']) else 0
                games = float(row[f'games_{i}']) if pd.notna(row[f'games_{i}']) else 0
                score += weights['season'] * (wr * games / 100)  # Normalize by games played
                
        # Mastery (from mastery_champ_1-16)
        for i in range(1, 17):
            if row[f'mastery_champ_{i}'] == champion:
                mastery = float(row[f'm_lv_{i}']) if pd.notna(row[f'm_lv_{i}']) else 0
                score += weights['mastery'] * (mastery / 7)  # Normalize by max mastery level
                
        return score
    
    # Get unique champions from all sources
    all_champions = set()
    
    # From recent champions
    for i in range(1, 4):
        all_champions.update(df[f'most_champ_{i}'].dropna())
    
    # From season champions
    for i in range(1, 8):
        all_champions.update(df[f'season_champ_{i}'].dropna())
    
    # From weekly champions
    for i in range(1, 4):
        all_champions.update(df[f'7d_champ_{i}'].dropna())
    
    # From mastery
    for i in range(1, 17):
        all_champions.update(df[f'mastery_champ_{i}'].dropna())
    
    # Calculate scores for each champion
    for champion in all_champions:
        if pd.notna(champion):
            champion_col = f'champion_score_{champion.replace(" ", "_").lower()}'
            champion_features[champion_col] = df.apply(
                lambda row: calculate_champion_score(row, champion), 
                axis=1
            )
    
    # Add role preferences (might influence champion selection)
    role_cols = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
    for col in role_cols:
        champion_features[f'role_pref_{col.lower()}'] = df[col]
    
    # Save to CSV
    output_file = os.path.join("util", "data", "champion_features.csv")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    champion_features.to_csv(output_file, index=False)
    
    # Print summary
    print("\nChampion Features Summary:")
    print(f"Number of unique champions: {len(all_champions)}")
    print(f"Total features created: {len(champion_features.columns)}")
    print("\nSample champion scores (first 5 rows, first 5 champions):")
    champion_cols = [col for col in champion_features.columns if col.startswith('champion_score_')]
    print(champion_features[champion_cols[:5]].head())
    
    return champion_features

# Example usage:
if __name__ == "__main__":
    # Read your filtered leaderboard data
    df = pd.read_csv("util/data/filtered_lb.csv")
    
    # Create champion features
    champion_features = create_champion_features(
        df,
        timestamp="2025-01-03 04:28:18",
        scraper_user="marthinsurya"
    )