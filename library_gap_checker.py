#!/usr/bin/env python3
"""
Author: Girish Unnithan
Description: Media Library Gap Checker (Multilingual & Special Edition Fix)
Checks Discogs flat CSV charts against a local library and reports missing entries as CSV.
"""

import os
import re
import csv
import glob

CHARTS_DIR = "/mnt/wd/charts"
LOCAL_LIBRARY_DIR = "/mnt/wd/music/albums"
OUTPUT_GAP_DIR = "/mnt/wd/gaps"

def clean_string_for_matching(text):
    """
    Advanced normalization to handle multilingual entries, 
    special edition brackets, punctuation, and artist variations.
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower().strip()
    
    # 1. Split on '=' to discard translated non-English metadata (e.g. "Kanye West = カニエ・ウェスト")
    if "=" in text:
        text = text.split("=", 1)[0].strip()
        
    # 2. Standardise Compilation Artists to match your "Various Artists" scheme
    if text in ["various", "various artists", "various - ost", "ost"] or "/ ost" in text:
        return "various artists"
        
    # 3. Strip out common edition tags that mess up the album folder matches
    # This handles variants like [Expanded Edition], (50th Anniversary), [2023 Remaster]
    text = re.sub(r'\[.*?remaster.*?\]|\(.*?remaster.*?\)', '', text)
    text = re.sub(r'\[.*?edition.*?\]|\(.*?edition.*?\)', '', text)
    text = re.sub(r'\[.*?anniversary.*?\]|\(.*?anniversary.*?\)', '', text)
    text = re.sub(r'\[.*?soundtrack.*?\]|\(.*?soundtrack.*?\)', '', text)
    
    # 4. Remove trailing asterisks and discogs database numbers like (2) or [3]
    text = text.replace("*", "")
    text = re.sub(r'[\(\[][0-9]+[\)\]]', '', text)
    
    # 5. Standardise symbols and clear out lingering non-alphanumeric punctuation
    text = text.replace("&", "and")
    text = re.sub(r"[^\w\s]", "", text)
    
    # Collapse multiple spaces down to a single space
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()

def scan_local_library(library_path):
    """Scans the local library and robustly caches the normalized (artist, album) pairs."""
    local_inventory = set()
    
    if not os.path.exists(library_path):
        print(f"Warning: Local library directory not found at {library_path}")
        return local_inventory

    print(f"Scanning local library at: {library_path}...")
    
    for folder_name in os.listdir(library_path):
        folder_full_path = os.path.join(library_path, folder_name)
        
        if not os.path.isdir(folder_full_path):
            continue
            
        if " - " in folder_name:
            parts = folder_name.split(" - ", 1)
            raw_artist = parts[0]
            
            # Remove the year designation at the end, e.g. (1993) or (2023]
            raw_album = re.sub(r'\s*[\(\[]\d{4}[\)\]]$', '', parts[1])
            
            clean_artist = clean_string_for_matching(raw_artist)
            clean_album = clean_string_for_matching(raw_album)
            
            if clean_artist and clean_album:
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
    print("--- Discogs Media Library Gap Checker (Multilingual Fix) ---")
    
    local_inventory = scan_local_library(LOCAL_LIBRARY_DIR)
    
    csv_pattern = os.path.join(CHARTS_DIR, "*.csv")
    chart_files = glob.glob(csv_pattern)
    
    if not chart_files:
        print(f"No Discogs reference CSV files found in {CHARTS_DIR}.")
        return
        
    os.makedirs(OUTPUT_GAP_DIR, exist_ok=True)
    
    for csv_file in chart_files:
        base_filename = os.path.basename(csv_file)
        
        if "local_library_inventory" in base_filename:
            continue
            
        print(f"Processing: {base_filename}...")
        
        missing, total_count = check_gaps_in_csv(csv_file, local_inventory)
        
        report_filename = base_filename.replace(".csv", "_missing_report.csv")
        report_path = os.path.join(OUTPUT_GAP_DIR, report_filename)
        
        fieldnames = ["rank", "album name", "album artist", "year", "genre", "style"]
        
        with open(report_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in missing:
                writer.writerow(item)
                    
        print(f" -> Complete. Found {len(missing)} missing items out of {total_count} records.\n")

if __name__ == "__main__":
    main()