import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_leaderboards(regions=None, pages_per_region=5, output_file=None, delay=2):
    """
    Scrape leaderboard data from op.gg for specified regions and return as DataFrame.
    
    Args:
        regions (list): List of regions to scrape. Defaults to ["kr", "na", "vn", "euw"]
        pages_per_region (int): Number of pages to scrape per region. Defaults to 5
        output_file (str): Path to output file. Defaults to "util/data/leaderboard_data.csv"
        delay (int): Delay between requests in seconds. Defaults to 2
    
    Returns:
        pandas.DataFrame: Scraped leaderboard data
    """
    # Set defaults
    if regions is None:
        regions = ["kr", "na", "vn", "euw"]
    
    if output_file is None:
        output_file = os.path.join("util", "data", "leaderboard_data.csv")
    
    # Initialize data list to store rows
    leaderboard_data = []

    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # Initialize WebDriver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        for region in regions:
            print(f"\nScraping {region.upper()} region...")
            for page in range(1, pages_per_region + 1):
                print(f"Processing page {page}/{pages_per_region}")
                url = f"https://www.op.gg/leaderboards/tier?region={region}&type=ladder&page={page}"
                
                try:
                    # Access the webpage
                    driver.get(url)

                    # Wait for table to load
                    table = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.css-1l95r9q.e4dns9u11"))
                    )

                    # Process rows
                    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
                    for row in rows:
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 7:
                                # Extract basic data
                                summoner = cells[1].text.strip().replace("\n", " ")
                                rank = cells[0].text.strip()
                                tier = cells[2].text.strip()
                                lp = cells[3].text.strip()
                                level = cells[5].text.strip()

                                # Extract champion data
                                champion_imgs = cells[4].find_elements(By.TAG_NAME, "img")
                                champions = [img.get_attribute("alt") for img in champion_imgs]
                                champion_data = champions + [""] * (3 - len(champions))

                                # Parse win/loss data
                                winrate_text = cells[6].text.strip().split("\n")
                                wins = winrate_text[0].rstrip("W") if len(winrate_text) > 0 else ""
                                losses = winrate_text[1].rstrip("L") if len(winrate_text) > 1 else ""
                                winrate = winrate_text[2] if len(winrate_text) > 2 else ""

                                # Append row data
                                leaderboard_data.append({
                                    "summoner": summoner,
                                    "region": region,
                                    "rank": rank,
                                    "tier": tier,
                                    "lp": lp,
                                    "most_champion_1": champion_data[0],
                                    "most_champion_2": champion_data[1],
                                    "most_champion_3": champion_data[2],
                                    "level": level,
                                    "win": wins,
                                    "loss": losses,
                                    "winrate": winrate
                                })

                        except Exception as e:
                            print(f"Error processing row in {region} page {page}: {e}")
                            continue

                except Exception as e:
                    print(f"Error processing {region} page {page}: {e}")
                    continue

                time.sleep(delay)

    except Exception as e:
        print(f"Fatal error: {e}")
        return None

    finally:
        driver.quit()

    # Create DataFrame
    df = pd.DataFrame(leaderboard_data)
    
    # Clean and convert data types
    df['lp'] = df['lp'].str.replace(',', '').str.replace('LP', '').astype(float)
    df['level'] = df['level'].astype(int)
    df['win'] = pd.to_numeric(df['win'], errors='coerce')
    df['loss'] = pd.to_numeric(df['loss'], errors='coerce')
    df['winrate'] = df['winrate'].str.rstrip('%').astype(float) / 100
    
    # Save to CSV if output_file is specified
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"Leaderboard data saved to {output_file}")

    return df