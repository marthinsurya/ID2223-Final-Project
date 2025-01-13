import pandas as pd
from datetime import datetime
import os
import numpy as np
from urllib.parse import quote, unquote

class ChampionConverter:
    def __init__(self):
        self.champions = [
            "Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Ambessa", "Amumu", "Anivia", "Annie", "Aphelios", "Ashe", "Aurelion Sol",
            "Aurora", "Azir", "Bard", "Bel'Veth", "Blitzcrank", "Brand", "Braum", "Briar", "Caitlyn", "Camille", "Cassiopeia", "Cho'Gath",
            "Corki", "Darius", "Diana", "Dr. Mundo", "Draven", "Ekko", "Elise", "Evelynn", "Ezreal", "Fiddlesticks", "Fiora", "Fizz", "Galio",
            "Gangplank", "Garen", "Gnar", "Gragas", "Graves", "Gwen", "Hecarim", "Heimerdinger", "Hwei", "Illaoi", "Irelia", "Ivern", "Janna",
            "Jarvan IV", "Jax", "Jayce", "Jhin", "Jinx", "K'Sante", "Kai'Sa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina", "Kayle",
            "Kayn", "Kennen", "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee Sin", "Leona", "Lillia", "Lissandra", "Lucian", "Lulu",
            "Lux", "Malphite", "Malzahar", "Maokai", "Master Yi", "Milio", "Miss Fortune", "Mordekaiser", "Morgana", "Naafiri", "Nami", "Nasus",
            "Nautilus", "Neeko", "Nidalee", "Nilah", "Nocturne", "Nunu & Willump", "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke",
            "Qiyana", "Quinn", "Rakan", "Rammus", "Rek'Sai", "Rell", "Renata Glasc", "Renekton", "Rengar", "Riven", "Rumble", "Ryze", "Samira",
            "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir", "Skarner", "Smolder", "Sona",
            "Soraka", "Swain", "Sylas", "Syndra", "Tahm Kench", "Taliyah", "Talon", "Taric", "Teemo", "Thresh", "Tristana", "Trundle",
            "Tryndamere", "Twisted Fate", "Twitch", "Udyr", "Urgot", "Varus", "Vayne", "Veigar", "Vel'Koz", "Vex", "Vi", "Viego", "Viktor",
            "Vladimir", "Volibear", "Warwick", "Wukong", "Xayah", "Xerath", "Xin Zhao", "Yasuo", "Yone", "Yorick", "Yuumi", "Zac", "Zed",
            "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra"
        ]

        self.champion_to_number = {champion: i for i, champion in enumerate(self.champions, start=1)}
        self.number_to_champion = {i: champion for i, champion in enumerate(self.champions, start=1)}

    def champion_to_num(self, champion_name):
        return self.champion_to_number.get(champion_name, None)

    def num_to_champion(self, number):
        return self.number_to_champion.get(number, None)
    
def convert_date(date_str):
    """Convert datetime string to Unix timestamp"""
    try:
        if pd.isna(date_str):
            return None
        return pd.to_datetime(date_str).timestamp()
    except:
        return None
    

def convert_to_minutes(time_str):
    """Convert time string (e.g., '15m 10s') to minutes (float)"""
    try:
        minutes = seconds = 0
        parts = time_str.lower().split()
        for part in parts:
            if 'm' in part:
                minutes = float(part.replace('m', ''))
            elif 's' in part:
                seconds = float(part.replace('s', ''))
        return round(minutes + seconds/60, 2)
    except:
        return 0.0
    
def convert_percentage_to_decimal(percentage_str):
    """Convert percentage string (e.g., 'P/Kill 43%') to decimal (0.43)"""
    try:
        # Extract number from string and convert to decimal
        num = float(''.join(filter(str.isdigit, percentage_str))) / 100
        return round(num, 2)
    except:
        return 0.0
    
def convert_tier_to_number(tier_str):
    """
    Convert tier string to number:
    Challenger -> 1
    Grandmaster -> 2
    Master -> 3
    Others -> 4
    """
    tier_map = {
        'challenger': 1,
        'grandmaster': 2,
        'master': 3
    }
    # Convert to lowercase and return mapped value or 4 for any other tier
    return tier_map.get(tier_str.lower().strip(), 4)

def convert_result_to_binary(result_str):
    """
    Convert match result to binary:
    Victory -> 1
    Defeat -> 0
    """
    return 1 if result_str.lower().strip() == 'victory' else 0

