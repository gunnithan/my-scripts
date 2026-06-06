


# Discogs Library Reference Exporter

## What This Tool Does
This script is an automation tool designed to generate a clean, ranked CSV list of the absolute **Most Wanted** (highest demand) albums directly from the Discogs database. By targeting specific musical fields, it scours thousands of pressings and exports a structured dataset containing essential metadata like album names, artists, release years, and primary genres.

---

## Example Use Case: Auditing Your Personal Media Collection
If you run a self-hosted media platform (such as Plex) or maintain a large digital music archive, it can be incredibly difficult to track what iconic albums are missing from your storage drives. 

This exporter serves as the vital first step in your automation chain. For example, you can generate a reference list of the "Top 100 Hard Rock Albums" or "Top 200 Blues Records". Once you have this clean CSV checklist, you can easily use separate comparison scripts or automation tools to scan your local media folders, cross-reference the paths, and instantly highlight the structural gaps in your collection. 

To ensure your charts are highly accurate, the script utilizes strict primary tag filters and robust text-normalization to strip out duplicate pressings, keeping your data clean and completely free of cross-genre clutter.

---

## Features
* **Strict Primary Tag Validation:** Enforces that your target Genre or Style is the absolute first metadata element (index 0) assigned by Discogs. This prevents massive mainstream crossover hits from muddying specialized genre charts.
* **Flexible Filtering:** Allows you to search exclusively by a broad top-level Genre, exclusively by a specific micro-Style, or use both simultaneously.
* **Smart Asset Deduplication:** Leaves structural articles like "The" fully intact but automatically strips trailing database wildcards (`*`) and unique pressing index numbers like `(2)` or `[3]`.
* **Dynamic File Versioning:** Automatically checks your destination directory and increments a version suffix (`_v_1`, `_v_2`, etc.) to protect you from accidentally overwriting past collections.
* **Fully Configurable Paths:** Keeps your code completely separate from your storage deployment layout. Directories and file settings are read directly out of a secure environment configuration.

---

## Directory Structure & Installation

### 1. Clone or Create the Project Files
Create a workspace folder on your host and setup your script ecosystem:
```bash
mkdir -p /opt/discogs-exporter/
cd /opt/discogs-exporter/

```

### 2. Install System Dependencies

Install the required system tools and official Python package modules using your terminal shell manager:

```bash
# Update local packages and install prerequisites
sudo apt update && sudo apt install -y python3-pip

# Install required external Python automation modules
pip3 install python-dotenv requests
```

## Configuration (`.env`)

To prevent sensitive developer credentials from leaking onto public GitHub repositories, all local path mappings and personal secret keys are abstracted out into a localized `.env` configuration file.

### 1. Configure the Exporter Variables

Create a hidden file named `.env` in the exact same directory as your execution script:

```bash
nano .env

```

Paste the following blocks inside it, adjusting the directory mount points and secret keys to match your system environment layout:

```env
# Your private Discogs Personal Access Token
DISCOGS_TOKEN=your_secret_discogs_developer_token_here

# Absolute path to the folder where you want your chart outputs saved
OUTPUT_CHARTS_DIR=/mnt/wd/charts/

```

### 2. Protect Your Secret Tokens On GitHub

Ensure your version control configuration explicitly ignores active system settings before staging commits. Create a `.gitignore` file in your project path:

```text
# .gitignore
.env
__pycache__/
*.pyc
*.csv

```

---

## How To Run

Execute the program directly from your workspace directory:

```bash
python3 discogs_flat_exporter.py

```

### Interactive Console Parameters

When prompted, pass your exact target musical attributes directly through your keyboard interface:

1. **Genre Input:** Enter high-level classification categories (e.g., `Rock`, `Pop`, `Jazz`, `Blues`, `Hip-Hop`, `Classical`). *Leave blank if you want to filter strictly by a sub-style.*
2. **Style Input:** Enter detailed stylistic variations (e.g., `Hard Rock`, `Country`, `R&B`, `Carnatic`, `Hindustani`, `Rap`). *Leave blank if you want to look up a broader genre family.*
3. **Language Input:** Input shorthand language query boundaries (`Eng`, `Hin`, or leave completely blank to scrape records in any language).
4. **Volume Target:** Specify the exact limit of unique primary references you wish to extract (e.g., `100`, `200`).

---

## Author & Project Info

* **Author:** Girish Unnithan
* **Date:** 06 June 2026
* **Deployment System:**  Ubuntu 26.04 LTS 

```

```