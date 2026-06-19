#!/usr/bin/env python3
"""
Author: Girish Unnithan
Description: Media Library Gap Checker (CSV Output Edition)
Checks Discogs flat CSV charts against a local library and reports missing entries as CSV.
"""

import os
import re
import csv
import glob

# Paths based on your updated setup
CHARTS_DIR = "/mnt/wd/charts"
LOCAL_LIBRARY_DIR = "/mnt/wd/music"
OUTPUT_GAP_DIR = "/mnt/wd/gaps"

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
    
    for folder_name in os.listdir(library_path):
        folder_full_path = os.path.join(library_path, folder_name)
        
        if not os.path.isdir(folder_full_path):
            continue
            
        # Regex to parse 'Artist - Album (Year)'
        match = re.match(r'^(.+?)\s+-\s+(.+?)\s*\(\d{4}\)$', folder_name)
        
        if match:
            raw_artist = match.group(1)
            raw_album = match.group(2)
            
            clean_artist = clean_string_for_matching(raw_artist)
            clean_album = clean_string_for_matching(raw_album)
            
            local_inventory.add((clean_artist, clean_album))
        else:
            if " - " in folder_name:
                parts = folder_name.split(" - ", 1)
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
            genre = row.get("genre", "")
            style = row.get("style", "")
            
            clean_chart_artist = clean_string_for_matching(album_artist)
            clean_chart_album = clean_string_for_matching(album_name)
            
            match_key = (clean_chart_artist, clean_chart_album)
            
            if match_key not in local_inventory:
                missing_albums.append({
                    "rank": rank,
                    "album artist": album_artist,
                    "album name": album_name,
                    "year": year,
                    "genre": genre,
                    "style": style
                })
                
    return missing_albums, total_chart_items

def main():
    print("--- Discogs Media Library Gap Checker (CSV Output) ---")
    
    local_inventory = scan_local_library(LOCAL_LIBRARY_DIR)
    
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
        
        # Swapped suffix out to .csv instead of .txt
        report_filename = base_filename.replace(".csv", "_missing_report.csv")
        report_path = os.path.join(OUTPUT_GAP_DIR, report_filename)
        
        # Fieldnames layout matching your original preferences
        fieldnames = ["rank", "album name", "album artist", "year", "genre", "style"]
        
        with open(report_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in missing:
                writer.writerow(item)
                    
        print(f" -> Analysis complete. {len(missing)} gaps found. Saved directly to {report_path}\n")

if __name__ == "__main__":
    main()