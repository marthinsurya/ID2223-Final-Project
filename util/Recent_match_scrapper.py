import time, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from urllib.parse import unquote
from webdriver_manager.chrome import ChromeDriverManager
from helper import convert_to_minutes, convert_percentage_to_decimal, convert_tier_to_number, convert_result_to_binary, format_summoner_name, convert_to_displayname

def setup_driver():
    options = Options()
    prefs = {
        'profile.default_content_setting_values': {'notifications': 2},
        'profile.managed_default_content_settings': {'images': 2}
    }
    options.add_experimental_option('prefs', prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    for arg in ['--headless', '--no-sandbox', '--disable-dev-shm-usage', 
                '--disable-gpu', '--window-size=1920,1080']:
        options.add_argument(arg)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_tooltip_date(driver, element):
    try:
        driver.execute_script("""
            arguments[0].scrollIntoView({block: 'center'});
            document.querySelectorAll('span.react-tooltip-lite').forEach(e => e.remove());
            arguments[0].dispatchEvent(new MouseEvent('mouseover', {
                view: window, bubbles: true, cancelable: true
            }));
        """, element)
        time.sleep(0.3)
        return driver.execute_script("""
            return Array.from(document.querySelectorAll('span.react-tooltip-lite'))
                .find(t => t.offsetParent !== null)?.textContent || null;
        """)
    except: return None
    
def extract_match_data(match):
    selectors = {
        'time_stamp': "div.time-stamp > div",
        'game_type': "div.game-type",
        'result': "div.result",
        'length': "div.length",
        'kda': "div.kda",
        'kda_ratio': "div.kda-ratio",
        'cs': "div.cs",
        'avg_tier': "div.avg-tier",
        'laning': "div.laning",
        'kill_participation': "div.p-kill",
        'champion_img': "div.info a.champion img",
        'champion_level': "div.info a.champion span.champion-level"
    }
    
    data = {}
    try:
        for key, selector in selectors.items():
            element = match.find_element(By.CSS_SELECTOR, selector)
            if key == 'champion_img':
                data[key] = element.get_attribute('alt')
            elif key == 'laning':
                data[key] = element.text.replace('\n', '')  # Remove newlines from laning data
            else:
                data[key] = element.text
    except Exception as e:
        print(f"Error extracting match data: {e}")
    return data

def get_players_info(match):
    try:
        players = []
        player_elements = match.find_elements(By.CSS_SELECTOR, "div.css-pp7uqb.e1xevas21")[:10]
        for player in player_elements:
            champion = player.find_element(By.CSS_SELECTOR, "div.icon img").get_attribute("alt")
            href = player.find_element(By.CSS_SELECTOR, "div.name a").get_attribute("href")
            region, name = href.split('/')[-2:]
            # Decode the URL-encoded name
            decoded_name = unquote(name)
            #print(f"Found player: {decoded_name} with champion {champion}")
            players.append({
                "champion": champion, 
                "region": region, 
                "name": decoded_name
            })
        return players
    except Exception as e:
        print(f"Error getting players info: {e}")
        return []

def convert_laning_ratio(laning_str):
    """Convert laning string (e.g., 'Laning 70:30') to decimal ratio"""
    try:
        # Extract the ratio part (e.g., '70:30' from 'Laning 70:30')
        ratio_part = laning_str.split('Laning')[-1].strip()
        
        # Split by ':' and convert to numbers
        first_num, second_num = map(int, ratio_part.split(':'))
        
        # Calculate ratio
        if second_num != 0:  # Avoid division by zero
            ratio = round(first_num / second_num, 2)
            return ratio
        return 0.0
    except Exception as e:
        print(f"Laning conversion error for '{laning_str}': {e}")
        return 0.0
    
def extract_cs_number(cs_str):
    """Extract pure CS number from string (e.g., 'CS 123 (7.9)' -> 123)"""
    try:
        # Extract first number from the string
        cs_number = ''.join(filter(str.isdigit, cs_str.split('(')[0]))
        return int(cs_number) if cs_number else 0
    except:
        return 0
    
def extract_cs_per_min(cs_str):
    """Extract CS per minute from string (e.g., 'CS 123 (7.9)' -> 7.9)"""
    try:
        # Extract number between parentheses
        cs_per_min = cs_str.split('(')[1].split(')')[0]
        return float(cs_per_min)
    except:
        return 0.0

def process_match_data(match_data, username, players):
    try:
        # Format username for comparison - ensure it's in display format
        display_name = convert_to_displayname(username)
        #print(f"\nInput username: {username}")
        #print(f"Converted display name: {display_name}")
        
        # # Debug print all players and their converted names
        # print("\nAll players:")
        # for p in players:
        #     orig_name = p['name']
        #     conv_name = convert_to_displayname(orig_name)
        #     print(f"Original: {orig_name} -> Converted: {conv_name}")
        
        # Find player index using normalized comparison
        player_index = next((i for i, p in enumerate(players) 
                           if convert_to_displayname(p['name']).lower().replace(' ', '') == 
                           display_name.lower().replace(' ', '')), -1)
        
        if player_index == -1:
            print(f"\nWarning: Player {display_name} not found in players list")
            print("Available players:", [convert_to_displayname(p['name']) for p in players])
            return None
            
        #print(f"\nFound player at index: {player_index}")
        team = "blue" if player_index < 5 else "red"
        #print(f"Team: {team}")
            
        
        # Modify how teammates and opponents are filtered
        if player_index < 5:
            # Player is on blue team
            teammates = [p for i, p in enumerate(players[:5]) 
                       if i != player_index]  # Use index comparison instead of name
            opponents = players[5:]  # All red team players
        else:
            # Player is on red team
            teammates = [p for i, p in enumerate(players[5:]) 
                       if i != (player_index - 5)]  # Adjust index for red team
            opponents = players[:5]  # All blue team players
        
        kda_parts = match_data.get('kda', '0/0/0').strip().split('/')
        kills, deaths, assists = [kda_parts[i] if i < len(kda_parts) else "0" for i in range(3)]
        kda_ratio = match_data.get("kda_ratio", "0").strip().replace(":1 KDA", "")

        kill_participation = convert_percentage_to_decimal(match_data.get("kill_participation", "0%"))

        laning_ratio = convert_laning_ratio(match_data.get("laning", "0:0"))

        cs = extract_cs_number(match_data.get("cs", "0"))
        cpm = extract_cs_per_min(match_data.get("cs", "0"))

        match_length_str = match_data.get("length", "0m 0s")
        match_length_mins = convert_to_minutes(match_length_str)

        # Convert tier to number
        avg_tier_num = convert_tier_to_number(match_data.get("avg_tier", ""))

        result_num = convert_result_to_binary(match_data.get("result", ""))
        
        match_row = {
            "player_id": display_name,  # Use display_name here
            "date": match_data.get("match_date", ""),
            "champion": match_data.get("champion_img", ""),
            "level": match_data.get("champion_level", ""),
            "team": team,
            "result": result_num,
            "match_length_mins": match_length_mins, 
            "kill": kills.strip(),
            "death": deaths.strip(),
            "assist": assists.strip(),
            "kda_ratio": kda_ratio,
            "kill_participation": kill_participation,
            "laning": laning_ratio,
            "cs": cs,
            "cs_per_min": cpm,
            "avg_tier": avg_tier_num
        }
        
        # Add teammates and opponents with display format
        for i, (team_list, prefix) in enumerate([(teammates, "team"), (opponents, "opp")]):
            for j, player in enumerate(team_list, 1):
                if j <= 5:  # Ensure we don't exceed 5 players per team
                    match_row[f"{prefix}mates{j}"] = convert_to_displayname(player["name"])
                    match_row[f"{prefix}_champ{j}"] = player["champion"]
                
        return match_row
    except Exception as e:
        print(f"Error processing match: {e}")
        return None

def get_matches_stats(region, username, max_retries=2):
    """
    Get match stats for a single player with retry mechanism
    """
    driver = None
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            driver = setup_driver()
            driver.set_page_load_timeout(20)  # Set page load timeout
            
            url = f"https://www.op.gg/summoners/{region}/{username}?queue_type=SOLORANKED"
            print(f"Accessing URL: {url}")
            driver.get(url)
            
            matches_container = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-1jxewmm.ek41ybw0"))
            )
            
            matches_data = []
            match_elements = matches_container.find_elements(By.CSS_SELECTOR, "div.css-j7qwjs.ery81n90")
            
            #print(f"Found {len(match_elements)} matches")
            
            for i, match in enumerate(match_elements, 1):
                try:
                    match_data = extract_match_data(match)
                    players = get_players_info(match)
                    match_data['match_date'] = get_tooltip_date(
                        driver, 
                        match.find_element(By.CSS_SELECTOR, "div.time-stamp > div")
                    )
                    
                    processed_data = process_match_data(match_data, username, players)
                    if processed_data:
                        matches_data.append(processed_data)
                except Exception as e:
                    print(f"Error processing match {i}: {e}")
                    continue
            
            if matches_data:
                return pd.DataFrame(matches_data)
            else:
                raise Exception("No valid matches found")
                
        except Exception as e:
            retry_count += 1
            print(f"Attempt {retry_count} failed: {e}")
            if retry_count <= max_retries:
                print(f"Retrying... ({retry_count}/{max_retries})")
                time.sleep(5)  # Wait 5 seconds before retrying
            else:
                print(f"Max retries reached")
                return pd.DataFrame()
                
        finally:
            if driver:
                driver.quit()
    
    return pd.DataFrame()

