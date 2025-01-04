import os
import pandas as pd
import numpy as np
from helper import ChampionConverter

def create_champion_features(merged_player_stats=None, meta_stats=None, weekly_meta=None, debug=None, consider_team_comp=True):
    """
    Create features for champion prediction using player data.
    Champion names will be used as column headers.
    Uses pd.concat to avoid DataFrame fragmentation.
    Parameters:
    - merged_player_stats: DataFrame containing player stats. If None, it will be loaded from the input file.
    - meta_stats: DataFrame containing meta stats. If None, it will be loaded from the input file.
    - weekly_stats: DataFrame containing weekly champion stats. If None, it will be loaded from the input file.
    - debug: Optional parameter for champion name to print debug information.
    """
    if merged_player_stats is None:
        input_file = os.path.join("util", "data", "player_stats_merged.csv")
        merged_player_stats = pd.read_csv(input_file)
    
    if meta_stats is None:
        meta_file = os.path.join("util", "data", "meta_stats.csv")
        meta_stats = pd.read_csv(meta_file)

    if weekly_meta is None:
        weekly_file = os.path.join("util", "data", "weekly_meta_stats.csv")
        weekly_stats = pd.read_csv(weekly_file)

    # Initialize the champion converter
    converter = ChampionConverter()

    # Get low tier champions and counter information
    tier_penalties = {3: 0.9, 4: 0.85, 5: 0.8}
    
    # Create tier_map as a dictionary of lists
    tier_map = {}
    for _, row in meta_stats.iterrows():
        champ = row['champion']
        tier = row['tier']
        if pd.notna(tier):
            if champ in tier_map:
                tier_map[champ].append(tier)
            else:
                tier_map[champ] = [tier]

    counter_map = {}
    for _, row in meta_stats.iterrows():
        if pd.notna(row['counter1']):
            champ = row['champion']
            counters = [row['counter1'], row['counter2'], row['counter3']]
            if champ in counter_map:
                counter_map[champ].extend([c for c in counters if pd.notna(c)])
            else:
                counter_map[champ] = [c for c in counters if pd.notna(c)]

    # Ensure unique counters and remove duplicates
    for champ, counters in counter_map.items():
        counter_map[champ] = list(set(counters))
    

    # Define importance weights
    weights = {
        'recent': 0.2,    # Last 20 games
        'weekly': 0.5,    # Last 7 days
        'meta': 0.2,      # Only from weekly_stats
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
            'meta_score': np.zeros(len(merged_player_stats)),
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

            # Add weekly stats weighting (meta score)
            if champion in weekly_stats['champion'].values:
                weekly_row = weekly_stats[weekly_stats['champion'] == champion].iloc[0]
                rank = weekly_row['rank']
                games = weekly_row['games']
                pick_rate = weekly_row['pick']
                ban_rate = weekly_row['ban']
                
                # Calculate weighted score for meta
                weight = (
                    1 / rank * 0.5 +  # Higher rank gives higher weight
                    games / 100 * 0.3 +  # More games give higher weight
                    pick_rate * 0.1 -  # Pick rate contributes positively
                    ban_rate * 0.1  # Ban rate contributes negatively
                )
                
                champion_scores['meta_score'][idx] = weight
            
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
            champion_scores['meta_score'] * weights['meta'] +
            champion_scores['season_score'] * weights['season'] +
            champion_scores['mastery_score'] * weights['mastery']
        )

        # Apply tier penalties
        if champion in tier_map:
            highest_tier = min(tier_map[champion])  # Get the highest tier (lowest number)
            if highest_tier in tier_penalties:
                base_score *= tier_penalties[highest_tier]  # Apply tier-specific penalty

        for idx, row in merged_player_stats.iterrows():
            base_score_before_penalty = base_score[idx]
            counter_penalty = 0
            counter_debug = []  

            # Process team composition and counters only if consider_team_comp is True
            if consider_team_comp:
                # Check team champions first
                for i in range(1, 5):
                    team_col = f'team_champ{i}'
                    if team_col in row and pd.notna(row[team_col]):
                        if row[team_col] == champion:
                            base_score[idx] = 0
                            break
                
                # If not already zeroed, check opponent champions
                if base_score[idx] != 0:
                    for i in range(1, 6):
                        opp_col = f'opp_champ{i}'
                        if opp_col in row and pd.notna(row[opp_col]):
                            opp_champ = row[opp_col]
                            # Check if champion is already picked
                            if opp_champ == champion:
                                base_score[idx] = 0
                                break
                            # Check for counters
                            if champion in counter_map and opp_champ in counter_map[champion]:
                                counter_penalty += 0.1
                                counter_debug.append(opp_champ)
                    
                    # Apply counter penalty if any
                    if counter_penalty > 0:
                        base_score[idx] = base_score[idx] * (1 - counter_penalty)
                        base_score[idx] = max(base_score[idx], 0)

            # Collect debug data regardless of consider_team_comp
            if debug == champion:
                # Get counter list for debug
                counter_list = []
                for i in range(1, 6):
                    opp_col = f'opp_champ{i}'
                    if opp_col in row and pd.notna(row[opp_col]):
                        if champion in counter_map and row[opp_col] in counter_map[champion]:
                            counter_list.append(row[opp_col])

                debug_row = {
                'champion': row['champion'],
                'recent_score': champion_scores['recent_score'][idx],
                'weekly_score': champion_scores['weekly_score'][idx],
                'base_score': base_score_before_penalty,
                'final_score': base_score[idx],
                'counter_penalty': counter_penalty if consider_team_comp else 0,
                'final_score_actual': feature_dict[row['champion']][idx] if row['champion'] in feature_dict else base_score[idx],
                'counter_list_debug': counter_list
                }
                debug_data.append(debug_row)

        if debug == champion and debug in counter_map:
            print(f"\n{debug} is countered by: {counter_map[debug]}")

        # Ensure no negative values
        feature_dict[champion] = np.maximum(base_score, 0)  # Minimum value is 0.0

    if debug:
        debug_df = pd.DataFrame(debug_data)
        print("\nDebug Data:")
        print(debug_df)

    # Create DataFrame all at once using the feature dictionary
    features = pd.DataFrame(feature_dict)

    # Move the champion column to be the first column
    columns = ['champion'] + [col for col in features.columns if col != 'champion']
    features = features[columns]
    
    # Save to CSV
    output_file = os.path.join("util", "data", "feature_eng_stats.csv")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    features.to_csv(output_file, index=False)
    
    # Print confirmation message
    print(f"Saved features to {output_file}")
    
    return features

if __name__ == "__main__":
    # Create features
    features = create_champion_features(debug='Viktor', consider_team_comp=True)