def merge_stats(recent_stats, player_stats, current_time =None):
    """
    Merge recent match stats with player profile stats and save to CSV.
    Only keeps rows where matches exist in both DataFrames.
    
    Args:
        recent_stats (DataFrame/dict): Recent match statistics
        player_stats (DataFrame/tuple): Player profile statistics
        
    Returns:
        DataFrame: Combined statistics
    """
    try:
        if current_time is None:
            current_time = datetime.utcnow().strftime("%Y-%m-%d")

        # Convert recent_stats to DataFrame if it's not already
        if not isinstance(recent_stats, pd.DataFrame):
            recent_df = pd.DataFrame(recent_stats)
        else:
            recent_df = recent_stats
        
        # Handle player_stats based on its type
        if isinstance(player_stats, tuple):
            # If it's a tuple (merged_df, dfs), use the merged_df
            player_df = player_stats[0]
        elif isinstance(player_stats, pd.DataFrame):
            player_df = player_stats
        else:
            raise ValueError("Invalid player_stats format")

        # Ensure player_id exists in both DataFrames
        if 'player_id' not in recent_df.columns:
            recent_df['player_id'] = player_df['player_id'].iloc[0]

        # Print info before merge
        print(f"\nBefore merge:")
        print(f"Recent stats rows: {len(recent_df)}")
        print(f"Player stats rows: {len(player_df)}")
        print(f"Unique players in recent stats: {recent_df['player_id'].nunique()}")
        print(f"Unique players in player stats: {player_df['player_id'].nunique()}")

        # Merge DataFrames with inner join
        merged_df = pd.merge(
            recent_df,
            player_df,
            on='player_id',
            how='inner',  # Changed from 'left' to 'inner'
            suffixes=('', '_profile')
        )

        # Print info after merge
        print(f"\nAfter merge:")
        print(f"Merged stats rows: {len(merged_df)}")
        print(f"Unique players in merged stats: {merged_df['player_id'].nunique()}")

        # Reorder columns to ensure player_id and region are first
        cols = merged_df.columns.tolist()
        cols = ['player_id'] + [col for col in cols if col != 'player_id']
        if 'region' in cols:
            cols.remove('region')
            cols.insert(1, 'region')
        merged_df = merged_df[cols]

        # Create directory if it doesn't exist
        save_dir = "util/data"
        os.makedirs(save_dir, exist_ok=True)

        # Save to CSV
        filename = f"player_stats_merged_{current_time}.csv"
        filepath = os.path.join(save_dir, filename)
        merged_df.to_csv(filepath, index=False)
        print(f"\nSuccessfully saved merged stats to {filepath}")

        return merged_df

    except Exception as e:
        print(f"Error in merge_stats: {e}")
        return None
    

def filter_leaderboard(df, tiers=None):
    """
    Filter leaderboard DataFrame to keep only specific tiers.
    
    Args:
        df (pandas.DataFrame): Input leaderboard DataFrame
        tiers (list): List of tiers to keep. Defaults to ["CHALLENGER", "GRANDMASTER"]
        timestamp (str): Current timestamp in UTC
        scraper_user (str): Current user's login
    
    Returns:
        pandas.DataFrame: Filtered leaderboard data
    """
    try:
        # Set default tiers if none provided
        if tiers is None:
            tiers = ["CHALLENGER", "GRANDMASTER"]
        
        # Convert tiers to uppercase for consistency
        tiers = [tier.upper() for tier in tiers]
        
        # Validate input DataFrame
        required_cols = ["tier", "summoner", "region"]
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")
        
        # Create copy to avoid modifying original DataFrame
        filtered_df = df.copy()
        
        # Convert tier column to uppercase for consistent filtering
        filtered_df['tier'] = filtered_df['tier'].str.upper()
        
        # Filter by specified tiers
        filtered_df = filtered_df[filtered_df['tier'].isin(tiers)]
        
        
        # Sort by region and tier
        filtered_df = filtered_df.sort_values(['region', 'tier', 'rank'])
        
        # Reset index
        filtered_df = filtered_df.reset_index(drop=True)
        
        # Save to CSV
        output_file = os.path.join("util", "data", "lb_filtered.csv")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        filtered_df.to_csv(output_file, index=False)
        
        print(f"\nFiltered leaderboard to {len(tiers)} tiers: {', '.join(tiers)}")
        print(f"Remaining entries: {len(filtered_df)}")
        print(f"Saved filtered leaderboard to {output_file}")
        
        # Print summary statistics
        print("\nSummary by region and tier:")
        summary = filtered_df.groupby(['region', 'tier']).size().unstack(fill_value=0)
        print(summary)
        
        return filtered_df
        
    except Exception as e:
        print(f"Error filtering leaderboard: {e}")
        return None

def format_summoner_name(summoner):
    """
    Format summoner name for URL usage
    
    Parameters:
    summoner: str - Original summoner name
    
    Returns:
    str - Formatted summoner name
    """
    if not summoner:
        raise ValueError("Summoner name cannot be empty")
        
    # Remove leading/trailing whitespace
    summoner = summoner.strip()
    
    # Replace spaces and special characters
    formatted_summoner = summoner.replace(" ", "-").replace("#", "-")
    
    # Handle other special characters through URL encoding
    formatted_summoner = quote(formatted_summoner)
    
    return formatted_summoner

def convert_to_displayname(name):
    """
    Convert a summoner name to display format
    Examples:
    marthinsurya-NA -> marthinsurya #NA
    toplane%20kid-EUW77 -> toplane kid #EUW77
    Walid-Georgey-EUW -> Walid Georgey #EUW
    Current%20User-KR -> Current User #KR
    """
    try:
        if not name:
            return ""
            
        # First decode URL encoding
        decoded = unquote(name)
        
        # Remove any trailing hyphens
        decoded = decoded.rstrip('-')
        
        # Split by last hyphen to separate name and region
        if '-' in decoded:
            parts = decoded.rsplit('-', 1)
            base_name = parts[0]  # Everything before last hyphen
            region = parts[1]
            
            # Replace remaining hyphens in base_name with spaces
            base_name = base_name.replace('-', ' ')
            
            # Clean up any double spaces
            base_name = ' '.join(filter(None, base_name.split()))
            
            return f"{base_name} #{region}"
        
        return decoded.replace('-', ' ')
    except Exception as e:
        print(f"Error converting name '{name}': {e}")
        return name



