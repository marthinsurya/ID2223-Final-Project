import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from helper import format_summoner_name

# Constants
BASE_URL = "https://www.op.gg/summoners/{region}/{username}?queue_type=SOLORANKED"
MASTERY_URL = "https://www.op.gg/summoners/{region}/{username}/mastery"

def setup_driver():
    """Setup optimized Chrome WebDriver"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-extensions")
    options.page_load_strategy = 'eager'
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_and_find_element(driver, selector, timeout=20, description="element"):
    """Utility function for waiting and finding elements"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element
    except Exception as e:
        print(f"Error finding {description}: {e}")
        return None

def get_recent_stats(stats_box):
    """Extract recent statistics from stats box"""
    try:
        stats = stats_box.find_element(By.CSS_SELECTOR, "div.stats")
        recent_stats = stats.text.strip().split("\n")
        
        # Parse the stats into a structured format
        games_info = recent_stats[0].split()  # ['20G', '13W', '7L']
        total_games = int(games_info[0].replace('G', ''))
        wins = int(games_info[1].replace('W', ''))
        losses = int(games_info[2].replace('L', ''))
        
        win_rate = float(recent_stats[1].replace('%', '')) / 100
        
        kda_parts = recent_stats[2].split(' / ')  # ['5.1', '4.0', '7.9']
        kills = float(kda_parts[0])
        deaths = float(kda_parts[1])
        assists = float(kda_parts[2])
        
        kda_ratio = float(recent_stats[3].replace(':1', ''))
        kill_participation = float(recent_stats[4].replace('P/Kill ', '').replace('%', '')) / 100

        recent_stats = {
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "avg_kills": kills,
            "avg_deaths": deaths,
            "avg_assists": assists,
            "kda_ratio": kda_ratio,
            "kill_participation": kill_participation,
        }
    
    except Exception as e:
        print(f"Error extracting recent stats: {e}")
        return None
    
    return recent_stats

def get_recent_champions(stats_box):
    champions = stats_box.find_element(By.CSS_SELECTOR, "div.champions")
    champion_elements = champions.find_elements(By.CSS_SELECTOR, "li")
    
    # Initialize flat dictionary with defaults
    recent_champ_stats = {
        "most_champ_1": None, "WR_1": 0.0, "W_1": 0, "L_1": 0, "KDA_1": 0.0,
        "most_champ_2": None, "WR_2": 0.0, "W_2": 0, "L_2": 0, "KDA_2": 0.0,
        "most_champ_3": None, "WR_3": 0.0, "W_3": 0, "L_3": 0, "KDA_3": 0.0
    }

    for i, champion in enumerate(champion_elements, 1):
        try:
            # Initialize kda for this iteration
            kda = 0.0
            
            # Extract champion name and image source
            champ_name = champion.find_element(By.TAG_NAME, "img").get_attribute("alt")
            
            # Extract win/lose stats and KDA
            win_lose = champion.find_element(By.CSS_SELECTOR, ".win-lose").text.strip()
            win_rate = float(win_lose.split('%')[0]) / 100  # "75%" -> 0.75
            wins = int(win_lose.split('(')[1].split('W')[0])  # "(3W 1L)" -> 3
            losses = int(win_lose.split('W')[1].split('L')[0])  # "1L)" -> 1
           
            # KDA processing with a more precise selector
            try:
                kda_element = champion.find_element(By.CSS_SELECTOR, "div[class*='e1t9nk8i2']")
                if kda_element:
                    kda_text = kda_element.text.strip()
                    #print(f"Found KDA text for champion {i}: '{kda_text}'")  # Debug print
                    if kda_text and "KDA" in kda_text:
                        kda = float(kda_text.split("KDA")[0].strip())
                        #print(f"Parsed KDA value: {kda}")  # Debug print
                    else:
                        print(f"Invalid KDA text format for champion {i}: '{kda_text}'")
                else:
                    print(f"No KDA element found for champion {i}")
            except Exception as e:
                print(f"Error processing KDA: {e}")
                kda = 0.0
                
            # Update flat dictionary
            recent_champ_stats[f"most_champ_{i}"] = champ_name
            recent_champ_stats[f"WR_{i}"] = win_rate
            recent_champ_stats[f"W_{i}"] = wins
            recent_champ_stats[f"L_{i}"] = losses
            recent_champ_stats[f"KDA_{i}"] = kda
            
        except Exception as e:
            print(f"Error processing champion {i}: {e}")
            # Dictionary already has default values for this champion
            continue
    
    return recent_champ_stats

