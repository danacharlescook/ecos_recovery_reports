# -*- coding: utf-8 -*-
"""
Created on Tue May 27 15:58:04 2025

@author: dcook
"""
                  
import os # Provides functions to interact with the operating system, paths and folders
import time #Allows the script to pause for a certain number of seconds
import shutil # Useful for file operations like moving or copying files
import subprocess
from selenium import webdriver # Allows you to control the browser
from selenium.webdriver.common.by import By # Used to specify how to locate elements on the page
from selenium.webdriver.chrome.service import Service # Lets you specify the path to your chromdriver executable
from selenium.webdriver.chrome.options import Options # Lets you configure how Chrome behaves (download preferences)
from selenium.common.exceptions import NoSuchElementException, TimeoutException # Allow the script to handle errors when elements aren't found or time out
from selenium.webdriver.support.ui import WebDriverWait # Used to wait for certain elements or conditions on a page before interacting with them
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs # Allows the script to extract parts of a URL like query parameters (used later to get documentId and entityId from the report URL)


# Set up Chrome options
download_dir = r"C:\Users\dcook\OneDrive - Defenders of Wildlife\Desktop\recovery_project\csv_outputs" # sets download_dir as the absolute path to the csv_outputs folder
# ensures the path is valid and fully resolved regardless of where the script is run
options = Options() # Creates an Options object to customize Chrome behavior 
options.add_experimental_option("detach", True)  # Keep browser open after script ends

# This next block sets preferences for chrome
options.add_experimental_option("prefs", { 
    "download.default_directory": download_dir, # Sets where downloaded files should go
    "download.prompt_for_download": False, # Prevents Chrome from asking the user where to save each file
    "download.directory_upgrade": True, # Allows Chrome to create the directory if it doesn't exist
    "safebrowsing.enabled": True # Enables Chrome's Safe Browsing feature to help detect potentially dangerous files
})


# Set path to your chromedriver executable
# This creates a Service object that tells Selenium where to find the ChromeDriver executable
service = Service(r"C:\\Users\\dcook\\OneDrive - Defenders of Wildlife\\Desktop\\chromedriver.exe") 
# launches a new Chrome browser instance using
# The srvice 
# the options configured earlier (like the default download folder and detachment bahvior)
driver = webdriver.Chrome(service=service, options=options)

# Ensure the output folder exists before downloads begin
os.makedirs(download_dir, exist_ok=True)

# Sample entity IDs (you can adjust this list as needed)
entity_ids = [5895, 8256, 2212, 1392, 1392]  # Add more as needed

