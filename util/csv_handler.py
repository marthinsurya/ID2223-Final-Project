import pandas as pd
from pathlib import Path
from datetime import datetime
import os

def append_and_deduplicate(filepath):
    """
    Handles appending and deduplication of CSV files using existing date column.
    Assumes date format like "Sat, Jan 4, 2025 12:20 AM"
    """
    try:
        # Get the newly saved data
        new_df = pd.read_csv(filepath)
        
        # Convert the date strings to datetime objects for proper sorting
        new_df['datetime'] = pd.to_datetime(new_df['date'], format='%a, %b %d, %Y %I:%M %p')
        
        # Create a temporary file path
        temp_filepath = filepath + '.temp'
        
        # Save the new data to temp file
        new_df.to_csv(temp_filepath, index=False)
        
        # Check if we have a historical file
        historical_filepath = filepath.replace('.csv', '_historical.csv')
        
        if os.path.exists(historical_filepath):
            # Read historical data
            historical_df = pd.read_csv(historical_filepath)
            
            # Convert historical dates to datetime for consistent comparison
            historical_df['datetime'] = pd.to_datetime(historical_df['date'], format='%a, %b %d, %Y %I:%M %p')
            
            # Append new data
            merged_df = pd.concat([historical_df, new_df], ignore_index=True)
            
            # Remove duplicates based on all columns that make a record unique
            # Adjust these columns based on what defines a unique record in your dataset
            dedup_columns = ['player_id', 'region', 'date', 'champion']
            merged_df = merged_df.drop_duplicates(
                subset=dedup_columns,
                keep='last'
            )
            
            # Sort by datetime
            merged_df = merged_df.sort_values('datetime', ascending=False)
            
            # Drop the temporary datetime column before saving
            merged_df = merged_df.drop('datetime', axis=1)
            
            # Save merged data
            merged_df.to_csv(historical_filepath, index=False)
        else:
            # If no historical file exists, create it with the new data
            new_df = new_df.drop('datetime', axis=1)  # Remove temporary datetime column
            new_df.to_csv(historical_filepath, index=False)
            
        # Clean up temp file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            
        print(f"Successfully updated historical data at {historical_filepath}")
        
    except Exception as e:
        print(f"Error in append_and_deduplicate: {e}")


if __name__ == "__main__":
    main()