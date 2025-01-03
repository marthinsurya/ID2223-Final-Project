# feature_engineering.py
import pandas as pd
import numpy as np
import os
from helper import (
    ChampionConverter, 
    convert_percentage_to_decimal,
    convert_tier_to_number,
    convert_result_to_binary
)

def create_champion_features(df, timestamp="2025-01-03 05:08:12", scraper_user="marthinsurya"):
    """
    Create features for champion prediction using player data.
    Champion names will be used as column headers.
    Uses pd.concat to avoid DataFrame fragmentation.
    """
    # Initialize the champion converter
    converter = ChampionConverter()
    
    # Define importance weights
    weights = {
        'recent': 0.4,    # Last few games
        'weekly': 0.3,    # Last 7 days
        'season': 0.2,    # Current season
        'mastery': 0.1    # All-time mastery
    }
    
    # Create dictionary to store all features
    feature_dict = {
        'player_id': df['player_id'],
        'region': df['region'],
        'timestamp': [timestamp] * len(df),
        'scraper_user': [scraper_user] * len(df)
    }
    
    # Process each champion
    for champion in converter.champions:
        # Initialize scores for this champion
        champion_scores = {
            'recent_score': np.zeros(len(df)),
            'weekly_score': np.zeros(len(df)),
            'season_score': np.zeros(len(df)),
            'mastery_score': np.zeros(len(df))
        }
        
        # Calculate scores for each player
        for idx, row in df.iterrows():
            # 1. Recent Performance
            for i in range(1, 4):
                if row.get(f'most_champ_{i}') == champion:
                    wr = float(row[f'WR_{i}']) if pd.notna(row[f'WR_{i}']) else 0
                    kda = float(row[f'KDA_{i}']) if pd.notna(row[f'KDA_{i}']) else 0
                    champion_scores['recent_score'][idx] = (wr * 0.6 + kda * 0.4)
            
            # 2. Weekly Performance
            for i in range(1, 4):
                if row.get(f'7d_champ_{i}') == champion:
                    wr = convert_percentage_to_decimal(str(row[f'7d_WR_{i}']))
                    games = float(row[f'7d_total_{i}']) if pd.notna(row[f'7d_total_{i}']) else 0
                    champion_scores['weekly_score'][idx] = wr * (games / 10)
            
            # 3. Season Performance
            for i in range(1, 8):
                if row.get(f'season_champ_{i}') == champion:
                    wr = convert_percentage_to_decimal(str(row[f'wr_{i}']))
                    games = float(row[f'games_{i}']) if pd.notna(row[f'games_{i}']) else 0
                    kda = float(row[f'kda_ratio_{i}']) if pd.notna(row[f'kda_ratio_{i}']) else 0
                    cs_per_min = float(row[f'cpm_{i}']) if pd.notna(row[f'cpm_{i}']) else 0
                    
                    champion_scores['season_score'][idx] = (
                        wr * 0.4 +
                        (kda / 10) * 0.3 +
                        (cs_per_min / 10) * 0.3
                    ) * (games / 100)
            
            # 4. Mastery Score
            for i in range(1, 17):
                if row.get(f'mastery_champ_{i}') == champion:
                    mastery = float(row[f'm_lv_{i}']) if pd.notna(row[f'm_lv_{i}']) else 0
                    champion_scores['mastery_score'][idx] = mastery / 7
        
        # Calculate final weighted score
        feature_dict[champion] = (
            champion_scores['recent_score'] * weights['recent'] +
            champion_scores['weekly_score'] * weights['weekly'] +
            champion_scores['season_score'] * weights['season'] +
            champion_scores['mastery_score'] * weights['mastery']
        )
    
    # Add role preferences to feature dictionary
    role_cols = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
    for role in role_cols:
        feature_dict[f'role_pref_{role.lower()}'] = df[role]
    
    # Add role information to feature dictionary
    feature_dict.update({
        'primary_role': df['most_role_1'],
        'primary_role_value': df['most_role_1_value'],
        'secondary_role': df['most_role_2'],
        'secondary_role_value': df['most_role_2_value']
    })
    
    # Convert tier if available
    if 'tier' in df.columns:
        feature_dict['tier'] = df['tier'].apply(convert_tier_to_number)
    
    # Create DataFrame all at once using the feature dictionary
    features = pd.DataFrame(feature_dict)
    
    # Save to CSV
    output_file = os.path.join("util", "data", "champion_features.csv")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    features.to_csv(output_file, index=False)
    
    # Print summary
    print("\nFeature Engineering Summary:")
    print(f"Total champions processed: {len(converter.champions)}")
    print(f"Total features created: {len(features.columns)}")
    print(f"Total players processed: {len(features)}")
    
    # Print sample of feature values
    print("\nSample of champion scores (first 5 champions, first 3 players):")
    champion_cols = converter.champions[:5]
    print(features[['player_id'] + champion_cols].head(3))
    
    return features

if __name__ == "__main__":
    # Read the input data
    input_file = os.path.join("util", "data", "player_stats_merged.csv")
    df = pd.read_csv(input_file)
    
    # Create features
    features = create_champion_features(df)