"""
================================================================================
Author: Girish Unnithan
Date: 06 June 2026
Description: Discogs Library Reference Exporter

GitHub Repository Setup Instructions:
  1. Ensure '.env' is added to your '.gitignore' file to prevent token leaks.
  2. Create a '.env' file in the root directory of this project.
  3. Populate the file with: 
     DISCOGS_TOKEN=your_actual_token_here
     OUTPUT_CHARTS_DIR=/mnt/wd/charts/
  4. Run 'pip3 install python-dotenv requests' before executing.

Logic Overview:
  1. Initialization: Automatically reads your secure developer API token and
     custom storage destination directory out of the local hidden '.env' file.
  2. Input Processing: Captures Genre, Style, and Language inputs via keyboard.
     Accepts optional parameters so you can search exclusively by Style (e.g. 
     Hard Rock) or exclusively by Genre (e.g. Rock). Shorthand entries like 
     'Eng' or 'Hin' map automatically to Discogs text query filters.
  3. API Pagination Loop: Sends structured requests to Discogs sorted by 
     'Most Wanted' (highest demand) in descending order. Iterates page-by-page
     handling rate limits politely with dynamic back-off delays.
  4. Strict Primary Tag Validation: Inspects the raw metadata arrays returned by
     Discogs. The album is ONLY accepted if your requested filter matches the 
     absolute first element (index 0) of the 'genre' or 'style' list. This prevents 
     massive crossover albums from bleeding into secondary collections.
  5. Smart Deduplication: Normalizes artist and album titles to block duplicate
     rows caused by master pressings. It leaves 'The' intact but strips away 
     trailing asterisks (*) and bracketed database numbers like (2) or [3].
  6. Flat File Export: Dynamically checks your system folder structure, auto-builds
     missing directories, and logs your reference lists straight to your specified
     OUTPUT_CHARTS_DIR folder with neat file versioning.
================================================================================
"""

import csv
import os
import re
import time
import requests
from dotenv import load_dotenv

# Automatically load environment variables from the local .env file
load_dotenv()

LANGUAGE_MAP = {
    "eng": "english",
    "hin": "hindi"
}

def clean_string_for_matching(text):
    """
    Cleans up artist and album strings to ensure smart duplicate matching.
    Leaves 'The' intact, but strips trailing asterisks and bracketed database numbers.
    """
    if not text:
        return ""
    
    # Convert to lowercase to ignore case differences (e.g. 'Rock' vs 'rock')
    text = text.lower().strip()
    
    # Remove trailing asterisks (e.g. 'rolling stones*' -> 'rolling stones')
    text = text.replace("*", "")
    
    # Remove bracketed numbers like (2) or [3] used by Discogs for unique IDs
    text = re.sub(r'[\(\[][0-9]+[\)\]]', '', text)
    
    # Strip any extra spaces left over after cleaning
    return text.strip()

def generate_flat_filename(base_dir, genre, style, language_code, target_count):
    """Saves directly to the configured folder directory with correct naming layout."""
    # Safety fallback if the environment path happens to be empty or unreadable
    if not base_dir:
        base_dir = "/mnt/wd/charts/"
        
    # Enforce standard directory trees on your storage array
    os.makedirs(base_dir, exist_ok=True)
    
    # Use style name if present; otherwise fall back to genre
    name_base = style if style else genre
    clean_base = name_base.lower().replace(" ", "_").replace("-", "_")
    
    if language_code:
        file_prefix = f"{clean_base}_{language_code.lower()}"
    else:
        file_prefix = clean_base
        
    counter = 1
    while True:
        filename = f"{file_prefix}_top{target_count}_v_{counter}.csv"
        full_path = os.path.join(base_dir, filename)
        
        if not os.path.exists(full_path):
            return full_path
        counter += 1