def get_player_list(leaderboard=None):
    """
    Convert leaderboard data into proper player list format for API calls.
    
    Args:
        leaderboard (DataFrame): Input leaderboard DataFrame containing summoner and region
    
    Returns:
        DataFrame: Formatted player list with region and username columns
    """
    try:
        
        if leaderboard is None:
            leaderboard_file = os.path.join("util", "data", "lb_filtered.csv")
            leaderboard = pd.read_csv(leaderboard_file)
            
        # Rename summoner column to username
        leaderboard = leaderboard.rename(columns={'summoner': 'username'})
        
        # Select only region and username columns in correct order
        player_list = leaderboard[['region', 'username']]
        
        print(f"Successfully processed {len(player_list)} players")
        return player_list
        
    except Exception as e:
        print(f"Error processing leaderboard: {e}")
        return None

def process_kda_perfect(df):
    """
    Process KDA values in the DataFrame, replacing 'Perfect' with appropriate values.
    """
    try:
        # Create a copy to avoid modifying the original dataframe
        df = df.copy()
        
        # Function to safely convert to numeric
        def safe_convert(x):
            if isinstance(x, (int, float)):
                return x
            if isinstance(x, str) and x.lower() == 'perfect':
                return 6
            try:
                return float(x)
            except:
                return None

        # 1. Process KDA_1, KDA_2, KDA_3
        for col in ['KDA_1', 'KDA_2', 'KDA_3']:
            if col in df.columns:
                df[col] = df[col].apply(safe_convert)

        # 2. Process kda_ssn_1 to kda_ssn_7
        for i in range(1, 8):
            col = f'kda_ssn_{i}'
            if col in df.columns:
                perfect_mask = df[col].astype(str).str.contains('perfect', case=False)
                if perfect_mask.any():
                    kills_col, assists_col = f'k_ssn_{i}', f'a_ssn_{i}'
                    if kills_col in df.columns and assists_col in df.columns:
                        df.loc[perfect_mask, col] = df.loc[perfect_mask].apply(
                            lambda row: pd.to_numeric(row[kills_col], errors='coerce') + 
                                      pd.to_numeric(row[assists_col], errors='coerce'), 
                            axis=1
                        )
                    else:
                        df.loc[perfect_mask, col] = 6
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. Process kda_ratio_profile
        if 'kda_ratio_profile' in df.columns:
            perfect_mask = df['kda_ratio_profile'].astype(str).str.contains('perfect', case=False)
            if perfect_mask.any():
                df.loc[perfect_mask, 'kda_ratio_profile'] = df.loc[perfect_mask].apply(
                    lambda row: pd.to_numeric(row['avg_kills'], errors='coerce') + 
                              pd.to_numeric(row['avg_assists'], errors='coerce'),
                    axis=1
                )
            df['kda_ratio_profile'] = pd.to_numeric(df['kda_ratio_profile'], errors='coerce')

        # 4. Process remaining kda_ratio columns
        other_cols = [col for col in df.columns if 'kda_ratio' in col.lower() 
                     and col != 'kda_ratio_profile' 
                     and col not in [f'kda_ssn_{i}' for i in range(1, 8)]]
        
        for col in other_cols:
            perfect_mask = df[col].astype(str).str.contains('perfect', case=False)
            if perfect_mask.any():
                prefix = col.split('kda_ratio')[0]
                kills_col, assists_col = f"{prefix}kills", f"{prefix}assists"
                if kills_col in df.columns and assists_col in df.columns:
                    df.loc[perfect_mask, col] = df.loc[perfect_mask].apply(
                        lambda row: pd.to_numeric(row[kills_col], errors='coerce') + 
                                  pd.to_numeric(row[assists_col], errors='coerce'),
                        axis=1
                    )
                else:
                    df.loc[perfect_mask, col] = 6
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    except Exception as e:
        print(f"Error in process_kda_perfect: {str(e)}")
        return df


def check_mixed_types(df):
    """
    Check and print dataframe column types, inconsistencies, and basic statistics
    """
    # Get type information
    dtype_info = pd.DataFrame({
        'dtype': df.dtypes,
        'non_null': df.count(),
        'null_count': df.isnull().sum(),
        'unique_values': [df[col].nunique() for col in df.columns]
    })
    
    # Add sample of unique values for each column
    dtype_info['sample_values'] = [df[col].dropna().sample(min(3, len(df[col].dropna()))).tolist() 
                                 if len(df[col].dropna()) > 0 else [] 
                                 for col in df.columns]
    
    # Check for mixed types in object columns
    mixed_type_cols = []
    for col in df.select_dtypes(include=['object']):
        types = df[col].apply(type).unique()
        if len(types) > 1:
            mixed_type_cols.append({
                'column': col,
                'types': [t.__name__ for t in types],
                'samples': df[col].dropna().sample(min(3, len(df[col].dropna()))).tolist()
            })
    
    print("=== DataFrame Overview ===")
    print(f"Shape: {df.shape}")
    print("\n=== Data Types Summary ===")
    print(df.dtypes.value_counts())
    
    if mixed_type_cols:
        print("\n=== Mixed Type Columns ===")
        for col_info in mixed_type_cols:
            print(f"\nColumn: {col_info['column']}")
            print(f"Types found: {col_info['types']}")
            print(f"Sample values: {col_info['samples']}")
    
    return dtype_info

def check_nan_float(df, column_name):
    float_mask = df[column_name].apply(lambda x: isinstance(x, float))
    is_nan_mask = df[column_name].isna()

    # Check if all float values are NaN
    all_floats_are_nan = (float_mask == is_nan_mask).all()
    print(f"Are all float values NaN? {all_floats_are_nan}")

    # Double check by comparing counts
    print(f"Number of float values: {float_mask.sum()}")
    print(f"Number of NaN values: {is_nan_mask.sum()}")

