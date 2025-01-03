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
from helper import convert_to_minutes, convert_percentage_to_decimal, convert_tier_to_number, convert_result_to_binary

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
            players.append({"champion": champion, "region": region, "name": name})
        return players
    except: return []

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
        player_index = next((i for i, p in enumerate(players) if unquote(p['name']) == username), -1)
        team = "blue" if player_index < 5 else "red"
        teammates = players[:5] if player_index < 5 else players[5:]
        opponents = players[5:] if player_index < 5 else players[:5]
        
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
            "player_id": username,
            "date": match_data.get("match_date", ""),
            "champion": match_data.get("champion_img", ""),
            "level": match_data.get("champion_level", ""),
            "team": team,
            "result": result_num,
            "match_length_mins": match_length_mins, 
            "kill": kills.strip(),  # Ensure no whitespace
            "death": deaths.strip(),  # Ensure no whitespace
            "assist": assists.strip(),  # Ensure no whitespace
            "kda_ratio": kda_ratio,
            "kill_participation": kill_participation,
            "laning": laning_ratio,
            "cs": cs,
            "cs_per_min": cpm,
            "avg_tier": avg_tier_num
        }
        
        # Add teammates and opponents
        for i, (team_list, prefix) in enumerate([(teammates, "team"), (opponents, "opp")]):
            for j, player in enumerate(team_list[:5], 1):
                match_row[f"{prefix}mates{j}"] = player["name"]
                match_row[f"{prefix}_champ{j}"] = player["champion"]
                
        return match_row
    except Exception as e:
        print(f"Error processing match: {e}")
        return None

def get_matches_stats(region, username):
    driver = None
    try:
        driver = setup_driver()
        driver.get(f"https://www.op.gg/summoners/{region}/{username.replace(' ', '%20')}?queue_type=SOLORANKED")
        
        matches_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-1jxewmm.ek41ybw0"))
        )
        
        matches_data = []
        match_elements = matches_container.find_elements(By.CSS_SELECTOR, "div.css-j7qwjs.ery81n90")
        
        for match in match_elements:
            match_data = extract_match_data(match)
            players = get_players_info(match)
            match_data['match_date'] = get_tooltip_date(driver, match.find_element(By.CSS_SELECTOR, "div.time-stamp > div"))
            
            processed_data = process_match_data(match_data, username, players)
            if processed_data:
                matches_data.append(processed_data)
        
        if matches_data:
            df = pd.DataFrame(matches_data)
            save_path = os.path.join("my_scrapper", "data", "recent_matches.csv")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            df.to_csv(save_path, index=False)
            print(f"Saved recent matches stats to {save_path}")
            return df
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver:
            driver.quit()
    return pd.DataFrame()