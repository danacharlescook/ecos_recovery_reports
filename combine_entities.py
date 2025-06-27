# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 12:41:40 2025

@author: dcook
"""

import os
import pandas as pd

# Path to the folder containing the indiviudal csv files

csv_folder = r"C:\Users\dcook\OneDrive - Defenders of Wildlife\Desktop\csv_outputs"
combined_data = []

# loop through all csvs named like entity_x.csv

for filename in os.listdir(csv_folder):
    if filename.startswith("entity_") and filename.endswith(".csv"):
        filepath = os.path.join(csv_folder, filename)
        try:
            df = pd.read_csv(filepath)
            # extract entity_id from the file name
            entity_id = filename.replace("entity_", "").replace(".csv", "")
            df["entity_id"] = entity_id
            combined_data.append(df)
            print(f"Added: {filename}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
# combine and save

if combined_data:
    combined_df = pd.concat(combined_data, ignore_index=True)
    combined_csv_path = os.path.join(csv_folder, "combined_entities.csv")
    combined_df.to_csv(combined_csv_path, index=False)
    print(f"Combined CSV daved as: {combined_csv_path}")
else:
    print("No matching CSV files found")
    
    
    
    


    
    
    
    
    
    
    
    
    
    
    