def convert_team_colors(df):
    """
    Convert 'team' column values from 'blue'/'red' to 1/2
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame with 'team' column
    
    Returns:
    pandas.DataFrame: DataFrame with converted team values
    """
    df = df.copy()
    
    if 'team' not in df.columns:
        raise ValueError("Column 'team' not found in DataFrame")
    
    # Create mapping dictionary
    team_mapping = {
        'blue': 1,
        'red': 2
    }
    
    # Convert team colors to numbers
    df['team'] = df['team'].map(team_mapping, na_action='ignore')
    
    return df

def convert_region(df):
    """
    Convert 'region' column values to numeric:
    kr -> 1
    euw -> 2
    vn -> 3
    na -> 4
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame with 'region' column
    
    Returns:
    pandas.DataFrame: DataFrame with converted region values
    """
    df = df.copy()
    
    if 'region' not in df.columns:
        raise ValueError("Column 'region' not found in DataFrame")
    
    # Create mapping dictionary
    region_mapping = {
        'kr': 1,
        'euw': 2,
        'vn': 3,
        'na': 4
    }
    
    # Convert regions to numbers, keeping NA as NA
    df['region'] = df['region'].map(region_mapping, na_action='ignore')
    
    return df

def convert_champion_columns(df):
    """
    Convert all champion-related columns to numbers using ChampionConverter
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame
    
    Returns:
    pandas.DataFrame: DataFrame with converted champion values
    """
    df = df.copy()
    
    # Initialize champion converter
    converter = ChampionConverter()
    
    # Get all champion-related columns
    champion_columns = [col for col in df.columns if 'champ' in col.lower()]
    
    for col in champion_columns:       
        # Convert champion names to numbers
        df[col] = df[col].map(converter.champion_to_num, na_action='ignore')
    
    return df

def convert_date_column(df):
    """
    Convert date column from string format to Unix timestamp
    Handles missing values (NaT, None, NaN)
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame with 'date' column
    
    Returns:
    pandas.DataFrame: DataFrame with converted date values
    """
    df = df.copy()
    
    if 'date' not in df.columns:
        raise ValueError("Column 'date' not found in DataFrame")
    
    # Convert dates to timestamps
    df['date'] = df['date'].apply(convert_date)
    
    return df

def convert_role_columns(df):
    """
    Convert role columns to numbers:
    TOP -> 1, MID -> 2, ADC -> 3, JUNGLE -> 4, SUPPORT -> 5
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame
    
    Returns:
    pandas.DataFrame: DataFrame with converted role values
    """
    df = df.copy()
    
    # Define role mapping
    role_mapping = {
        'TOP': 1,
        'MID': 2,
        'ADC': 3,
        'JUNGLE': 4,
        'SUPPORT': 5
    }
    
    # Role columns to convert
    role_columns = ['most_role_1', 'most_role_2']
    
    
    for col in role_columns:
        if col in df.columns:       
            # Convert roles to numbers
            df[col] = df[col].map(role_mapping, na_action='ignore')
            
        else:
            print(f"Warning: Column {col} not found in DataFrame")
    
    return df

def convert_id_columns(df):
    """
    Drop ID-related columns (player_id, teammates1-4, oppmates1-5)
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame
    
    Returns:
    pandas.DataFrame: DataFrame with ID columns dropped
    """
    df = df.copy()
    
    # Specific ID columns to drop
    id_columns = (
        ['player_id', 'region_profile'] + 
        [f'teammates{i}' for i in range(1, 5)] +  # teammates1 to teammates4
        [f'oppmates{i}' for i in range(1, 6)]     # oppmates1 to oppmates5
    )
    
    
    # Verify columns exist and drop them
    existing_columns = [col for col in id_columns if col in df.columns]
    if len(existing_columns) != len(id_columns):
        missing = set(id_columns) - set(existing_columns)
        print(f"Note: Some columns were not found in DataFrame: {missing}")
    
    # Drop the columns
    df = df.drop(columns=existing_columns)
    
    return df

def remove_match_stats(df):
    """
    Remove match-specific statistics to prevent future data leakage.
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame
    
    Returns:
    pandas.DataFrame: DataFrame with match-specific columns removed
    """
    # List of columns that contain match-specific information
    match_stat_columns = [
        'level',            # Champion level
        'result',           # Match outcome (target variable)
        'match_length_mins',# Match duration
        'kill',            # Kills in the match
        'death',           # Deaths in the match
        'assist',          # Assists in the match
        'kda_ratio',       # KDA ratio for the match
        'kill_participation',# Kill participation in the match
        'laning',          # Laning phase performance
        'cs',              # Creep score in the match
        'cs_per_min'       # CS per minute in the match
    ]
    
    # Create a copy of the dataframe
    df_clean = df.copy()
    
    # Remove match-specific columns
    columns_to_drop = [col for col in match_stat_columns if col in df_clean.columns]
    df_clean = df_clean.drop(columns=columns_to_drop)
    
    return df_clean

