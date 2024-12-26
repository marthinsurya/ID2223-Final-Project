import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

# Setup WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the URL
player_url = "https://www.op.gg/summoners/kr/%EB%AF%BC%EC%B2%A0%EC%9D%B4%EC%97%AC%EC%B9%9C%EA%B5%AC%ED%95%A8-0415?queue_type=SOLORANKED"

# Open the page
driver.get(player_url)

def get_recent_match():
    # Wait until the main container is visible
    main_container = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#content-container"))
    )
   
    # Inside the main container, navigate to the stats box
    recent_match_box = main_container.find_element(By.CSS_SELECTOR, "div.css-fkbae7.er95z9k0 > div.css-1jxewmm.ek41ybw0")

    try:
        # Inside the recent match box, wait until the match results are available
        recent_matches = []

        # Process each child under div.css-1jxewmm.ek41ybw0
        match_elements = recent_match_box.find_elements(By.CSS_SELECTOR, "div.css-j7qwjs.ery81n90")
        for match in match_elements:
            game_type = match.find_element(By.CSS_SELECTOR, "div.game-type").text
            time_stamp = match.find_element(By.CSS_SELECTOR, "div.time-stamp").text
            result = match.find_element(By.CSS_SELECTOR, "div.result").text
            length = match.find_element(By.CSS_SELECTOR, "div.length").text
            kda = match.find_element(By.CSS_SELECTOR, "div.kda").text
            kda_ratio = match.find_element(By.CSS_SELECTOR, "div.kda-ratio").text
            cs = match.find_element(By.CSS_SELECTOR, "div.cs").text
            avg_tier = match.find_element(By.CSS_SELECTOR, "div.avg-tier").text
            laning = match.find_element(By.CSS_SELECTOR, "div.laning").text.replace('\n', '') # show lane performance first 14 mins
            kill_participation = match.find_element(By.CSS_SELECTOR, "div.p-kill").text

            champion_img = match.find_element(By.CSS_SELECTOR, "div.info a.champion img")
            champion_name = champion_img.get_attribute("alt")
            champion_level = match.find_element(By.CSS_SELECTOR, "div.info a.champion span.champion-level").text

            game_tags_container = match.find_element(By.CSS_SELECTOR, "div.game-tags__scroll-container div.game-tags")
        
             # Extract the game tags from div elements
            tag_elements = game_tags_container.find_elements(By.CSS_SELECTOR, "div.tag")
            tags = [tag.text for tag in tag_elements]
            
            # Extract the game tags from button elements
            badge_elements = game_tags_container.find_elements(By.CSS_SELECTOR, "button.OPScoreBadge div.badge")
            badges = [badge.text for badge in badge_elements]
            
            # Check if there is a kill-tag
            tags += badges

            player_elements = recent_match_box.find_elements(By.CSS_SELECTOR, "div.css-86ve5u.e1xevas20 > div.css-pp7uqb.e1xevas21")
        
            # Extract information for up to 10 players
            players_info = []
            for player in player_elements[:10]:
                champion_img = player.find_element(By.CSS_SELECTOR, "div.icon img")
                champion_name = champion_img.get_attribute("alt")  # Get the 'alt' attribute which contains the champion's name
                
                summoner_link = player.find_element(By.CSS_SELECTOR, "div.name a")
                href = summoner_link.get_attribute("href")  # Get the 'href' attribute
                region, name = href.split('/')[-2], href.split('/')[-1]  # Extract the region and name from the URL
                
                players_info.append({
                    "champion": champion_name,
                    "region": region,
                    "name": name
                })

            recent_matches.append({
                "game_type": game_type,
                "time_stamp": time_stamp,
                "result": result,
                "length": length,
                "champion": champion_name,
                "level": champion_level,
                "kda": kda,
                "kda_ratio": kda_ratio,
                "laning": laning,
                "kill_participation": kill_participation,
                "cs": cs,
                "avg_tier": avg_tier,
                "game_tags": tags,
                "players": players_info
            })
        
        return recent_matches

    except Exception as e:
        print(f"Error processing recent match data: {e}")
        return []

try:
    # Extract recent match data
    recent_game_results = get_recent_match()
    first_game_result = recent_game_results[0]
    for key, value in first_game_result.items():
        print(f"{key}: {value}")
    

except Exception as e:
    print(f"Error scraping stats data: {e}")

time.sleep(2)  # Add a delay to avoid rate-limiting

# Quit the driver
driver.quit()