def get_preferred_role(stats_box):
    # Role priority (higher index = higher priority when tied)
    role_priority = {
        'SUPPORT': 0,
        'ADC': 1,
        'TOP': 2,
        'JUNGLE': 3,
        'MID': 4
    }
    
    # Find the positions section
    positions = stats_box.find_element(By.CSS_SELECTOR, "div.positions")
    role_elements = positions.find_elements(By.CSS_SELECTOR, "li")
    
    preferred_roles = {
        'TOP': 0.0, 'JUNGLE': 0.0, 'MID': 0.0, 'ADC': 0.0, 'SUPPORT': 0.0,
        'most_role_1': None, 'most_role_2': None,
        'most_role_1_value': 0.0, 'most_role_2_value': 0.0
    }
    
    # First, collect all role percentages
    for role in role_elements:
        role_name = role.find_element(By.CSS_SELECTOR, "div.position img").get_attribute("alt")
        percentage = role.find_element(By.CSS_SELECTOR, "div.gauge").get_attribute("style")
        
        if percentage:
            percentage_value = percentage.split(":")[1].strip().replace("%", "").strip(';')
            try:
                preferred_roles[role_name] = int(percentage_value)/100
            except ValueError:
                preferred_roles[role_name] = 0
    
    # Sort roles by percentage first, then by priority when tied
    sorted_roles = sorted(
        [(role, value) for role, value in preferred_roles.items() if role in role_priority],
        key=lambda x: (x[1], role_priority[x[0]]),  # Sort by percentage first, then role priority
        reverse=True
    )
    
    # Add top 2 roles if they exist
    if len(sorted_roles) > 0:
        preferred_roles['most_role_1'] = sorted_roles[0][0]
        preferred_roles['most_role_1_value'] = sorted_roles[0][1]
    if len(sorted_roles) > 1:
        preferred_roles['most_role_2'] = sorted_roles[1][0]
        preferred_roles['most_role_2_value'] = sorted_roles[1][1]
    
    return preferred_roles

def get_weekly_stats(ranked_7d_box):
    # Find the list of champions in the ranked 7d box
    champion_elements = ranked_7d_box.find_elements(By.CSS_SELECTOR, "ul li")[:3]
    
    # Initialize flat dictionary with defaults for 3 champions
    weekly_stats = {
        "7d_champ_1": None, "7d_total_1": 0, "7d_W_1": 0, "7d_L_1": 0, "7d_WR_1": 0.0,
        "7d_champ_2": None, "7d_total_2": 0, "7d_W_2": 0, "7d_L_2": 0, "7d_WR_2": 0.0,
        "7d_champ_3": None, "7d_total_3": 0, "7d_W_3": 0, "7d_L_3": 0, "7d_WR_3": 0.0
    }
    
    # Find the list of champions and take first 3
    for i, champion in enumerate(champion_elements, 1):
        try:
            # Extract champion name
            champ_name = champion.find_element(By.CSS_SELECTOR, "div.info > div.name > a").text.strip()

            # Extract wins and losses
            try:
                win_text = champion.find_element(By.XPATH, ".//div[@class='graph']//div[@class='text left']").text.strip()
                loss_text = champion.find_element(By.XPATH, ".//div[@class='graph']//div[@class='text right']").text.strip()
                wins = int(win_text.replace('W', '').strip()) if 'W' in win_text else 0
                losses = int(loss_text.replace('L', '').strip()) if 'L' in loss_text else 0
            except Exception:
                wins = 0
                losses = 0

            # Calculate total games
            total_games = wins + losses
            
            # Extract win rate
            try:
                win_rate_text = champion.find_element(By.CSS_SELECTOR, "div.winratio").text.strip()
                win_rate = float(win_rate_text.replace('%', '').strip()) / 100 if win_rate_text else 0
            except Exception:
                win_rate = 0
            
            # Update flat dictionary with dynamic numbering
            weekly_stats[f"7d_champ_{i}"] = champ_name
            weekly_stats[f"7d_total_{i}"] = total_games
            weekly_stats[f"7d_W_{i}"] = wins
            weekly_stats[f"7d_L_{i}"] = losses
            weekly_stats[f"7d_WR_{i}"] = win_rate
            
        except Exception as e:
            print(f"Error processing champion {i} in 7d stats: {e}")
            # Add default values for error cases
            weekly_stats[f"7d_champ_{i}"] = None
            weekly_stats[f"7d_total_{i}"] = 0
            weekly_stats[f"7d_W_{i}"] = 0
            weekly_stats[f"7d_L_{i}"] = 0
            weekly_stats[f"7d_WR_{i}"] = 0.0
    
    return weekly_stats