def convert_df(df):
    """
    Master function to handle all conversions for training DataFrame
    
    Includes:
    - Team color conversion (blue/red to 1/2)
    - Region conversion (kr/euw/vn/na to 1/2/3/4)
    - Champion conversion (champion names to numbers)
    - Date conversion (string to Unix timestamp)
    - Role conversion (TOP/MID/ADC/JUNGLE/SUPPORT to 1/2/3/4/5)
    - Drop ID columns (player_id, teammates1-4, oppmates1-5, region_profile)
    
    Parameters:
    df (pandas.DataFrame): Input training DataFrame
    
    Returns:
    pandas.DataFrame: Processed DataFrame with all conversions
    """
    df = df.copy()
    
    # Drop rows where champion is NA
    initial_rows = len(df)
    df = df.dropna(subset=['champion'])
    rows_dropped = initial_rows - len(df)
    print(f"Dropped {rows_dropped} rows with NA champion values")

    # Sequential conversions
    conversions = [
        convert_team_colors,      # Convert blue/red to 1/2
        convert_region,          # Convert kr/euw/vn/na to 1/2/3/4
        convert_champion_columns, # Convert champion names to numbers
        convert_date_column,     # Convert dates to timestamps
        convert_role_columns,    # Convert roles to 1-5
        convert_id_columns,       # Drop ID-related columns
        remove_match_stats        # Remove match-specific columns
    ]
    
    ## Apply each conversion function in sequence
    for convert_func in conversions:
        try:
            print(f"Applying {convert_func.__name__}...")
            df = convert_func(df)
        except Exception as e:
            print(f"Error in {convert_func.__name__}: {str(e)}")
            raise
    
    return df


