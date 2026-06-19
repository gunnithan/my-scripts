#!/usr/bin/env python3
"""
Author: Girish Unnithan
Description: Local Library Inventory Exporter
Dumps the exact parsed structure of the local library into a CSV for troubleshooting.
"""

import os
import re
import csv

LOCAL_LIBRARY_DIR = "/mnt/wd/music/albums"
OUTPUT_CSV_PATH = "/mnt/wd/gaps/local_library_inventory.csv"

def clean_string_for_matching(text):
    """The current normalization logic we are testing."""
    if not text:
        return ""
    text = text.lower().strip()
    text = text.replace("*", "")
    text = re.sub(r'[\(\[][0-9]+[\)\]]', '', text)
    return text.strip()

def main():
    print(f"Scanning library to build diagnostic inventory...")
    
    if not os.path.exists(LOCAL_LIBRARY_DIR):
        print(f"Error: Directory does not exist at {LOCAL_LIBRARY_DIR}")
        return

    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    
    folders = os.listdir(LOCAL_LIBRARY_DIR)
    total_folders = len(folders)
    parsed_count = 0
    
    with open(OUTPUT_CSV_PATH, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Writing headers showing both raw and normalized values
        writer.writerow([
            "Raw Folder Name", 
            "Parsed Artist", 
            "Parsed Album", 
            "Normalized Artist", 
            "Normalized Album"
        ])
        
        for folder_name in folders:
            folder_full_path = os.path.join(LOCAL_LIBRARY_DIR, folder_name)
            
            if not os.path.isdir(folder_full_path):
                continue
                
            parsed_count += 1
            raw_artist, raw_album = "Unknown", "Unknown"
            
            # Match current production regex
            match = re.match(r'^(.+?)\s+-\s+(.+?)\s*\(\d{4}\)$', folder_name)
            
            if match:
                raw_artist = match.group(1)
                raw_album = match.group(2)
            elif " - " in folder_name:
                parts = folder_name.split(" - ", 1)
                raw_artist = parts[0]
                raw_album = re.sub(r'\s*\(\d{4}\)$', '', parts[1])
                
            clean_artist = clean_string_for_matching(raw_artist)
            clean_album = clean_string_for_matching(raw_album)
            
            writer.writerow([
                folder_name, 
                raw_artist.strip(), 
                raw_album.strip(), 
                clean_artist, 
                clean_album
            ])
            
    print(f"Done! Evaluated {parsed_count} folders out of {total_folders} entries.")
    print(f"Inventory csv saved to: {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    main()