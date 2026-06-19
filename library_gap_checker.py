#!/usr/bin/env python3
"""
Author: Girish Unnithan
Description: Media Library Gap Checker
Checks Discogs flat CSV charts against a local library and reports missing entries.
"""

import os
import re
import csv
import glob

# Paths based on your server setup
CHARTS_DIR = "/mnt/wd/charts"
LOCAL_LIBRARY_DIR = "/mnt/wd/Music/Albums"
OUTPUT_GAP_DIR = "/mnt/wd/charts/gaps"

def clean_string_for_matching(text):
    """
    Mirroring the exact cleanup logic from discogs_flat_exporter.py.
    Leaves 'The' intact, strips trailing asterisks and bracketed database numbers.
    """
    if not text:
        return ""
    text = text.lower().strip()
    text = text.replace("*", "")
    text = re.sub(r'[\(\[][0-9]+[\)\]]', '', text)
    return text.strip()

def scan_local_library(library_path):
    """
    Scans the local library for directories matching 'Artist - Album (Year)'.
    Returns a set of unique (cleaned_artist, cleaned_album) tuples.
    """
    local_inventory = set()
    
    if not os.path.exists(library_path):
        print(f"Warning: Local library directory not found at {library_path}")
        return local_inventory

    print(f"Scanning local library at: {library_path}...")
    
    # Iterate through all entries in the directory
    for folder_name in os.listdir(library_path):
        folder_full_path = os.path.join(library_path, folder_name)
        
        # Only process directories
        if not os.path.isdir(folder_full_path):
            continue
            
        # Regex to parse 'Artist - Album (Year)' 
        # Accounts for spaces and matches standard year formats at the end
        match = re.match(r'^(.+?)\s+-\s+(.+?)\s*\(\d{4}\)$', folder_name)
        
        if match:
            raw_artist = match.group(1)
            raw_album = match.group(2)
            
            clean_artist = clean_string_for_matching(raw_artist)
            clean_album = clean_string_for_matching(raw_album)
            
            local_inventory.add((clean_artist, clean_album))
        else:
            # Fallback if folder formatting slightly misses the year tag
            if " - " in folder_name:
                parts = folder_name.split(" - ", 1)
                # Strip out trailing year if it's there but didn't match the main regex
                album_part = re.sub(r'\s*\(\d{4}\)$', '', parts[1])
                
                clean_artist = clean_string_for_matching(parts[0])
                clean_album = clean_string_for_matching(album_part)
                local_inventory.add((clean_artist, clean_album))

    print(f"Found {len(local_inventory)} valid local albums cached for matching.\n")
    return local_inventory

def check_gaps_in_csv(csv_path, local_inventory):
    """Compares a single Discogs reference chart against the local inventory."""
    missing_albums = []
    total_chart_items = 0
    
    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_chart_items += 1
            album_name = row.get("album name", "").strip()
            album_artist = row.get("album artist", "").strip()
            rank = row.get("rank", "0")
            year = row.get("year", "Unknown")
            
            clean_chart_artist = clean_string_for_matching(album_artist)
            clean_chart_album = clean_string_for_matching(album_name)
            
            match_key = (clean_chart_artist, clean_chart_album)
            
            if match_key not in local_inventory:
                missing_albums.append({
                    "rank": rank,
                    "artist": album_artist,
                    "album": album_name,
                    "year": year
                })
                
    return missing_albums, total_chart_items

def main():
    print("--- Discogs Media Library Gap Checker ---")
    
    # Cache local inventory first to keep lookup speeds at O(1)
    local_inventory = scan_local_library(LOCAL_LIBRARY_DIR)
    
    if not local_inventory:
        print("No local files matched the 'Artist - Album (Year)' naming scheme. Please check your folder layouts.")
        # We can still proceed but it will just flag everything as missing
    
    # Locate all compiled reference charts
    csv_pattern = os.path.join(CHARTS_DIR, "*.csv")
    chart_files = glob.glob(csv_pattern)
    
    if not chart_files:
        print(f"No Discogs reference CSV files found in {CHARTS_DIR}.")
        print("Please run your discogs_flat_exporter.py script first.")
        return
        
    os.makedirs(OUTPUT_GAP_DIR, exist_ok=True)
    
    print(f"Discovered {len(chart_files)} chart reference files to cross examine.")
    
    for csv_file in chart_files:
        base_filename = os.path.basename(csv_file)
        print(f"Processing: {base_filename}...")
        
        missing, total_count = check_gaps_in_csv(csv_file, local_inventory)
        
        # Generate the name for the output gap report text file
        report_filename = base_filename.replace(".csv", "_missing_report.txt")
        report_path = os.path.join(OUTPUT_GAP_DIR, report_filename)
        
        with open(report_path, mode="w", encoding="utf-8") as report:
            report.write(f"=================================================================\n")
            report.write(f"Missing Album Report for: {base_filename}\n")
            report.write(f"Source Chart Size: {total_count} records\n")
            report.write(f"Total Items Missing from Local Storage: {len(missing)}\n")
            report.write(f"=================================================================\n\n")
            
            if not missing:
                report.write("Perfect match! You have every single album from this list.\n")
            else:
                report.write(f"{'Rank':<6} | {'Artist':<30} | {'Album Name':<40} | {'Year':<6}\n")
                report.write(f"{'-'*6}-+-{'-'*30}-+-{'-'*40}-+-{'-'*6}\n")
                
                for item in missing:
                    # Truncate strings slightly if they are massive to keep the report neat
                    artist_disp = item['artist'][:28] + ".." if len(item['artist']) > 30 else item['artist']
                    album_disp = item['album'][:38] + ".." if len(item['album']) > 40 else item['album']
                    
                    report.write(f"{item['rank']:<6} | {artist_disp:<30} | {album_disp:<40} | {item['year']:<6}\n")
                    
        print(f" -> Analysis complete. {len(missing)} gaps found. Report logged to {report_path}\n")

if __name__ == "__main__":
    main()