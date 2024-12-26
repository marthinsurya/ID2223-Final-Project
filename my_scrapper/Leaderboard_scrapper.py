import os
import csv
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

# Setup ChromeDriver service
service = Service(ChromeDriverManager().install())

# Initialize WebDriver with the service and options
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define regions and pages to scrape
regions = ["kr", "na", "vn", "euw"]
pages_to_scrape = 5

# Define the output folder and ensure it exists
output_folder = os.path.join("ID2223-Final-Project", "my_scraper")
os.makedirs(output_folder, exist_ok=True)

# Define the full path to the output CSV file
output_file = os.path.join(output_folder, "leaderboard_data.csv")

# Open the CSV file for writing
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    
    # Write header row
    csv_writer.writerow([
        "summoner", "region", "rank", "tier", "lp", 
        "most_champion_1", "most_champion_2", "most_champion_3", 
        "level", "win", "loss", "winrate"
    ])

    for region in regions:
        for page in range(1, pages_to_scrape + 1):
            url = f"https://www.op.gg/leaderboards/tier?region={region}&type=ladder&page={page}"
            print(f"Scraping URL: {url}")

            # Access the webpage
            driver.get(url)

            try:
                # Wait for the leaderboard table to load
                table = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.css-1l95r9q.e4dns9u11"))
                )
                print("Table found!")

                # Find leaderboard table rows
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"Number of rows found for {region} page {page}:", len(rows))

                # Iterate through rows, skipping the header row
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 7:
                        summoner = cells[1].text.strip().replace("\n", " ")
                        rank = cells[0].text.strip()
                        tier = cells[2].text.strip()
                        lp = cells[3].text.strip()

                        # Extract champion names
                        champion_imgs = cells[4].find_elements(By.TAG_NAME, "img")
                        champions = [img.get_attribute("alt") for img in champion_imgs]
                        most_champion_1 = champions[0] if len(champions) > 0 else ""
                        most_champion_2 = champions[1] if len(champions) > 1 else ""
                        most_champion_3 = champions[2] if len(champions) > 2 else ""

                        level = cells[5].text.strip()
                        
                        # Parse win/loss and winrate
                        winrate_text = cells[6].text.strip()
                        wins, losses, winrate = "", "", ""
                        try:
                            win_loss = winrate_text.split("\n")
                            if len(win_loss) >= 2:
                                wins = win_loss[0][:-1].strip()  # Remove 'W'
                                losses = win_loss[1][:-1].strip()  # Remove 'L'
                            winrate = win_loss[-1].strip() if len(win_loss) > 2 else ""
                        except IndexError:
                            print("Error parsing win/loss data for row:", winrate_text)

                        # Write row to CSV
                        csv_writer.writerow([
                            summoner, region, rank, tier, lp, 
                            most_champion_1, most_champion_2, most_champion_3, 
                            level, wins, losses, winrate
                        ])
            except Exception as e:
                print(f"Error while parsing leaderboard data for {region} page {page}: {e}")
            
            # Add a delay between requests to avoid rate-limiting
            time.sleep(2)

# Quit the driver
driver.quit()

print(f"Leaderboard data saved to {output_file}")