# === Main Script ===
# Begins a loop that processes each entityId from the entity_ids list
for entity_id in entity_ids:
    # Prints a message to indicate which entity ID is currently being processed (adds a new line for clarity in console output)
    print(f"\nChecking entity ID: {entity_id}")
    # Starts a try block to catch and handle errors during the processing of each entity (useful for when some pages are missing or load incorrectly)
    try:
        # Step 1: Constructs the URL to the species profile page for the current entity_id
        profile_url = f"https://ecos.fws.gov/ecp/species/{entity_id}"
        # Uses Selenium to navigate the chrome browser to that page
        driver.get(profile_url)

        # Step 2: Find all "View Implementation Progress" links
        links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, "View Implementation Progress"))
        )
        # Waits (up to 10 seconds) for all links on the page that contain the partial text "View Implementation progress" to appear
        
        if links:
            href = links[0].get_attribute("href")
            driver.get(href)
            # If more than one "View Implementation progress" links are found, 
            # retireve the href (url) from the first link
            # navigate the browser to that URL
        else:
            print(f"No implementation progress link found for entityId {entity_id}")
            continue
            # If no matching links are found, print a warning message
            # The continue statement skips the rest of the loop for this entity ID and goes to the next one
            
        # Step 3: Parse the link to get documentId and entityId
        parsed_url = urlparse(href)
        # Uses Python's urlparse function to split the report URL (href) into its components (scheme, domain, path, query string)
        
        query_params = parse_qs(parsed_url.query)
        # Extracts the query parameters from the parsed URL and stores them in a dictionary
        
        document_id = query_params.get("documentId", [None])[0]
        # Extracts the dicumentId and entityId values from the dictionary
        
        true_entity_id = query_params.get("entityId", [None])[0]
        # Uses [0] to get the first item in the list (since parse_qs always returns lists as values)
        # defaults to None if either key is missing to avoid a crash
        
        if not document_id or not true_entity_id:
            print(f"Could not parse documentId or entityId from link for {entity_id}")
            continue
        # Checks if either document_id or true_entity_id wasn't found (i.e still None)
        # If so it prints an error message and skips to the next entity_id in the loop
        
        
        # Step 4: Visit the report page
        report_url = f"https://ecos.fws.gov/ecp0/reports/implementation-activity-status-ore-report?documentId={document_id}&entityId={true_entity_id}"
        driver.get(report_url)
        # Constructs the full URL to the implementation report using the previously extracted document_id and true_entity_id
        # Instructs Selenium's browsesr instnace (driver) to navigate to that URL
        
        # Step 5: Click the CSV button
        csv_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'CSV')]"))
        )
        # Waits up to 10 seconds for the CSV download button to appear and be clickable
        # Uses XPath to look for any <psan> element that contains the text "CSV"
        # This ensures the script doesn't try to click before the page has fully loaded
    
        
        csv_button.click()
        # Clicks the CSV button to trigger the download of the implementation report data as a .csv file
        # The file will be saved to the csv_outputs folder defined earlier via the Chrome options
    
        print(f"CSV download triggered for entity ID {true_entity_id}.")
        # Prints a confirmation message in the console to indicate that the donwload has started for that particular entity

        # Step 6: Wait and rename the most recent "Report Results" file
        time.sleep(5)  # Wait for download to complete
        # This pauses teh script for 5 seconds to give the browser enough time to download the CSV file after clicking the "CSV" button
        # Downloads are not instant. Without this pause the script might check for the file before it finishes downloading
        
        files = [f for f in os.listdir(download_dir) if f.startswith("Report Results")]
        # Scans the csv_outputs folder to find files that sart with the name "Reports Results"
        # Chrome names files based on the page title or donwload content, and these files are named "Reports Results.csv"
        
        if not files:
            
            print(f"No CSV file found after download for entity {true_entity_id}")
            continue
            # If no CSV files were found, the script logs a message and skips to the next entity ID
            # Prevents the script from breaking or performing further actions when there is no file to process

        latest_file = max(
            [os.path.join(download_dir, f) for f in files],
            key=os.path.getctime
        )
        # Among all "Report Results" files, this selects the mosrt recently created one
        # os.path.getctime() fetched the file creation time
        # max() finds the file with the newest timestamp
        # If multiple report files already exist, this ensures you rename or prcess the newest one, avoiding mix-ups with earlier downloads

        new_filename = f"entity_{true_entity_id}.csv"
        # Creates a new filename using the entity ID (e.g entity_2262.csv)
        # Gives the file a meaningful and unique name tied to the entity, so you can easilty identify it later
        
        new_filepath = os.path.join(download_dir, new_filename)
        # Constructs the full path to where the renamed file should go (still within the csv_outputs folder)
        # Keeps everything organiaed and ensures that the move target is valid

        shutil.move(latest_file, new_filepath)
        # Renames the donwloaded csv file (latest file) by moving it to the new path with the new name
        # shutil.move is used here as a simple way to both rename and relocate files in one step
        # The file orginially named something like "Report Results (2).csv" becomes "entity_2262.csv"
        
        print(f"Renamed '{os.path.basename(latest_file)}' to '{new_filename}'")
        # Logs what just happened- shows the original name and the new name of the file
        # Good for debugging and tracking progress when processing many entity IDs
        

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error processing entityId {entity_id}: {e}")
        # This handles specific errors that can happen during Selenium browser automation
        # NoSuchElemetException is raised when an element (like a link or button) can't be found on the page
        # TimeoutException is raised when Selenium waits too long for something to appear (like the csv button) and doesn't show up in time.
        # These are common issues in web scraping and catching them prevents the script from crashing completely when on entity fails
        # If one of these errors occurs while processing a particular entity_id, the script logs the problem and moves on to the next one instead of stopping
        
    except Exception as e:
        print(f"Unexpected error for entityId {entity_id}: {e}")
        # This is a catch-all for any other unexpected errors like network issues, permission errors, or unhandled logic problems
        # Logs a message witht he entity ID and error message, then continues with the rest of the script
        

print("\nAll done. Check the 'csv_outputs' folder.")


# run the second script after download completes
combine_script_path = os.path.abspath("C:\\Users\\dcook\\OneDrive - Defenders of Wildlife\\Desktop\\recovery_project\\combine_entities.py")
subprocess.run(["python", combine_script_path], check=True)



'''
entity_ids = [
    2262, 1063, 5507, 6617, 6617, 466, 6988, 6988, 6738, 6523, 5741, 4970, 3646,
    7738, 5225, 209, 8284, 1721, 5307, 5307, 5008, 3089, 5578, 252, 252, 3944,
    1465, 6747, 61, 326, 1530, 5895, 8256, 2212, 1392, 1392, 2263, 7955, 1348,
    5212, 5212, 3607, 3607, 6292, 6292, 3614, 1590, 1590, 8245, 4193, 2572, 3651,
    3651, 3651, 3651, 3651, 3958, 7099, 6172, 7507, 7507, 7782, 4699, 7437, 1463,
    1463, 53, 7005, 3970, 8472, 8470, 1134, 9866, 8080, 7246, 7246, 3520, 3520,
    6956, 6956, 3951, 4111, 5522, 5522, 7394, 7394, 5579, 599, 8452, 8452, 123,
    189, 4639, 3250, 3250, 1215, 7757, 6289, 8243, 4462, 4462, 433, 4775, 9758,
    3212, 3184, 5986, 7438, 9245, 401, 5698, 423, 423, 5845, 5098, 7511, 7230,
    255, 255, 9246, 5226, 5226, 8958, 4922, 6699, 6699, 8551, 3211, 3211, 6730,
    5390, 5361, 7206, 6701, 104, 104, 7332, 7332, 305

'''