import pandas as pd
from datetime import datetime
import os
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
        return pd.to_datetime(date_str).timestamp()
    

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


def check_dataframe_types(df):
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