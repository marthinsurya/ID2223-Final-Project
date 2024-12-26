import time
import re
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

def get_champion_table_data(driver, url, role):
    try:
        # Open the page
        driver.get(url)

        # Wait for the table to load
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content-container > div.flex.gap-2.md\\:mx-auto.md\\:w-width-limit.mt-2.flex-col.overflow-hidden > div.flex.flex-row-reverse.gap-2 > main > div:nth-child(2) > table"))
        )

        # Find all rows in the table
        rows = table.find_elements(By.TAG_NAME, "tr")

        # Store the data
        champions_data = []

        # Define the color to tier mapping
        tier_color_mapping = {
            "#0093FF": 1,  # Blue
            "#00BBA3": 2,  # Teal
            "#FFB900": 3,  # Yellow
            "#9AA4AF": 4,  # Gray
        }

        for row in rows:
            # Extract columns from each row
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 1:  # Ensure the row contains enough data (i.e., not a header or empty row)
                # Extract data from each column
                rank = cols[0].text.strip()
                champion = cols[1].text.strip()

                # Extract the tier (SVG-based) from the third column
                tier_element = cols[2].find_element(By.TAG_NAME, "svg")
                tier = 5  # Default tier value if no matching color found

                if tier_element:
                    # Get the fill color of the SVG path to determine tier
                    path_elements = tier_element.find_elements(By.TAG_NAME, "path")
                    for path in path_elements:
                        fill_color = path.get_attribute("fill")
                        if fill_color in tier_color_mapping:
                            tier = tier_color_mapping[fill_color]
                            break  # If a matching color is found, use it and stop

                # Extract win rate and pick rate (fixed column order)
                win_rate = cols[4].text.strip()
                pick_rate = cols[5].text.strip()
                ban_rate_html = cols[6].get_attribute("innerHTML").strip()
                
                ban_rate_match = re.search(r"([\d.]+)%", ban_rate_html.replace("<!-- -->", ""))

                if ban_rate_match:
                    # Extract the number if a match is found
                    ban_rate = ban_rate_match.group(1)
                else:
                    ban_rate = "N/A" 

                 # Extract counters (champions)
                counter_champions = []
                counter_column = cols[7]  # The column for counters
                counter_list = counter_column.find_elements(By.TAG_NAME, "a")
               
                for counter in counter_list[:3]:  # Get only the first 3 counters
                    try:
                        img_element = counter.find_element(By.TAG_NAME, "img")  # Find the <img> tag
                        champion_name = img_element.get_attribute("alt")  # Extract the alt attribute
                        counter_champions.append(champion_name)  # Add to the list
                    except Exception as e:
                        print(f"Error extracting counter champion: {e}")

                # Store the extracted data
                champions_data.append({
                    "rank": rank,
                    "champion": champion,
                    "tier": tier,
                    "role": role,  # Add role to the data
                    "win_rate": win_rate,
                    "pick_rate": pick_rate,
                    "ban_rate": ban_rate,
                    "counter1": counter_champions[0] if len(counter_champions) > 0 else "",
                    "counter2": counter_champions[1] if len(counter_champions) > 1 else "",
                    "counter3": counter_champions[2] if len(counter_champions) > 2 else ""                    
                })

        return champions_data

    except Exception as e:
        print(f"Error extracting table data for {role}: {e}")
        return []

# Define the roles and corresponding URLs
roles = ["top", "jungle", "mid", "adc", "support"]
base_url = "https://www.op.gg/champions?position={role}"

all_roles_data = []

try:
    # Loop through each role and collect data
    for role in roles:
        role_url = base_url.format(role=role)
        print(f"Scraping data for role: {role}")
        role_data = get_champion_table_data(driver, role_url, role)
        all_roles_data.extend(role_data)

    # Debug: Print all collected data
    print("\nAll Roles Data:")
    for data in all_roles_data:
        print(data)

except Exception as e:
    print(f"Error scraping data for all roles: {e}")

# Wait before quitting to ensure the script completes
time.sleep(2)

# Quit the driver
driver.quit()