def get_season_data(season_champ_box):   
    # Initialize flat dictionary with defaults for 7 champions
    season_data = {
        "season_champ_1": None, "cs_ssn_1": "0", "cpm_ssn_1": "0", "kda_ssn_1": "0", "k_ssn_1": "0", "d_ssn_1": "0", "a_ssn_1": "0", "wr_ssn_1": 0.0, "games_ssn_1": "0",
        "season_champ_2": None, "cs_ssn_2": "0", "cpm_ssn_2": "0", "kda_ssn_2": "0", "k_ssn_2": "0", "d_ssn_2": "0", "a_ssn_2": "0", "wr_ssn_2": 0.0, "games_ssn_2": "0",
        "season_champ_3": None, "cs_ssn_3": "0", "cpm_ssn_3": "0", "kda_ssn_3": "0", "k_ssn_3": "0", "d_ssn_3": "0", "a_ssn_3": "0", "wr_ssn_3": 0.0, "games_ssn_3": "0",
        "season_champ_4": None, "cs_ssn_4": "0", "cpm_ssn_4": "0", "kda_ssn_4": "0", "k_ssn_4": "0", "d_ssn_4": "0", "a_ssn_4": "0", "wr_ssn_4": 0.0, "games_ssn_4": "0",
        "season_champ_5": None, "cs_ssn_5": "0", "cpm_ssn_5": "0", "kda_ssn_5": "0", "k_ssn_5": "0", "d_ssn_5": "0", "a_ssn_5": "0", "wr_ssn_5": 0.0, "games_ssn_5": "0",
        "season_champ_6": None, "cs_ssn_6": "0", "cpm_ssn_6": "0", "kda_ssn_6": "0", "k_ssn_6": "0", "d_ssn_6": "0", "a_ssn_6": "0", "wr_ssn_6": 0.0, "games_ssn_6": "0",
        "season_champ_7": None, "cs_ssn_7": "0", "cpm_ssn_7": "0", "kda_ssn_7": "0", "k_ssn_7": "0", "d_ssn_7": "0", "a_ssn_7": "0", "wr_ssn_7": 0.0, "games_ssn_7": "0"
    }
    
    try:
        # Find all champion boxes directly
        champion_boxes = season_champ_box.find_elements(By.CSS_SELECTOR, "div.champion-box")
        
        for i, box in enumerate(champion_boxes[:7], 1):
            try:
                # Extract champion name
                champ_name = box.find_element(By.CSS_SELECTOR, "div.name a").text.strip()
                # Extract CS stats and CPM
                cs_text = box.find_element(By.CSS_SELECTOR, "div.cs").text.strip()
                cs_parts = cs_text.split()
                cs_stats = cs_parts[1] if len(cs_parts) > 1 else "0"
                # Extract CPM from parentheses
                cpm = cs_parts[2].strip('()') if len(cs_parts) > 2 else "0"
                
                # Extract KDA ratio
                kda_element = box.find_element(By.CSS_SELECTOR, "div.kda div[class^='css-']")
                kda_text = kda_element.text.strip()
                kda_ratio = kda_text.replace(" KDA", "").replace(":1", "").strip()
                
                # Extract K/D/A averages
                kda_detail = box.find_element(By.CSS_SELECTOR, "div.kda div.detail").text.strip()
                k, d, a = map(str.strip, kda_detail.split('/'))
                
                # Extract win rate
                win_rate_element = box.find_element(By.CSS_SELECTOR, "div.played div[class^='css-']")
                win_rate_text = win_rate_element.text.strip()
                win_rate = float(win_rate_text.replace('%', '')) / 100
                
                # Extract games played
                games_text = box.find_element(By.CSS_SELECTOR, "div.played div.count").text.strip()
                games_played = games_text.replace(" Played", "")
                
                # Update flat dictionary
                season_data[f"season_champ_{i}"] = champ_name
                season_data[f"cs_ssn_{i}"] = cs_stats
                season_data[f"cpm_ssn_{i}"] = cpm
                season_data[f"kda_ssn_{i}"] = kda_ratio
                season_data[f"k_ssn_{i}"] = k
                season_data[f"d_ssn_{i}"] = d
                season_data[f"a_ssn_{i}"] = a
                season_data[f"wr_ssn_{i}"] = win_rate
                season_data[f"games_ssn_{i}"] = games_played

            except Exception as e:
                print(f"Error processing champion {i}: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                
    except Exception as e:
        print(f"Error in get_season_data main block: {str(e)}")
        print(f"Error type: {type(e).__name__}")
    
    return season_data

def get_mastery_data(driver):
    # Initialize dictionary with metadata
    mastery_data = { }
    
    try:
        # Wait for container to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-zefc5s.e1poynyt0"))
        )
        
        # Get all champion boxes (limiting to first 16)
        champion_boxes = driver.find_elements(By.CSS_SELECTOR, "div.css-8fea4f.e1poynyt1")[:16]
        
        # Process each champion
        for i, champion in enumerate(champion_boxes, 1):
            try:
                name = champion.find_element(By.CSS_SELECTOR, "strong.champion-name").text.strip()
                level = champion.find_element(By.CSS_SELECTOR, "div.champion-level__text > span").text.strip()
                #points = champion.find_element(By.CSS_SELECTOR, "div.champion-point > span").text.strip()
                
                mastery_data[f"mastery_champ_{i}"] = name
                mastery_data[f"m_lv_{i}"] = level
                #mastery_data[f"m_points_{i}"] = points.replace(",", "")
                
            except Exception as e:
                print(f"Error processing champion {i}: {e}")
                mastery_data[f"mastery_champ_{i}"] = None
                mastery_data[f"m_lv_{i}"] = "0"
                #mastery_data[f"m_points_{i}"] = "0"

    except Exception as e:
        print(f"Error scraping mastery data: {e}")

    return mastery_data


