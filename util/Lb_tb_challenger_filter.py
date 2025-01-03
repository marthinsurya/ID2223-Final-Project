import csv
import os

# File paths
input_file = "ID2223-Final-Project/my_scraper/leaderboard_data.csv"
output_file = "ID2223-Final-Project/my_scraper/lb_challenger_only.csv"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Open the input and output files
with open(input_file, mode="r", encoding="utf-8") as infile, open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
    csv_reader = csv.reader(infile)
    csv_writer = csv.writer(outfile)

    # Read the header row
    header = next(csv_reader)
    csv_writer.writerow(header)  # Write header to output file

    # Filter rows where 'tier' is "Challenger"
    tier_index = header.index("tier")  # Get the index of the 'tier' column
    for row in csv_reader:
        if row[tier_index].strip().lower() == "challenger":
            csv_writer.writerow(row)

print(f"Filtered data saved to {output_file}")
