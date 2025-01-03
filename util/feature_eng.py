import pandas as pd
import numpy as np
import os
from helper import ChampionConverter

def create_champion_features(merged_player_stats=None, meta_stats=None, debug=None):
    """
    Create features for champion prediction using player data.
    Champion names will be used as column headers.
    Uses pd.concat to avoid DataFrame fragmentation.
    Parameters:
    - merged_player_stats: DataFrame containing player stats. If None, it will be loaded from the input file.
    - meta_stats: DataFrame containing meta stats. If None, it will be loaded from the input file.
    - debug: Optional parameter for champion name to print debug information.
    """
    if merged_player_stats is None:
        input_file = os.path.join("util", "data", "player_stats_merged.csv")
        merged_player_stats = pd.read_csv(input_file)
    
    if meta_stats is None:
        meta_file = os.path.join("util", "data", "meta_stats.csv")
        meta_stats = pd.read_csv(meta_file)

    # Initialize the champion converter
    converter = ChampionConverter()

    # Get low tier champions and counter information
    tier_penalties = {3: 0.9, 4: 0.85, 5: 0.8}
    tier_map = meta_stats.set_index('champion')['tier'].to_dict()

    counter_map = {}
    for _, row in meta_stats.iterrows():
        if pd.notna(row['counter1']):
            champ = row['champion']
            counters = [row['counter1'], row['counter2'], row['counter3']]
            counter_map[champ] = [c for c in counters if pd.notna(c)]

    # Define importance weights
    weights = {
        'recent': 0.3,    # Last 20 games
        'weekly': 0.6,    # Last 7 days
        'season': 0.06,   # Current season
        'mastery': 0.04   # All-time mastery
    }

    # Move 'champion' column to the first position
    cols = ['champion'] + [col for col in merged_player_stats if col != 'champion']
    merged_player_stats = merged_player_stats[cols]

    # Initialize feature dictionary with existing DataFrame
    feature_dict = merged_player_stats.to_dict(orient='list')
    
    # For debug information
    debug_data = []

    # Process each champion to create new features
    for champion in converter.champions:
        # Initialize scores for this champion
        champion_scores = {
            'recent_score': np.zeros(len(merged_player_stats)),
            'weekly_score': np.zeros(len(merged_player_stats)),
            'season_score': np.zeros(len(merged_player_stats)),
            'mastery_score': np.zeros(len(merged_player_stats))
        }
        
        # Calculate scores for each player
        for idx, row in merged_player_stats.iterrows():
            # 1. Recent Performance
            for i in range(1, 4):
                if row.get(f'most_champ_{i}') == champion:
                    # Get base stats
                    wr = float(row[f'WR_{i}']) if pd.notna(row[f'WR_{i}']) else 0
                    kda = float(row[f'KDA_{i}']) if pd.notna(row[f'KDA_{i}']) else 0
                    wins = float(row[f'W_{i}']) if pd.notna(row[f'W_{i}']) else 0
                    losses = float(row[f'L_{i}']) if pd.notna(row[f'L_{i}']) else 0
                    games = wins + losses
                    total_games = float(row['total_games']) if pd.notna(row['total_games']) else 20
                    
                    # Calculate performance quality
                    performance_quality = (
                        (wr * 0.7) +           # Winrate contribution (70%)
                        (min(kda, 10) / 10 * 0.3)  # KDA contribution (30%), capped at 10
                    )
                    
                    # Calculate games quantity factor
                    games_factor = min(games / 5, 1.0)  # 5 games cap
                    games_ratio = games / total_games  # How much of total games on this champion
                    
                    # Adjust score based on performance trend
                    if games >= 5:  # Enough games to establish a trend
                        if performance_quality < 0.4:  # Poor performance
                            # Penalize more for consistent poor performance
                            performance_quality *= 0.8
                        elif performance_quality > 0.7:  # Excellent performance
                            # Reward consistent good performance
                            performance_quality *= 1.2
                    
                    # Final recent score combines quality and quantity
                    champion_scores['recent_score'][idx] = (
                        performance_quality * (0.7 + (0.3 * games_factor))  # Base score + games bonus
                    ) * (1 + games_ratio * 0.2)  # Small bonus for champion dedication
            
            # 2. Weekly Performance
            for i in range(1, 4):
                if row.get(f'7d_champ_{i}') == champion:
                    # Get weekly stats
                    weekly_wins = float(row[f'7d_W_{i}']) if pd.notna(row[f'7d_W_{i}']) else 0
                    weekly_losses = float(row[f'7d_L_{i}']) if pd.notna(row[f'7d_L_{i}']) else 0
                    weekly_games = float(row[f'7d_total_{i}']) if pd.notna(row[f'7d_total_{i}']) else 0
                    weekly_wr = float(row[f'7d_WR_{i}']) if pd.notna(row[f'7d_WR_{i}']) else 0
                    
                    # Compare with overall profile stats
                    profile_wr = float(row['win_rate']) if pd.notna(row['win_rate']) else 0.5
                    
                    # Calculate weekly performance quality
                    if weekly_games > 0:
                        # Win rate trend (compared to overall performance)
                        wr_trend = (weekly_wr - profile_wr) / profile_wr if profile_wr > 0 else 0
                        
                        # Games intensity (how much they played this champion in the week)
                        weekly_intensity = min(weekly_games / 10, 1.0)  # Cap at 10 games per week
                        
                        # Win streak factor (more recent wins are better)
                        win_ratio = weekly_wins / weekly_games if weekly_games > 0 else 0
                        
                        # Calculate weekly performance score
                        weekly_performance = (
                            (weekly_wr * 0.4) +                    # Base win rate (40%)
                            (max(min(wr_trend, 1), -1) * 0.2) +    # Win rate trend vs profile (20%)
                            (weekly_intensity * 0.2) +              # Games played factor (20%)
                            (win_ratio * 0.2)                       # Win ratio (20%)
                        )
                        
                        # Adjust score based on sample size
                        if weekly_games >= 5:  # Significant weekly sample
                            if weekly_performance < 0.4:  # Poor week
                                weekly_performance *= 0.8
                            elif weekly_performance > 0.7:  # Great week
                                weekly_performance *= 1.2
                        
                        # Calculate final weekly score
                        champion_scores['weekly_score'][idx] = weekly_performance * (
                            0.7 +  # Base weight
                            (0.3 * min(weekly_games / 5, 1.0))  # Games bonus (up to 30%)
                        )
            
            # 3. Season Performance
            for i in range(1, 8):
                if row.get(f'season_champ_{i}') == champion:
                    wr = float(row[f'wr_ssn_{i}']) if pd.notna(row[f'wr_ssn_{i}']) else 0
                    games = float(row[f'games_ssn_{i}']) if pd.notna(row[f'games_ssn_{i}']) else 0
                    kda = float(row[f'kda_ssn_{i}']) if pd.notna(row[f'kda_ssn_{i}']) else 0
                    
                    champion_scores['season_score'][idx] = (
                        wr * 0.7 +
                        (kda / 10) * 0.3 
                    ) * (games / 100)
            
            # 4. Mastery Score
            for i in range(1, 17):
                if row.get(f'mastery_champ_{i}') == champion:
                    mastery = float(row[f'm_lv_{i}']) if pd.notna(row[f'm_lv_{i}']) else 0
                    champion_scores['mastery_score'][idx] = mastery / 7
        
        # Calculate final weighted score
        base_score = (
            champion_scores['recent_score'] * weights['recent'] +
            champion_scores['weekly_score'] * weights['weekly'] +
            champion_scores['season_score'] * weights['season'] +
            champion_scores['mastery_score'] * weights['mastery']
        )

        # Apply tier penalties
        tier = tier_map.get(champion)
        if tier in tier_penalties:
            base_score *= tier_penalties[tier]  # Apply tier-specific penalty
            
        # Apply counter penalties - check all opponent champions
        for idx, row in merged_player_stats.iterrows():
            counter_penalty = 0
            # Check all opponent champions (opp_champ1 to opp_champ5)
            for i in range(1, 6):
                opp_col = f'opp_champ{i}'
                if opp_col in row and pd.notna(row[opp_col]):
                    opp_champ = row[opp_col]
                    if opp_champ in counter_map and champion in counter_map[opp_champ]:
                        counter_penalty += 0.1  # Stack small penalties for each counter

            if counter_penalty > 0:
                base_score[idx] -= min(counter_penalty, 0.3)  # Cap total counter penalty at 30%

        # Check team champions and opponent champions
        for idx, row in merged_player_stats.iterrows():
            teammates_champ_list = []
            opponent_champ_list = []
            for i in range(1, 5):
                team_col = f'team_champ{i}'
                if team_col in row:
                    teammates_champ_list.append(row[team_col])
                if row[team_col] == champion:
                    base_score[idx] = 0
            
            for i in range(1, 6):
                opp_col = f'opp_champ{i}'
                if opp_col in row:
                    opponent_champ_list.append(row[opp_col])
                if row[opp_col] == champion:
                    base_score[idx] = 0

            final_score = base_score[idx]
            final_score_actual = feature_dict[row['champion']][idx] if row['champion'] in feature_dict else final_score
            if debug == champion:
                debug_data.append({
                    'champion': row['champion'],
                    #'recent_score': champion_scores['recent_score'][idx],
                    #'weekly_score': champion_scores['weekly_score'][idx],
                    #'season_score': champion_scores['season_score'][idx],
                    #'mastery_score': champion_scores['mastery_score'][idx],
                    'base_score': base_score[idx],
                    'final_score': final_score,
                    'final_score_actual': final_score_actual,
                    'teammates_champ_list': teammates_champ_list,
                    'opponent_champ_list': opponent_champ_list
                })

        # Ensure no negative values
        feature_dict[champion] = np.maximum(base_score, 0.01)  # Small positive floor
    
    if debug:
        debug_df = pd.DataFrame(debug_data)
        print(debug_df)

    # Create DataFrame all at once using the feature dictionary
    features = pd.DataFrame(feature_dict)

    # Move the champion column to be the first column
    columns = ['champion'] + [col for col in features.columns if col != 'champion']
    features = features[columns]
    
    # Save to CSV
    output_file = os.path.join("util", "data", "champion_features.csv")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    features.to_csv(output_file, index=False)
    
    # # Print summary
    # print("\nFeature Engineering Summary:")
    # print(f"Total champions processed: {len(converter.champions)}")
    # print(f"Total features created: {len(features.columns)}")
    # print(f"Total players processed: {len(features)}")
    
    # # Print sample of feature values
    # print("\nSample of champion scores (first 5 champions, first 3 players):")
    # champion_cols = converter.champions[:5]
    # print(features[['player_id'] + champion_cols].head(3))
    
    return features

if __name__ == "__main__":
    # Create features
    features = create_champion_features(debug='Viktor')