def get_player_stats(region, username):
    """Main function to get player statistics"""
    driver = None
    try:
        driver = setup_driver()
        
        # Format URLs
        profile_url = BASE_URL.format(region=region, username=username)
        mastery_url = MASTERY_URL.format(region=region, username=username)
        
        # Get main profile data
        driver.get(profile_url)
        
        # Find main containers
        main_container = wait_and_find_element(driver, "#content-container")
        if not main_container:
            raise Exception("Could not find main container")
            
        stats_box = wait_and_find_element(
            driver,
            "div.stats-box.stats-box--SOLORANKED"
        )
        
        season_champ_box = wait_and_find_element(
            driver,
            "div:nth-child(1) > div.css-18w3o0f.ere6j7v0"
        )

        ranked_7d_box = wait_and_find_element(
            driver,
            "div[class*='efsztyx0']"
        )

        # Extract all stats
        player_data = {
            'recent_stats': get_recent_stats(stats_box) if stats_box else None,
            'recent_champions': get_recent_champions(stats_box) if stats_box else None,
            'preferred_roles': get_preferred_role(stats_box) if stats_box else None,
            'season_data': get_season_data(season_champ_box) if season_champ_box else None,
            'weekly_stats': get_weekly_stats(ranked_7d_box) if ranked_7d_box else None,
        }
        
        # Get mastery data
        driver.get(mastery_url)
        mastery_data = get_mastery_data(driver)
        player_data['mastery_data'] = mastery_data

        # Create DataFrames
        dfs = {}
        for key, data in player_data.items():
            if data:
                dfs[key] = pd.DataFrame([data])

        # Add player ID and region to each DataFrame
        for df in dfs.values():
            df.insert(0, 'player_id', username)  # Insert player_id as first column
            df.insert(1, 'region', region)      # Insert region as second column

        # Merge all DataFrames into one
        merged_df = None
        for name, df in dfs.items():
            if merged_df is None:
                merged_df = df
            else:
                # Drop common columns except player_id and region
                common_cols = df.columns.intersection(merged_df.columns)
                cols_to_drop = [col for col in common_cols if col not in ['player_id', 'region']]
                df_to_merge = df.drop(columns=cols_to_drop, errors='ignore')
                merged_df = pd.merge(merged_df, df_to_merge, on=['player_id', 'region'], how='outer')

        # Ensure player_id and region are the first columns in final order
        if merged_df is not None and not merged_df.empty:
            # Get all columns except player_id and region
            other_cols = [col for col in merged_df.columns if col not in ['player_id', 'region']]
            # Reorder columns with player_id and region first
            merged_df = merged_df[['player_id', 'region'] + other_cols]

        # # Save merged DataFrame
        # save_dir = "util/data"
        # os.makedirs(save_dir, exist_ok=True)
        
        # if merged_df is not None and not merged_df.empty:
        #     filepath = os.path.join(save_dir, f"player_stats.csv")
        #     merged_df.to_csv(filepath, index=False)
        #     print(f"Saved player stats to {filepath}")

        return merged_df, dfs

    except Exception as e:
        print(f"Error in get_player_stats: {e}")
        return None, {}

    finally:
        if driver:
            driver.quit()

