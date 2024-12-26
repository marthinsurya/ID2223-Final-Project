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
url = "https://www.op.gg/summoners/kr/%EB%AF%BC%EC%B2%A0%EC%9D%B4%EC%97%AC%EC%B9%9C%EA%B5%AC%ED%95%A8-0415?queue_type=SOLORANKED"
mastery_url = "https://www.op.gg/summoners/kr/%EB%AF%BC%EC%B2%A0%EC%9D%B4%EC%97%AC%EC%B9%9C%EA%B5%AC%ED%95%A8-0415/mastery"

# Open the page
driver.get(url)

def get_recent_stats(stats_box):
    stats = stats_box.find_element(By.CSS_SELECTOR, "div.stats")
    recent_stats = stats.text.strip().split("\n")  # ['20G 13W 7L', '65%', '5.1 / 4.0 / 7.9', '3.25:1', 'P/Kill 50%']
    print(f"recent_stats: {recent_stats}")
    return recent_stats

def get_recent_champions(stats_box):
    champions = stats_box.find_element(By.CSS_SELECTOR, "div.champions")
    champion_elements = champions.find_elements(By.CSS_SELECTOR, "li")
    
    recent_champs_data = []
    for champion in champion_elements:
        # Extract champion name and image source
        img_tag = champion.find_element(By.TAG_NAME, "img")
        champ_name = img_tag.get_attribute("alt")
        img_url = img_tag.get_attribute("src").split(".png")[0]  # Remove the .png part
        
        # Extract win/lose stats and KDA
        win_lose = champion.find_element(By.CSS_SELECTOR, ".win-lose").text.strip()
        kda = champion.find_element(By.CSS_SELECTOR, ".css-1mz60y0.e1t9nk8i2").text.strip() if champion.find_elements(By.CSS_SELECTOR, ".css-1mz60y0.e1t9nk8i2") else ""

        # Print the extracted data
        print(f"Champion: {champ_name}")
        print(f"Image URL (without .png): {img_url}")
        print(f"Win/Loss: {win_lose}")
        print(f"KDA: {kda}")
        print("-" * 50)
        
        # Store in a list
        recent_champs_data.append({
            "champion": champ_name,
            "image_url": img_url,
            "win_loss": win_lose,
            "kda": kda
        })

    return recent_champs_data

def get_preferred_role(stats_box):
    # Find the positions section
    positions = stats_box.find_element(By.CSS_SELECTOR, "div.positions")
    role_elements = positions.find_elements(By.CSS_SELECTOR, "li")
    
    preferred_roles = {}
    for role in role_elements:
        # Extract role name from the img alt text
        role_name = role.find_element(By.CSS_SELECTOR, "div.position img").get_attribute("alt")
        
        # Extract the percentage from the height of the .gauge div
        percentage = role.find_element(By.CSS_SELECTOR, "div.gauge").get_attribute("style")
        
        # Debug output: Print raw percentage value
        print(f"Raw percentage for {role_name}: {percentage}")
        
        # If percentage style exists, clean and process the value
        if percentage:
            # Extract the numeric percentage part from the style attribute
            percentage_value = percentage.split(":")[1].strip().replace("%", "").strip(';')
            print(f"Cleaned percentage for {role_name}: {percentage_value}")  # Debug output
            
            # Try converting it to an integer
            try:
                percentage_int = int(percentage_value)
                preferred_roles[role_name] = percentage_int/100
            except ValueError:
                preferred_roles[role_name] = 0  # If conversion fails, set it to 0
        else:
            preferred_roles[role_name] = 0  # If no percentage is found, set it to 0
    
    # Debug output: Print the preferred roles dictionary before returning
    print(f"Preferred roles before return: {preferred_roles}")
    
    return preferred_roles

def get_season_heroes(season_hero_box):
    # Find all champion boxes inside the season hero box
    champion_boxes = season_hero_box.find_elements(By.CSS_SELECTOR, "div.champion-box")
    
    season_heroes = []
    for box in champion_boxes:
        try:
            # Extract champion name from div.name
            name_div = box.find_element(By.CSS_SELECTOR, "div.info div.name a")
            champ_name = name_div.text.strip()
            
            # Extract CS stats from div.cs
            cs_div = box.find_element(By.CSS_SELECTOR, "div.info div.cs")
            cs_stats = cs_div.text.strip()
            
            # Extract KDA ratio
            kda_ratio_div = box.find_element(By.XPATH, ".//div[@class='kda']//div[1]")
            kda_ratio = kda_ratio_div.text.strip()

            
            # Extract K/D/A average
            kda_detail_div = box.find_element(By.CSS_SELECTOR, "div.kda div.detail")
            kda_detail = kda_detail_div.text.strip()
            
            # Extract win rate
            win_rate_div = box.find_element(By.XPATH, ".//div[@class='played']//div[1]")
            win_rate = win_rate_div.text.strip()
            
            # Extract games played
            games_played_div = box.find_element(By.CSS_SELECTOR, "div.played div.count")
            games_played = games_played_div.text.strip()
            
            # Append the champion data as a dictionary
            season_heroes.append({
                "champion": champ_name,
                "cs_stats": cs_stats,
                "kda_ratio": kda_ratio,
                "kda_detail": kda_detail,
                "win_rate": win_rate,
                "games_played": games_played
            })
            
            # Debug: Print each champion's data
            print(f"Champion: {champ_name}")
            print(f"CS Stats: {cs_stats}")
            print(f"KDA Ratio: {kda_ratio}")
            print(f"KDA Detail: {kda_detail}")
            print(f"Win Rate: {win_rate}")
            print(f"Games Played: {games_played}")
            print("-" * 50)
        
        except Exception as e:
            print(f"Error processing champion box: {e}")
    
    return season_heroes

