import time
import re
import os
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Constants
ROLES = ["top", "jungle", "mid", "adc", "support"]
BASE_URL = "https://www.op.gg/champions?position={role}"
TIER_COLOR_MAPPING = {
    "#0093FF": 1,  # Blue
    "#00BBA3": 2,  # Teal
    "#FFB900": 3,  # Yellow
    "#9AA4AF": 4,  # Gray
}

def setup_driver():
    """Setup and return a configured Chrome WebDriver with optimized settings"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    
    # Remove log_level parameter from ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def parse_rate(rate_str):
    """Convert percentage string to float"""
    try:
        return float(rate_str.strip().rstrip('%')) / 100
    except:
        return 0.0

def extract_counter_champions(counter_column):
    """Extract counter champions from column"""
    counter_champions = []
    try:
        counter_list = counter_column.find_elements(By.TAG_NAME, "a")
        for counter in counter_list[:3]:
            img_element = counter.find_element(By.TAG_NAME, "img")
            champion_name = img_element.get_attribute("alt")
            counter_champions.append(champion_name)
    except Exception:
        pass
    return counter_champions + [""] * (3 - len(counter_champions))

def get_champion_table_data(driver, url, role):
    """Extract champion data from a specific role page with optimized parsing"""
    try:
        driver.get(url)
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content-container > div.flex.gap-2.md\\:mx-auto.md\\:w-width-limit.mt-2.flex-col.overflow-hidden > div.flex.flex-row-reverse.gap-2 > main > div:nth-child(2) > table"))
        )

        champions_data = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) <= 1:
                continue

            # Get tier value
            tier_element = cols[2].find_element(By.TAG_NAME, "svg")
            tier = 5
            if tier_element:
                for path in tier_element.find_elements(By.TAG_NAME, "path"):
                    fill_color = path.get_attribute("fill")
                    if fill_color in TIER_COLOR_MAPPING:
                        tier = TIER_COLOR_MAPPING[fill_color]
                        break

            # Extract ban rate
            ban_rate_html = cols[6].get_attribute("innerHTML").strip()
            ban_rate_match = re.search(r"([\d.]+)", ban_rate_html.replace("<!-- -->", ""))
            ban_rate = float(ban_rate_match.group(1)) / 100 if ban_rate_match else 0.0

            # Get counter champions
            counter1, counter2, counter3 = extract_counter_champions(cols[7])

            champions_data.append({
                "rank": cols[0].text.strip(),
                "champion": cols[1].text.strip(),
                "tier": tier,
                "role": role,
                "win_rate": parse_rate(cols[4].text),
                "pick_rate": parse_rate(cols[5].text),
                "ban_rate": ban_rate,
                "counter1": counter1,
                "counter2": counter2,
                "counter3": counter3,
            })

        return champions_data

    except Exception as e:
        print(f"Error extracting table data for {role}: {e}")
        return []

def get_meta_stats():
    """Main function to scrape champion data with improved error handling and logging"""
    driver = None
    
    try:
        driver = setup_driver()
        all_roles_data = []

        for role in ROLES:
            role_url = BASE_URL.format(role=role)
            role_data = get_champion_table_data(driver, role_url, role)
            all_roles_data.extend(role_data)

        if not all_roles_data:
            print("No data was collected from any role")
            return pd.DataFrame()

        df = pd.DataFrame(all_roles_data)
        
        # Save data
        save_dir = os.path.join("ID2223-Final-Project", "my_scrapper", "data")
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, "meta_stats.csv")
        df.to_csv(filepath, index=False)

        return df

    except Exception as e:
        print(f"Error in get_meta_stats: {e}")
        return pd.DataFrame()

    finally:
        if driver:
            driver.quit()

# example
df = get_meta_stats()
    