def get_multiple_player_stats(players_df):
    """
    Get stats for multiple players from a DataFrame
    
    Parameters:
    players_df: DataFrame with columns 'region' and 'username'
    """
    all_merged_dfs = []
    error_players = []
    
    save_dir = "util/data"
    os.makedirs(save_dir, exist_ok=True)
    checkpoint_file = os.path.join(save_dir, "player_stats_checkpoint.csv")
    all_merged_dfs = []
    error_players = []
    
    # Load checkpoint if exists
    start_idx = 0
    if os.path.exists(checkpoint_file):
        try:
            checkpoint_df = pd.read_csv(checkpoint_file)
            all_merged_dfs = [checkpoint_df]
            # Get the number of players already processed
            processed_players = set(checkpoint_df['player_id'])
            # Filter out already processed players
            players_df = players_df[~players_df['username'].isin(processed_players)]
            print(f"Loaded checkpoint with {len(processed_players)} players already processed")
        except Exception as e:
            print(f"Error loading checkpoint: {e}")

    print(f"Processing {len(players_df)} remaining players...")
    
    for idx, row in players_df.iterrows():
        region = row['region'].lower()  # Ensure region is lowercase
        username = row['username']
        
        try:
            # Format the username
            formatted_username = format_summoner_name(username)
            print(f"\nProcessing player {idx + 1}/{len(players_df)}: {username} ({region})")
            print(f"Formatted username: {formatted_username}")
            
            # Add delay between requests
            if idx > 0:
                time.sleep(2)
                
            merged_df, _ = get_player_stats(region, formatted_username)
            if merged_df is not None and not merged_df.empty:
                # Store original username in the DataFrame
                merged_df['player_id'] = username  # Store original username
                all_merged_dfs.append(merged_df)
                print(f"Successfully processed {username}")

                # Save checkpoint every 10 players
                if len(all_merged_dfs) % 10 == 0:
                    checkpoint_save = pd.concat(all_merged_dfs, ignore_index=True)
                    checkpoint_save.to_csv(checkpoint_file, index=False)
                    print(f"Saved checkpoint after processing {len(all_merged_dfs)} players")

            else:
                print(f"No data found for {username}")
                error_players.append({
                    'region': region,
                    'username': username,
                    'formatted_username': formatted_username,
                    'error': 'No data found'
                })
                
        except Exception as e:
            print(f"Error processing {username}: {e}")
            error_players.append({
                'region': region,
                'username': username,
                'formatted_username': formatted_username if 'formatted_username' in locals() else 'Error in formatting',
                'error': str(e)
            })
            continue

    # Combine and save final results
    if all_merged_dfs:
        final_df = pd.concat(all_merged_dfs, ignore_index=True)
        
        # Save final combined stats
        filepath = os.path.join(save_dir, "player_stats.csv")
        final_df.to_csv(filepath, index=False)
        print(f"\nSaved combined stats for {len(all_merged_dfs)} players to {filepath}")
        
        # Clean up checkpoint file
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            print("Removed checkpoint file after successful completion")
        
        # Save error log
        if error_players:
            error_df = pd.DataFrame(error_players)
            error_filepath = os.path.join(save_dir, "player_stats_errors.csv")
            error_df.to_csv(error_filepath, index=False)
            print(f"Saved error log to {error_filepath}")
        
        return final_df
    else:
        print("\nNo player data was collected")
        return None