def get_7d_stats(ranked_7d_box):
    # Find the list of champions in the ranked 7d box
    champion_elements = ranked_7d_box.find_elements(By.CSS_SELECTOR, "ul li")
    
    weekly_stats = []
    
    for champion in champion_elements:
        try:
            # Extract champion name from div.name
            champ_name = champion.find_element(By.CSS_SELECTOR, "div.info > div.name > a").text.strip()

            # Use XPath to find the win and loss data
            try:
                # Extract wins and losses using XPath based on the position of the fill divs
                win_text = champion.find_element(By.XPATH, ".//div[@class='graph']//div[@class='text left']").text.strip()
                loss_text = champion.find_element(By.XPATH, ".//div[@class='graph']//div[@class='text right']").text.strip()
                
                # Extract the win and loss counts from the text
                wins = int(win_text.replace('W', '').strip()) if 'W' in win_text else 0
                losses = int(loss_text.replace('L', '').strip()) if 'L' in loss_text else 0
            except Exception as e:
                # If unable to find the specific elements, set wins and losses to 0
                print(f"Error finding win/loss data for {champ_name}: {e}")
                wins = 0
                losses = 0

            # Calculate total games
            total_games = wins + losses
            
            # Extract win rate from div.winratio
            try:
                win_rate_text = champion.find_element(By.CSS_SELECTOR, "div.winratio").text.strip()
                win_rate = float(win_rate_text.replace('%', '').strip()) if win_rate_text else 0
            except Exception as e:
                # If unable to find win rate, set it to 0
                print(f"Error finding win rate for {champ_name}: {e}")
                win_rate = 0
            
            # Append champion data to the list
            weekly_stats.append({
                "champion": champ_name,
                "total_games": total_games,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate
            })
            
            # Debug output: Print each champion's data
            print(f"Champion: {champ_name}, Wins: {wins}, Losses: {losses}, Total Games: {total_games}, Win Rate: {win_rate}%")
        
        except Exception as e:
            print(f"Error processing champion in 7d stats: {e}")
    
    return weekly_stats

def get_mastery_data(driver):
    try:
        # Locate the mastery container
        mastery_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content-container > div.box--desktop.dashboard--loading.css-7ruavw.erdn3wx2 > div > div"))
        )

        # Find all champions inside the mastery container
        champions = mastery_container.find_elements(By.CSS_SELECTOR, "div.css-8fea4f.e1poynyt1")

        mastery_data = []
        for champion in champions:
            # Extract the champion's name
            name = champion.find_element(By.CSS_SELECTOR, "strong.champion-name").text.strip()

            # Extract the champion's mastery points
            points = champion.find_element(By.CSS_SELECTOR, "div.champion-point span").text.strip()

            level = champion.find_element(By.CSS_SELECTOR, "div.champion-level__text span").text.strip()

            # Append the extracted data to the list
            mastery_data.append({
                "champion_name": name,
                "champion_points": points,
                "champion_level": level
            })

            # Debug: Print the extracted champion data
            print(f"Champion: {name}")
            print(f"Mastery Points: {points}")
            print(f"Champion Level: {level}")
            print("-" * 50)

        return mastery_data

    except Exception as e:
        print(f"Error scraping mastery data: {e}")
        return []




try:
    # Wait until the main container is visible
    main_container = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#content-container"))
    )
   
    # Inside the main container, navigate to the stats box
    stats_box = main_container.find_element(By.CSS_SELECTOR, "div.css-fkbae7.er95z9k0 > div.stats-box.stats-box--SOLORANKED.css-1egz98l.e1t9nk8i0")
    season_hero_box = main_container.find_element(By.CSS_SELECTOR, "div.css-1xs6mqa.e1b7nks50 > div:nth-child(1) > div.css-18w3o0f.elcihb00")
    ranked_7d_box = main_container.find_element(By.CSS_SELECTOR, "div.css-1xs6mqa.e1b7nks50 > div:nth-child(1) > div.css-1v1ie3n.efsztyx0")


    # Extract stats
    recent_stats = get_recent_stats(stats_box)
    
    # Extract champions recent 20
    recent_champs_data = get_recent_champions(stats_box)

    # Extract preferred roles
    preferred_roles = get_preferred_role(stats_box)
    
    print("Preferred roles with percentages:")
    for role, percentage in preferred_roles.items():
        print(f"{role}: {percentage}")

    # Extract season heroes
    season_heroes = get_season_heroes(season_hero_box)

    ranked_7d = get_7d_stats(ranked_7d_box)

    driver.get(mastery_url)

    # Extract mastery data
    mastery_data = get_mastery_data(driver)

    # Debug: Print the extracted mastery data
    print("Mastery Data:")
    for data in mastery_data:
        print(f"Champion: {data['champion_name']}, Mastery Points: {data['champion_points']}")


    

except Exception as e:
    print(f"Error scraping stats data: {e}")

time.sleep(2)  # Add a delay to avoid rate-limiting

# Quit the driver
driver.quit()

