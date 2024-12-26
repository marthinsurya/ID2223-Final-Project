import csv
import time
import requests
from urllib.parse import quote

# Input file path
input_file = "ID2223-Final-Project/my_scraper/lb_challenger_only.csv"

# List to store failed summoner names
failed_summoners = []

# Function to check if the URL is accessible
def check_connection(region, summoner):
    # Format the summoner name: Replace spaces with '-' and '#' with '-'
    formatted_summoner = summoner.replace(" ", "-").replace("#", "-")
    
    # Encode the summoner name to handle special characters like Korean or other symbols
    formatted_summoner = quote(formatted_summoner)
    
    # Construct the full URL: region is correctly placed before the summoner name
    url = f"https://www.op.gg/summoners/{region}/{formatted_summoner}?queue_type=SOLORANKED"
    
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the response status is 200 (OK)
        if response.status_code == 200:
            print(f"Connection successful to {url}")
            return True
        else:
            print(f"Failed to connect to {url}. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        return False

# Open the input CSV file
with open(input_file, mode="r", encoding="utf-8") as infile:
    csv_reader = csv.reader(infile)
    header = next(csv_reader)  # Skip the header row
    
    # Process each row in the CSV file
    for row in csv_reader:
        region = row[1].strip()  # Get region from the first column
        summoner = row[0].strip()  # Get summoner name from the second column
        
        # Check connection for the region and summoner
        if not check_connection(region, summoner):
            failed_summoners.append(summoner)
        
        # Pause for a short time between requests to avoid overloading the server
        time.sleep(2)

# Print out failed summoner names if any
if failed_summoners:
    print("\nFailed to connect to the following summoners:")
    for summoner in failed_summoners:
        print(summoner)
else:
    print("\nAll connections were successful.")

print("Connection check completed.")
