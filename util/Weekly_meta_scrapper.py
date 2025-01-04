import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helper import convert_percentage_to_decimal

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
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def get_weekly_meta():
    BASE_URL = "https://www.op.gg/statistics/champions?tier=challenger&period=week&mode=ranked"
    driver = setup_driver()
    
    try:
        driver.get(BASE_URL)
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content-container > div:nth-child(2) > table"))
        )
        
        # Extract table rows
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        # Define the column order
        columns = ["rank", "champion", "games", "KDA", "WR", "pick", "ban", "cs", "gold"]
        
        data = []
        for row in rows[1:]:  # Skip the header row
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells]
            
            if len(row_data) >= len(columns):
                # Remove ":1" from KDA format
                row_data[3] = row_data[3].replace(":1", "")
                # Convert WR, pick, and ban percentages to decimals
                row_data[4] = convert_percentage_to_decimal(row_data[4])
                row_data[5] = convert_percentage_to_decimal(row_data[5])
                row_data[6] = convert_percentage_to_decimal(row_data[6])
                # Remove commas from the gold values
                row_data[8] = int(row_data[8].replace(",", ""))
                
                data.append(row_data[:len(columns)])
        
        # Create a DataFrame with the extracted data
        df = pd.DataFrame(data, columns=columns)
        
        # Ensure the directory exists
        os.makedirs('./util/data', exist_ok=True)
        
        # Define the save path
        save_path = "./util/data/weekly_meta_stats.csv"
        
        # Automatically save the DataFrame to a CSV file in the specified directory
        df.to_csv(save_path, index=False)
        
        # Print confirmation message
        print(f"Saved weekly meta to {save_path}")
        
        return df
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        driver.quit()

# if __name__ == "__main__":
#     weekly_meta_data = get_weekly_meta()
    
#     if weekly_meta_data is not None:
#         print(weekly_meta_data)