def fetch_discogs_top_albums(token, genre, style, language_query, target_count=100):
    """Queries the Discogs API ensuring the target is the absolute primary (first) metadata attribute."""
    url = "https://api.discogs.com/database/search"
    headers = {
        "User-Agent": "MediaLibraryGapChecker/1.0",
        "Authorization": f"Discogs token={token}"
    }
    
    collected_releases = []
    seen_keys = set() 
    page = 1
    per_page = 50
    
    search_terms = []
    if genre: search_terms.append(f"Genre: {genre}")
    if style: search_terms.append(f"Style: {style}")
    search_desc = " + ".join(search_terms) if search_terms else "All Music"
    
    print(f"\nConnecting to Discogs database for {search_desc} [Lang: {language_query or 'Any'}]...")
    print("Sorting results by: Most Wanted (Highest Demand with Strict Primary Validation)")
    
    while len(collected_releases) < target_count:
        params = {
            "type": "release",
            "format": "album",
            "per_page": per_page,
            "page": page,
            "sort": "want",        
            "sort_order": "desc"   
        }
        
        if genre:
            params["genre"] = genre
        if style:
            params["style"] = style
        if language_query:
            params["q"] = language_query
            
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 429:
                print("Rate limit hit. Waiting 5 seconds...")
                time.sleep(5)
                continue
                
            if response.status_code != 200:
                print(f"Error connecting to API: {response.status_code}")
                break
                
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                print("No more entries matching your filters found in the Discogs database.")
                break
                
            for item in results:
                item_genres = item.get("genre", [])
                item_styles = item.get("style", [])
                
                # If searching by genre, enforce that our input is the FIRST element
                if genre and item_genres:
                    if item_genres[0].lower() != genre.lower():
                        continue  
                        
                # If searching by style, enforce that our input is the FIRST element
                if style and item_styles:
                    if item_styles[0].lower() != style.lower():
                        continue  
                
                raw_title = item.get("title", "")
                if " - " in raw_title:
                    artist, album = raw_title.split(" - ", 1)
                else:
                    artist = "Unknown Artist"
                    album = raw_title
                
                match_artist = clean_string_for_matching(artist)
                match_album = clean_string_for_matching(album)
                match_key = (match_artist, match_album)
                
                if match_key not in seen_keys:
                    seen_keys.add(match_key)
                    
                    primary_genre = item_genres[0] if item_genres else (genre if genre else "Various")
                    primary_style = item_styles[0] if item_styles else (style if style else "")
                    
                    collected_releases.append({
                        "album": album.strip(),
                        "artist": artist.strip(),
                        "year": item.get("year", "Unknown"),
                        "genre": primary_genre,
                        "style": primary_style
                    })
                    
                    if len(collected_releases) >= target_count:
                        break
            
            print(f"Progress: {len(collected_releases)} / {target_count} items tracked...")
            page += 1
            time.sleep(1.0)
            
        except Exception as e:
            print(f"Network processing error: {e}")
            break
            
    return collected_releases

def main():
    print("--- Discogs Library Reference Exporter ---")
    
    api_token = os.getenv("DISCOGS_TOKEN")
    output_directory = os.getenv("OUTPUT_CHARTS_DIR")
    
    if not api_token:
        print("Note: DISCOGS_TOKEN not detected in .env file.")
        api_token = input("Please enter your Discogs Personal Access Token: ").strip()
        
    if not api_token:
        print("Error: A valid Discogs token is required to execute searches.")
        return
        
    if not output_directory:
        print("Note: OUTPUT_CHARTS_DIR variable missing in env configuration.")
        output_directory = input("Enter destination directory path (e.g. /mnt/wd/charts/): ").strip()

    print("\n[Discogs Genre Examples]: Rock, Pop, Jazz, Blues, Hip-Hop, Classical, Funk / Soul")
    genre = input("Enter exact genre name (Or leave blank to search by style only): ").strip()
    
    print("\n[Discogs Style Examples]: Hard Rock, Country, R&B, Carnatic, Hindustani, Rap, Pop Rap")
    style = input("Enter exact style name (Or leave blank if genre was specified): ").strip()
    
    if not genre and not style:
        print("Error: You must provide at least a genre or a style to run a lookup.")
        return
    
    lang_input = input("\nEnter language filter (Eng/Hin or leave blank for any): ").strip().lower()
    language_query = LANGUAGE_MAP.get(lang_input, lang_input if lang_input else "")
    
    try:
        total_items = int(input("\nHow many items do you want in your reference check list? (e.g. 100): "))
    except ValueError:
        total_items = 100

    albums = fetch_discogs_top_albums(api_token, genre, style, language_query, total_items)
    
    if not albums:
        print("Export aborted: No data retrieved from Discogs.")
        return
        
    output_filepath = generate_flat_filename(output_directory, genre, style, lang_input, total_items)
    
    print(f"\nWriting dataset out directly to: {output_filepath}")
    
    with open(output_filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["rank", "album name", "album artist", "year", "genre", "style"])
        writer.writeheader()
        
        for idx, album in enumerate(albums, start=1):
            writer.writerow({
                "rank": idx,
                "album name": album["album"],
                "album artist": album["artist"],
                "year": album["year"],
                "genre": album["genre"],
                "style": album["style"]
            })
            
    print(f"Success! Reference file compiled with {len(albums)} entries.")

if __name__ == "__main__":
    main()