def get_multiple_matches_stats(players_df):
    """
    Get match stats for multiple players from a DataFrame
    
    Parameters:
    players_df: DataFrame with columns 'region' and 'username'
    """
    save_dir = "util/data"
    os.makedirs(save_dir, exist_ok=True)
    checkpoint_file = os.path.join(save_dir, "recent_matches_checkpoint.csv")
    all_matches_dfs = []
    error_players = []
    
    # Load checkpoint if exists
    start_idx = 0
    if os.path.exists(checkpoint_file):
        try:
            checkpoint_df = pd.read_csv(checkpoint_file)
            all_matches_dfs = [checkpoint_df]
            # Get the number of players already processed
            processed_players = set(checkpoint_df['player_id'])
            # Filter out already processed players
            players_df = players_df[~players_df['username'].isin(processed_players)]
            print(f"Loaded checkpoint with {len(processed_players)} players already processed")
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
    
    print(f"Processing matches for {len(players_df)} remaining players...")
    
    for idx, row in players_df.iterrows():
        region = row['region'].lower()  # Ensure region is lowercase
        username = row['username']
        
        try:
            # Format the username
            formatted_username = format_summoner_name(username)
            print(f"\nProcessing matches for player {idx + 1}/{len(players_df)}: {username} ({region})")
            #print(f"Formatted username: {formatted_username}")
            
            # Add delay between requests
            if idx > 0:
                time.sleep(2)
                
            matches_df = get_matches_stats(region, formatted_username)
            
            if matches_df is not None and not matches_df.empty:
                # Add player identification columns
                matches_df['player_id'] = username  # Original username
                matches_df['region'] = region
                all_matches_dfs.append(matches_df)
                print(f"Successfully processed matches for {username}")
                #print(f"Found {len(matches_df)} matches")

                 # Save checkpoint every 5 players
                if len(all_matches_dfs) % 5 == 0:
                    checkpoint_save = pd.concat(all_matches_dfs, ignore_index=True)
                    checkpoint_save.to_csv(checkpoint_file, index=False)
                    print(f"Saved checkpoint after processing {len(all_matches_dfs)} players")

            else:
                print(f"No match data found for {username}")
                error_players.append({
                    'region': region,
                    'username': username,
                    'formatted_username': formatted_username,
                    'error': 'No match data found'
                })
                
        except Exception as e:
            print(f"Error processing matches for {username}: {e}")
            error_players.append({
                'region': region,
                'username': username,
                'formatted_username': formatted_username if 'formatted_username' in locals() else 'Error in formatting',
                'error': str(e)
            })
            continue

    # Combine all match stats
    if all_matches_dfs:
        final_df = pd.concat(all_matches_dfs, ignore_index=True)
                
        filepath = os.path.join(save_dir, f"recent_matches.csv")
        final_df.to_csv(filepath, index=False)
        print(f"\nSaved combined match stats for {len(all_matches_dfs)} players to {filepath}")

        # Clean up checkpoint file
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            print("Removed checkpoint file after successful completion")
        
        # Save error log if any errors occurred
        if error_players:
            error_df = pd.DataFrame(error_players)
            error_filepath = os.path.join(save_dir, f"recent_matches_error.csv")
            error_df.to_csv(error_filepath, index=False)
            print(f"Saved error log to {error_filepath}")
        
        # Print summary
        print("\nSummary:")
        print(f"Total players processed: {len(players_df)}")
        print(f"Successful: {len(all_matches_dfs)}")
        print(f"Failed: {len(error_players)}")
        print(f"Total matches collected: {len(final_df)}")
        
        return final_df
    else:
        print("\nNo match data was collected")
        return None
    

