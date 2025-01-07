import os
import pandas as pd

def check_data_loading(file_path):
    """
    Debug function to check how the data is being loaded with proper encoding
    """
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin1', 'ISO-8859-1']
    
    for encoding in encodings:
        try:
            print(f"\nTrying encoding: {encoding}")
            
            # Read raw data first
            with open(file_path, 'r', encoding=encoding) as f:
                raw_lines = f.readlines()[:5]  # First 5 lines
            print("Raw data first 5 lines:")
            for line in raw_lines:
                print(line.strip())

            # Now read with pandas
            df = pd.read_csv(file_path, encoding=encoding)
            
            # Check champion-related columns
            champ_cols = [col for col in df.columns if '7d_champ' in col]
            print("\nChampion columns:")
            for col in champ_cols:
                print(f"\n{col} unique values:")
                print(df[col].value_counts().head())
                print(f"Data type: {df[col].dtype}")

            # Check specific row data
            print("\nSample row check:")
            sample_row = df.iloc[0]
            for col in ['7d_champ_1', '7d_champ_2', '7d_champ_3']:
                print(f"{col}: {sample_row[col]} (type: {type(sample_row[col])})")

            print(f"\nSuccessfully read file with {encoding} encoding")
            return df
            
        except UnicodeDecodeError:
            print(f"Failed to read with {encoding} encoding")
            continue
        except Exception as e:
            print(f"Error with {encoding} encoding: {str(e)}")
            continue
    
    raise ValueError("Could not read file with any of the attempted encodings")

# Use this function in your main code
try:
    #input_file = os.path.join("util", "data", f"player_stats_merged_2025-01-05_1.csv")
    input_file = os.path.join("util", "data", f"training_feature.csv")
    print(f"Checking file: {input_file}")
    df_check = check_data_loading(input_file)
    
    # Additional validation
    print("\nDataFrame Info:")
    print(df_check.info())
    
    print("\nSample of champion columns:")
    champ_cols = [col for col in df_check.columns if 'champ' in col.lower()]
    print(df_check[champ_cols].head())
    
except Exception as e:
    print(f"Error: {str(e)}")