#!/usr/bin/env python3
import os
import re
import csv
import glob

CHARTS_DIR = "/mnt/wd/charts"
LOCAL_LIBRARY_DIR = "/mnt/wd/music"

def clean_string_for_matching(text):
    if not text: return ""
    return text.lower().strip().replace("*", "")

def debug_check():
    print("--- Diagnostic Path Check ---")
    print(f"Checking library path: {LOCAL_LIBRARY_DIR}")
    if not os.path.exists(LOCAL_LIBRARY_DIR):
        print("ERROR: Library path does not exist!")
        return
        
    folders = [f for f in os.listdir(LOCAL_LIBRARY_DIR) if os.path.isdir(os.path.join(LOCAL_LIBRARY_DIR, f))]
    print(f"Total folders found in directory: {len(folders)}")
    
    print("\n--- Testing Regex on first 10 folders ---")
    for folder in folders[:10]:
        # Loose check to see what's happening
        match = re.match(r'^(.+?)\s+-\s+(.+?)\s*\(\d{4}\)$', folder)
        if match:
            print(f"[MATCHED]  Folder: '{folder}' -> Artist: '{match.group(1)}', Album: '{match.group(2)}'")
        else:
            print(f"[FAILED]   Folder: '{folder}' (Does not match 'Artist - Album (Year)' pattern)")

    print("\n--- Checking CSV Structure ---")
    csv_files = glob.glob(os.path.join(CHARTS_DIR, "*.csv"))
    if not csv_files:
        print("No CSV files found in charts directory.")
        return
        
    test_csv = csv_files[0]
    print(f"Reading first CSV file: {os.path.basename(test_csv)}")
    with open(test_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print("First 5 rows in CSV:")
        for i, row in enumerate(reader):
            if i >= 5: break
            print(f"  Artist: '{row.get('album artist')}' | Album: '{row.get('album name')}'")

if __name__ == "__main__":
    debug_check()