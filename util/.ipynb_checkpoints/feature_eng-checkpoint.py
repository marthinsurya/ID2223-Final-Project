import os
import pandas as pd
import numpy as np
from helper import ChampionConverter, process_kda_perfect

def create_champion_features(merged_player_stats=None, meta_stats=None, weekly_meta=None, debug=None, consider_team_comp=True, test_mode=False):
    """
    Create features for champion prediction using player data.
    Champion names will be used as column headers.
    Uses pd.concat to avoid DataFrame fragmentation.
    """
    try:
        if merged_player_stats is None:
            print("Loading merged player stats...")
            input_file = os.path.join("util", "data", "player_stats_merged.csv")
            merged_player_stats = pd.read_csv(input_file, low_memory=False)
            
        #processing kda value
        merged_player_stats = process_kda_perfect(merged_player_stats)
   

        if test_mode:
            print("Test mode: Using only first 100 rows")
            merged_player_stats = merged_player_stats.head(100)
        
        if meta_stats is None:
            print("Loading meta stats...")
            meta_file = os.path.join("util", "data", "meta_stats.csv")
            meta_stats = pd.read_csv(meta_file, low_memory=False)

        if weekly_meta is None:
            print("Loading weekly meta stats...")
            weekly_file = os.path.join("util", "data", "weekly_meta_stats.csv")
            weekly_meta = pd.read_csv(weekly_file, low_memory=False)
        
        
        # Initialize variables
        debug_data = []
        original_columns = merged_player_stats.columns.tolist()
        feature_dict = {}

        # Copy original columns
        for col in merged_player_stats.columns:
            feature_dict[col] = merged_player_stats[col].values.copy()


        # Initialize the champion converter
        converter = ChampionConverter()
        all_champions = converter.champions
        #total_champions = len(converter.champions)
        
            

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

        # Move 'champion' column to the first position
        cols = ['champion'] + [col for col in merged_player_stats if col != 'champion']
        merged_player_stats = merged_player_stats[cols]

        # Define importance weights
        weights = {
            'recent': 0.3,    # Last 20 games
            'weekly': 0.4,    # Last 7 days
            'meta': 0.2,      # Only from weekly_stats
            'season': 0.06,   # Current season
            'mastery': 0.04   # All-time mastery
        }

        # Process rows in batches
        batch_size = 100
        total_rows = len(merged_player_stats)
        
        print(f"Total rows: {total_rows}")

        for batch_start in range(0, total_rows, batch_size):
            batch_end = min(batch_start + batch_size, total_rows)
            batch_rows = merged_player_stats.iloc[batch_start:batch_end]
            print(f"\nProcessing rows {batch_start} to {batch_end} ({batch_start/total_rows*100:.2f}% complete)")

            # Initialize batch scores dictionary
            batch_scores = {champion: np.zeros(len(batch_rows)) for champion in all_champions}
            
            # Process each row in this batch
            for batch_idx, (idx, row) in enumerate(batch_rows.iterrows()):
                # Process each champion for this row
                for champion in all_champions:
                    # Initialize scores for this champion and row
                    champion_scores = {
                        'recent_score': 0,
                        'weekly_score': 0,
                        'meta_score': 0,
                        'season_score': 0,
                        'mastery_score': 0
                    }

                    # Store debug info if needed
                    base_score_before_penalty = 0
                    counter_penalty = 0
                    counter_debug = []

                    # 1. Recent Performance
                    for i in range(1, 4):
                        if row.get(f'most_champ_{i}') == champion:
                            wr = float(row[f'WR_{i}']) if pd.notna(row[f'WR_{i}']) else 0
                            kda = float(row[f'KDA_{i}']) if pd.notna(row[f'KDA_{i}']) else 0
                            wins = float(row[f'W_{i}']) if pd.notna(row[f'W_{i}']) else 0
                            losses = float(row[f'L_{i}']) if pd.notna(row[f'L_{i}']) else 0
                            games = wins + losses
                            total_games = float(row['total_games']) if pd.notna(row['total_games']) else 20
                            
                            performance_quality = (
                                (wr * 0.7) +
                                (min(kda, 10) / 10 * 0.3)
                            )
                            
                            games_factor = min(games / 5, 1.0)
                            games_ratio = games / total_games
                            
                            if games >= 5:
                                if performance_quality < 0.4:
                                    performance_quality *= 0.8
                                elif performance_quality > 0.7:
                                    performance_quality *= 1.2
                            
                            champion_scores['recent_score'] = (
                                performance_quality * (0.7 + (0.3 * games_factor))
                            ) * (1 + games_ratio * 0.2)
                            break  # Exit loop once found
                    
                    # 2. Weekly Performance
                    for i in range(1, 4):
                        if row.get(f'7d_champ_{i}') == champion:
                            weekly_wins = float(row[f'7d_W_{i}']) if pd.notna(row[f'7d_W_{i}']) else 0
                            weekly_losses = float(row[f'7d_L_{i}']) if pd.notna(row[f'7d_L_{i}']) else 0
                            weekly_games = float(row[f'7d_total_{i}']) if pd.notna(row[f'7d_total_{i}']) else 0
                            weekly_wr = float(row[f'7d_WR_{i}']) if pd.notna(row[f'7d_WR_{i}']) else 0
                            profile_wr = float(row['win_rate']) if pd.notna(row['win_rate']) else 0.5
                            
                            if weekly_games > 0:
                                wr_trend = (weekly_wr - profile_wr) / profile_wr if profile_wr > 0 else 0
                                weekly_intensity = min(weekly_games / 10, 1.0)
                                win_ratio = weekly_wins / weekly_games if weekly_games > 0 else 0
                                
                                weekly_performance = (
                                    (weekly_wr * 0.4) +
                                    (max(min(wr_trend, 1), -1) * 0.2) +
                                    (weekly_intensity * 0.2) +
                                    (win_ratio * 0.2)
                                )
                                
                                if weekly_games >= 5:
                                    if weekly_performance < 0.4:
                                        weekly_performance *= 0.8
                                    elif weekly_performance > 0.7:
                                        weekly_performance *= 1.2
                                
                                champion_scores['weekly_score'] = weekly_performance * (
                                    0.7 + (0.3 * min(weekly_games / 5, 1.0))
                                )
                                break  # Exit loop once found

                    # 3. Meta Score
                    if champion in weekly_meta['champion'].values:
                        weekly_row = weekly_meta[weekly_meta['champion'] == champion].iloc[0]
                        rank = weekly_row['rank']
                        games = weekly_row['games']
                        pick_rate = weekly_row['pick']
                        ban_rate = weekly_row['ban']
                        
                        weight = (
                            1 / rank * 0.5 +
                            games / 100 * 0.3 +
                            pick_rate * 0.1 -
                            ban_rate * 0.1
                        )
                        
                        champion_scores['meta_score'] = weight

                    # 4. Season Performance
                    for i in range(1, 8):
                        if row.get(f'season_champ_{i}') == champion:
                            wr = float(row[f'wr_ssn_{i}']) if pd.notna(row[f'wr_ssn_{i}']) else 0
                            games = float(row[f'games_ssn_{i}']) if pd.notna(row[f'games_ssn_{i}']) else 0
                            kda = float(row[f'kda_ssn_{i}']) if pd.notna(row[f'kda_ssn_{i}']) else 0
                            
                            champion_scores['season_score'] = (
                                wr * 0.7 +
                                (kda / 10) * 0.3 
                            ) * (games / 100)
                            break  # Exit loop once found
                    
                    # 5. Mastery Score
                    for i in range(1, 17):
                        if row.get(f'mastery_champ_{i}') == champion:
                            mastery = float(row[f'm_lv_{i}']) if pd.notna(row[f'm_lv_{i}']) else 0            
                            champion_scores['mastery_score'] = mastery / 7
                            break  # Exit loop once found

                    # Calculate base score for this champion and row
                    base_score = (
                        champion_scores['recent_score'] * weights['recent'] +
                        champion_scores['weekly_score'] * weights['weekly'] +
                        champion_scores['meta_score'] * weights['meta'] +
                        champion_scores['season_score'] * weights['season'] +
                        champion_scores['mastery_score'] * weights['mastery']
                    )

                    
                    # Store the pre-penalty score for debugging
                    base_score_before_penalty = base_score

                    # Apply tier penalties
                    if champion in tier_map:
                        highest_tier = min(tier_map[champion])
                        if highest_tier in tier_penalties:
                            base_score *= tier_penalties[highest_tier]

                    # Process team composition and counter penalties
                    if consider_team_comp:
                        # Check team champions
                        for i in range(1, 5):
                            team_col = f'team_champ{i}'
                            if team_col in row and pd.notna(row[team_col]):
                                if row[team_col] == champion:
                                    base_score = 0
                                    break
                        
                        # Only check opponents if base_score isn't already 0
                        if base_score != 0:
                            counter_penalty = 0
                            counter_debug = []  # For debug information
                            
                            for i in range(1, 6):
                                opp_col = f'opp_champ{i}'
                                if opp_col in row and pd.notna(row[opp_col]):
                                    opp_champ = row[opp_col]
                                    if opp_champ == champion:
                                        base_score = 0
                                        break
                                    if champion in counter_map and opp_champ in counter_map[champion]:
                                        counter_penalty += 0.1
                                        counter_debug.append(opp_champ)
                            
                            if counter_penalty > 0:
                                base_score = base_score * (1 - counter_penalty)

                    # Store the final score for this champion and row
                    batch_scores[champion][batch_idx] = max(base_score, 0)

                    # Collect debug data if this is the debug champion
                    if debug == champion:
                        counter_list = []
                        for i in range(1, 6):
                            opp_col = f'opp_champ{i}'
                            if opp_col in row and pd.notna(row[opp_col]):
                                if champion in counter_map and row[opp_col] in counter_map[champion]:
                                    counter_list.append(row[opp_col])

                        debug_row = {
                            'champion': row['champion'],
                            'recent_score': champion_scores['recent_score'],
                            'weekly_score': champion_scores['weekly_score'],
                            'meta_score': champion_scores['meta_score'],
                            'base_score': base_score_before_penalty,
                            'final_score': base_score,
                            'counter_penalty': counter_penalty if consider_team_comp else 0,
                            'final_score_actual': feature_dict[row['champion']][idx] if row['champion'] in feature_dict else base_score,
                            'counter_list_debug': counter_list
                        }
                        debug_data.append(debug_row)

            # Update feature_dict with batch results
            for champion in batch_scores:
                if champion not in feature_dict:
                    feature_dict[champion] = np.zeros(total_rows)
                feature_dict[champion][batch_start:batch_end] = batch_scores[champion]

            # Save after each batch with timestamp
            temp_df = pd.DataFrame({
                **{col: feature_dict[col] for col in original_columns},  # Original columns first
                **{champion: feature_dict[champion] for champion in all_champions}  # Then champion columns
            })
            
            batch_save_file = os.path.join("util", "data", f"feature_eng_stats.csv")
            temp_df.to_csv(batch_save_file, index=False)
            print(f"Saved batch progress to {batch_save_file}")

            if debug:
                print(f"{debug} is countered by: {counter_map[debug]}")

        # Process debug data if any
        if debug:
            debug_df = pd.DataFrame(debug_data)
            print("\nDebug Data:")
            print(debug_df)

        # Create final DataFrame
        champion_features = pd.DataFrame(feature_dict)

        # Create the final DataFrame by combining original data with new features
        features = pd.concat([
            merged_player_stats[original_columns],  # Keep all original columns
            champion_features[[col for col in champion_features.columns if col not in original_columns]]  # Only new champion columns
        ], axis=1)

        # Move the champion column to be the first column
        if 'champion' in features.columns:
            columns = ['champion'] + [col for col in features.columns if col != 'champion']
            features = features[columns]
        
        # Save to CSV with current date in filename
        output_file = os.path.join("util", "data", f"feature_eng_stats.csv")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        features.to_csv(output_file, index=False)
        
        # Print confirmation message
        print(f"Saved features to {output_file}")
            
        return features

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        input_file = os.path.join("util", "data", f"player_stats_merged_2025-01-05.csv")              
        merged_stats = pd.read_csv(input_file)

        features = create_champion_features(
            merged_player_stats=merged_stats,
            debug='Viktor',
            consider_team_comp=True,
            test_mode=True
        )
        
        if features is not None:
            print("\nProcessing completed successfully!")
            print(f"Generated features for {len(features)} rows")
        else:
            print("\nProcessing failed or was interrupted.")
            
    except Exception as e:
        print(f"\nFatal error: {str(e)}")