def get_top_champion_scores(df, n=5):
    """
    Get top n champion scores from a DataFrame
    
    Parameters:
    df: pandas DataFrame containing champion scores
    n: number of top champions to return (default 5)
    
    Returns:
    pandas DataFrame with original data plus top n champion scores and their names
    """
    try:
        converter = ChampionConverter()
        df = df.copy()
        
        # Get all champion columns (from Aatrox to Zyra)
        champion_start = df.columns.get_loc('Aatrox')
        champion_end = df.columns.get_loc('Zyra') + 1
        champion_cols = df.columns[champion_start:champion_end]
        
        # Convert scores to numeric, replacing non-numeric values with 0
        champion_scores = df[champion_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # Get indices of top n values for each row
        top_n_indices = champion_scores.apply(lambda x: pd.Series(x.nlargest(n).index), axis=1)
        top_n_values = champion_scores.apply(lambda x: pd.Series(x.nlargest(n).values), axis=1)
        
        # Create new columns for champion names and scores
        for i in range(n):
            # Champion scores
            df[f'{i+1}_champ_score'] = top_n_values.iloc[:, i].astype(float)
            
            # Champion names (converted to numbers)
            champ_names = top_n_indices.iloc[:, i]
            df[f'{i+1}_champ_name'] = champ_names.map(
                lambda x: int(converter.champion_to_num(x)) if pd.notnull(x) else -1
            )
        
        return df
    
    except Exception as e:
        print(f"Error in get_top_champion_scores: {str(e)}")
        # Return original DataFrame with default values in case of error
        for i in range(1, n + 1):
            df[f'{i}_champ_score'] = 0.0
            df[f'{i}_champ_name'] = -1
        return df
    
def check_datatypes(df):
    datatype= pd.DataFrame({
        'dtype': df.dtypes,
        'unique_values': df.nunique()
    })

    print(datatype)
    return datatype

def calculate_champ_variety_score(df):
    df = df.copy()  # Create a copy to avoid warnings
    
    # Create a list of champion columns we want to check
    champ_columns = [
        'most_champ_1', 'most_champ_2', 'most_champ_3',
        '7d_champ_1', '7d_champ_2', '7d_champ_3'
    ]
    
    # Filter to only include columns that exist in the DataFrame
    existing_columns = [col for col in champ_columns if col in df.columns]
    
    # Function to count unique non-NaN values
    def count_unique_champions(row):
        # Get all values that are not NaN
        valid_champions = row[existing_columns].dropna()
        # Count unique values
        return len(set(valid_champions))
    
    # Calculate the score for each row
    df['champ_variety_score'] = df.apply(count_unique_champions, axis=1)
    
    return df

def calculate_playstyle(df):
    df = df.copy()
    
    # Playstyle categorization (0-5)
    conditions = [
        # 0: Assassin/Carry (high kills, high KDA, high kill participation)
        (df['avg_kills'] > df['avg_assists']) & 
        (df['kda_ratio_profile'] > 3) & 
        (df['kill_participation_profile'] > 0.6),
        
        # 1: Support/Utility (high assists, good KDA, high kill participation)
        (df['avg_assists'] > df['avg_kills']) & 
        (df['kda_ratio_profile'] > 2.5) & 
        (df['kill_participation_profile'] > 0.55),
        
        # 2: Tank/Initiator (moderate deaths, high assists, high kill participation)
        (df['avg_deaths'] > 3) & 
        (df['avg_assists'] > df['avg_kills']) & 
        (df['kill_participation_profile'] > 0.5),
        
        # 3: Split-pusher (lower kill participation, good KDA)
        (df['kill_participation_profile'] < 0.5) & 
        (df['kda_ratio_profile'] > 2),
        
        # 4: Aggressive/Fighter (high kills and deaths, high kill participation)
        (df['avg_kills'] > 3) & 
        (df['avg_deaths'] > 4) & 
        (df['kill_participation_profile'] > 0.55)
    ]
    
    values = [0, 1, 2, 3, 4]  # Numeric values for each playstyle
    df['playstyle'] = np.select(conditions, values, default=5)
    
    return df

def get_most_role_3(df):
    df = df.copy()
    
    # Role mapping
    role_mapping = {
        'TOP': 1,
        'MID': 2,
        'ADC': 3,
        'JUNGLE': 4,
        'SUPPORT': 5
    }
    
    def get_third_role_info(row):
        # Create dictionary of role values excluding most_role_1 and most_role_2
        role_values = {
            'TOP': row['TOP'],
            'JUNGLE': row['JUNGLE'],
            'MID': row['MID'],
            'ADC': row['ADC'],
            'SUPPORT': row['SUPPORT']
        }
        
        # Remove most_role_1 and most_role_2 from consideration
        role_values.pop(row['most_role_1'], None)
        role_values.pop(row['most_role_2'], None)
        
        # Find highest remaining role and its value
        if role_values:
            third_role, third_value = max(role_values.items(), key=lambda x: x[1])
            return role_mapping[third_role], third_value
        return 0, 0.0  # Default values if no third role found

    # Add both most_role_3 and most_role_3_value
    df[['most_role_3', 'most_role_3_value']] = df.apply(get_third_role_info, axis=1, result_type='expand')
    
    return df

def calculate_role_specialization(df):
    df = df.copy()
    
    # Define conditions for role specialization
    conditions = [
        # 0: Pure Specialist (one dominant role)
        (df['most_role_1_value'] > 0.6),
        
        # 1: Strong Dual Role (two significant roles)
        (df['most_role_1_value'] <= 0.6) & 
        (df['most_role_2_value'] >= 0.3),
        
        # 2: Primary Role with Backups (moderate first role, has backups)
        (df['most_role_1_value'] <= 0.6) & 
        (df['most_role_2_value'] < 0.3) &
        (df['most_role_1_value'] > 0.3) &
        (df['most_role_3_value'] > 0.1),  # Has a viable third role
        
        # 3: Role Swapper (moderate first role, low others)
        (df['most_role_1_value'] <= 0.6) & 
        (df['most_role_2_value'] < 0.3) &
        (df['most_role_1_value'] > 0.3) &
        (df['most_role_3_value'] <= 0.1),  # No viable third role
        
        # 4: True Flex (plays multiple roles evenly)
        (df['most_role_1_value'] <= 0.3) & 
        (df['most_role_1_value'] > 0) &
        (df['most_role_3_value'] >= 0.15)  # Significant third role
    ]
    
    # 5 will be No Preference/Undefined (very low values or missing data)
    values = [0, 1, 2, 3, 4]  # Numeric values for each category
    df['role_specialization'] = np.select(conditions, values, default=5)
    
    return df

def calculate_champion_loyalty(df):
    df = df.copy()
    
    def get_loyalty_scores(row):
        try:
            # Get champions lists, handle potential NaN/None values (only top 2)
            recent_champs = [
                row['most_champ_1'] if pd.notna(row['most_champ_1']) else None,
                row['most_champ_2'] if pd.notna(row['most_champ_2']) else None
            ]
            
            # Include all 7 season champions
            season_champs = []
            season_games = []
            for i in range(1, 8):
                champ = row[f'season_champ_{i}'] if pd.notna(row[f'season_champ_{i}']) else None
                games = row[f'games_ssn_{i}'] if pd.notna(row[f'games_ssn_{i}']) else 0
                if champ is not None:
                    season_champs.append(champ)
                    season_games.append(games)
            
            # Add individual champion loyalty flags (only top 2)
            champ_loyalty_flags = {
                'recent_champ_1_loyal': 1 if (pd.notna(row['most_champ_1']) and 
                                            row['most_champ_1'] in season_champs) else 0,
                'recent_champ_2_loyal': 1 if (pd.notna(row['most_champ_2']) and 
                                            row['most_champ_2'] in season_champs) else 0
            }
            
            # Remove None values from recent champions
            recent_champs = [c for c in recent_champs if c is not None]
            
            # If no valid champions, return defaults
            if not recent_champs or not season_champs:
                return {
                    'loyalty_score': 0,
                    'confidence_score': 0,
                    **champ_loyalty_flags
                }
            
            # Calculate games played for recent champions (only top 2)
            recent_games = [
                (row['W_1'] + row['L_1']) if pd.notna(row['most_champ_1']) else 0,
                (row['W_2'] + row['L_2']) if pd.notna(row['most_champ_2']) else 0
            ]
            
            total_recent_games = sum(recent_games)
            total_season_games = sum(season_games)
            
            if total_recent_games == 0:
                return {
                    'loyalty_score': 0,
                    'confidence_score': 0,
                    **champ_loyalty_flags
                }
                
            # Calculate overlap score with enhanced weights
            loyalty_score = 0
            for idx, champ in enumerate(recent_champs):
                if champ in season_champs:
                    season_idx = season_champs.index(champ)
                    
                    recent_weight = recent_games[idx] / total_recent_games
                    season_weight = season_games[season_idx] / total_season_games
                    position_weight = 1.7 if idx == 0 else 1.3  # Adjusted weights for 2 champions
                    seasonal_position_weight = 1.3 if season_idx < 3 else 1.0
                    
                    combined_weight = (
                        recent_weight * 0.6 +
                        season_weight * 0.4
                    ) * position_weight * seasonal_position_weight
                    
                    loyalty_score += combined_weight
            
            # Calculate confidence score (adjusted for 2 champions)
            confidence_score = 0
            confidence_score += 0.5 if pd.notna(row['most_champ_1']) else 0  # Increased weight for main
            confidence_score += 0.2 if pd.notna(row['most_champ_2']) else 0  # Increased weight for second
            confidence_score += sum(0.1 for i in range(1, 4) if pd.notna(row[f'season_champ_{i}']))
            confidence_score += sum(0.05 for i in range(4, 8) if pd.notna(row[f'season_champ_{i}']))
            
            recent_games = sum((row[f'W_{i}'] + row[f'L_{i}']) if pd.notna(row[f'most_champ_{i}']) else 0 
                             for i in range(1, 3))  # Only top 2
            confidence_score += min(0.1, recent_games / 100)
            
            return {
                'loyalty_score': round(min(loyalty_score, 1.0), 3),
                'confidence_score': round(min(confidence_score, 1.0), 3),
                **champ_loyalty_flags
            }
            
        except Exception as e:
            print(f"Error calculating loyalty scores: {e}")
            return {
                'loyalty_score': 0,
                'confidence_score': 0,
                'recent_champ_1_loyal': 0,
                'recent_champ_2_loyal': 0
            }
    
    # Apply calculations and expand results to columns
    results = df.apply(get_loyalty_scores, axis=1)
    
    # Convert results to new columns
    df['champion_loyalty_score'] = results.apply(lambda x: x['loyalty_score'])
    df['loyalty_confidence_score'] = results.apply(lambda x: x['confidence_score'])
    df['recent_champ_1_loyal'] = results.apply(lambda x: x['recent_champ_1_loyal'])
    df['recent_champ_2_loyal'] = results.apply(lambda x: x['recent_champ_2_loyal'])
    
    return df

def optimize_feature_dtypes(df):
    """
    Optimize data types for feature columns using unsigned integers for non-negative values
    """
    df = df.copy()
    
    # Very small range integers (< 10 unique values) to uint8 (0 to 255)
    category_cols = {
        'region': 4,              # 4 unique values
        'team': 2,               # 2 unique values
        'champ_variety_score': 6, # 6 unique values
        'playstyle': 6,          # 6 unique values
        'most_role_1': 5,        # 5 unique values
        'most_role_2': 5,        # 5 unique values
        'most_role_3': 5,        # 5 unique values
        'role_specialization': 5,  # 5 unique values
        'recent_champ_1_loyal':2,  # 2 unique values
        'recent_champ_2_loyal':2   # 2 unique values
    }
    
    for col, n_unique in category_cols.items():
        if col in df.columns:
            if df[col].isna().any():
                # For columns with NaN, ensure proper handling
                df[col] = df[col].astype('category')
                # Fill NaN with a new category if needed
                df[col] = df[col].cat.add_categories(['Unknown']).fillna('Unknown')
            else:
                df[col] = df[col].astype('category')  # Regular unsigned integer
    
    # Medium range integers (< 200 unique values) to UInt8 (0 to 255)
    champion_cols = [
        'champion',         # 168 unique
        'team_champ1',     # 149 unique
        'team_champ2',     # 154 unique
        'team_champ3',     # 143 unique
        'team_champ4',     # 140 unique
        'opp_champ1',      # 144 unique
        'opp_champ2',      # 82 unique
        'opp_champ3',      # 145 unique
        'opp_champ4',      # 119 unique
        'opp_champ5',      # 110 unique
        'most_champ_1',    # 138 unique
        'most_champ_2',    # 134 unique
        'season_champ1',   # 139 unique
        'season_champ2',   # 129 unique
        'season_champ3',   # 132 unique
        '1_champ_name',    # 114 unique
        '2_champ_name',    # 114 unique
        '3_champ_name',    # 112 unique
        '4_champ_name',    # 111 unique
        '5_champ_name'     # 113 unique
    ]
    
    for col in champion_cols:
        if col in df.columns:
            df[col] = df[col].astype('UInt8')  # All champion IDs can fit in UInt8
    
    # Float32 columns (performance metrics and ratios)
    float32_cols = [
        'most_role_1_value',         # 15 unique
        'most_role_2_value',         # 11 unique
        'most_role_3_value',         # 15 unique
        'avg_kills',                 # 92 unique
        'avg_deaths',                # 58 unique
        'avg_assists',               # 132 unique
        'kda_ratio_profile',         # 286 unique
        'kill_participation_profile', # 37 unique
        'WR_1',                      # 64 unique
        'WR_2',                      # 23 unique
        'WR_3',                      # 10 unique
        'champion_loyalty_score',     # 156 unique
        'loyalty_confidence_score'    # 5 unique
    ]
    
    for col in float32_cols:
        if col in df.columns:
            df[col] = df[col].astype('float32')
    
    return df

def remove_unwanted_columns(df):
    """
    Removes specified columns from the DataFrame
    
    Args:
        df (pd.DataFrame): Input DataFrame
    
    Returns:
        pd.DataFrame: DataFrame with specified columns removed
    """
    df = df.copy()
    
    # Define columns to remove
    columns_to_remove = (
        # Time and basic stats
        ['date'] +
        ['total_games', 'wins', 'losses', 'win_rate'] +
        ['WR_1', 'WR_2', 'WR_3'] +
        ['most_champ_3'] +
        ['W_1', 'L_1', 'KDA_1', 'W_2', 'L_2', 'KDA_2', 'W_3', 'L_3', 'KDA_3'] +
        
        # Roles
        ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT'] +
        
        # Season and weekly stats
        ['cs_ssn_1', 'cpm_ssn_1', 'kda_ssn_1', 'k_ssn_1', 'd_ssn_1', 'a_ssn_1', 'wr_ssn_1', 'games_ssn_1',
         'cs_ssn_2', 'cpm_ssn_2', 'kda_ssn_2', 'k_ssn_2', 'd_ssn_2', 'a_ssn_2', 'wr_ssn_2', 'games_ssn_2',
         'cs_ssn_3', 'cpm_ssn_3', 'kda_ssn_3', 'k_ssn_3', 'd_ssn_3', 'a_ssn_3', 'wr_ssn_3', 'games_ssn_3',
         'season_champ_4', 'cs_ssn_4', 'cpm_ssn_4', 'kda_ssn_4', 'k_ssn_4', 'd_ssn_4', 'a_ssn_4', 'wr_ssn_4', 'games_ssn_4',
         'season_champ_5', 'cs_ssn_5', 'cpm_ssn_5', 'kda_ssn_5', 'k_ssn_5', 'd_ssn_5', 'a_ssn_5', 'wr_ssn_5', 'games_ssn_5',
         'season_champ_6', 'cs_ssn_6', 'cpm_ssn_6', 'kda_ssn_6', 'k_ssn_6', 'd_ssn_6', 'a_ssn_6', 'wr_ssn_6', 'games_ssn_6',
         'season_champ_7', 'cs_ssn_7', 'cpm_ssn_7', 'kda_ssn_7', 'k_ssn_7', 'd_ssn_7', 'a_ssn_7', 'wr_ssn_7', 'games_ssn_7'] +
        
        # Weekly stats
        ['7d_champ_1', '7d_total_1', '7d_WR_1', '7d_champ_2', '7d_total_2', '7d_WR_2', 
         '7d_champ_3', '7d_total_3', '7d_WR_3'] +
        ['7d_W_1', '7d_L_1', '7d_W_2', '7d_L_2', '7d_W_3', '7d_L_3'] +
        
        # Mastery stats
        ['mastery_champ_1', 'm_lv_1', 'mastery_champ_2', 'm_lv_2', 'mastery_champ_3', 'm_lv_3',
         'mastery_champ_4', 'm_lv_4', 'mastery_champ_5', 'm_lv_5', 'mastery_champ_6', 'm_lv_6',
         'mastery_champ_7', 'm_lv_7', 'mastery_champ_8', 'm_lv_8', 'mastery_champ_9', 'm_lv_9',
         'mastery_champ_10', 'm_lv_10', 'mastery_champ_11', 'm_lv_11', 'mastery_champ_12', 'm_lv_12',
         'mastery_champ_13', 'm_lv_13', 'mastery_champ_14', 'm_lv_14', 'mastery_champ_15', 'm_lv_15',
         'mastery_champ_16', 'm_lv_16'] +
        
        # Champion scores and others
        ['1_champ_score', '2_champ_score', '3_champ_score', '4_champ_score', '5_champ_score'] +
        ['avg_tier', 'team'] +
        
        # Champions individual score
        ["Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Ambessa", "Amumu", "Anivia", "Annie", "Aphelios", 
         "Ashe", "Aurelion Sol", "Aurora", "Azir", "Bard", "Bel'Veth", "Blitzcrank", "Brand", "Braum", 
         "Briar", "Caitlyn", "Camille", "Cassiopeia", "Cho'Gath", "Corki", "Darius", "Diana", "Dr. Mundo", 
         "Draven", "Ekko", "Elise", "Evelynn", "Ezreal", "Fiddlesticks", "Fiora", "Fizz", "Galio", 
         "Gangplank", "Garen", "Gnar", "Gragas", "Graves", "Gwen", "Hecarim", "Heimerdinger", "Hwei", 
         "Illaoi", "Irelia", "Ivern", "Janna", "Jarvan IV", "Jax", "Jayce", "Jhin", "Jinx", "K'Sante", 
         "Kai'Sa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina", "Kayle", "Kayn", "Kennen", 
         "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee Sin", "Leona", "Lillia", "Lissandra", 
         "Lucian", "Lulu", "Lux", "Malphite", "Malzahar", "Maokai", "Master Yi", "Milio", "Miss Fortune", 
         "Mordekaiser", "Morgana", "Naafiri", "Nami", "Nasus", "Nautilus", "Neeko", "Nidalee", "Nilah", 
         "Nocturne", "Nunu & Willump", "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", 
         "Quinn", "Rakan", "Rammus", "Rek'Sai", "Rell", "Renata Glasc", "Renekton", "Rengar", "Riven", 
         "Rumble", "Ryze", "Samira", "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", 
         "Singed", "Sion", "Sivir", "Skarner", "Smolder", "Sona", "Soraka", "Swain", "Sylas", "Syndra", 
         "Tahm Kench", "Taliyah", "Talon", "Taric", "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere", 
         "Twisted Fate", "Twitch", "Udyr", "Urgot", "Varus", "Vayne", "Veigar", "Vel'Koz", "Vex", "Vi", 
         "Viego", "Viktor", "Vladimir", "Volibear", "Warwick", "Wukong", "Xayah", "Xerath", "Xin Zhao", 
         "Yasuo", "Yone", "Yorick", "Yuumi", "Zac", "Zed", "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra"]
    )
    
    # Remove columns that exist in the DataFrame
    columns_to_remove = [col for col in columns_to_remove if col in df.columns]
    
    # Drop the columns
    df = df.drop(columns=columns_to_remove)
    
    # Print info about removed columns
    print(f"Removed {len(columns_to_remove)} columns")
    print(f"Remaining columns: {len(df.columns)}")
    
    return df


def apply_feature_engineering(df, n=5):
    """
    Performs feature engineering pipeline
    """
    df = df.copy()
    
    # Engineering pipeline
    transformations = [
        calculate_champ_variety_score,
        calculate_playstyle,
        get_most_role_3,
        calculate_role_specialization,
        calculate_champion_loyalty,
        lambda x: get_top_champion_scores(x, n),  # Add top 5 champions
        remove_unwanted_columns,
        optimize_feature_dtypes 
    ]
    
    for transform in transformations:
        try:
            print(f"Applying {transform.__name__}...")
            df = transform(df)
        except Exception as e:
            print(f"Error in {transform.__name__}: {str(e)}")
            raise
    
    return df
