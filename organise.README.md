# Interactive Music Library Organiser

A lightweight, interactive Bash script designed to clean up flat music libraries on Linux/Ubuntu servers. It scans folders named in an `Artist - Album (Year)` format and automatically sorts them into nested `Artist/Album` structures, offering a full preview and manual overrides before making any changes on disk.

## Features

*   **Flat-to-Nested Migration:** Automatically converts `Artist - Album` flat directories into structured `Artist/Artist - Album` layouts.
*   **100% Interactive & Safe:** Shows the exact source and target paths before every single move, preventing runaway script errors.
*   **Manual Overrides:** Allows you to fix typos, rename artists on the fly (e.g., handling edge cases like *AC/DC* or *Jay-Z*), or skip specific folders entirely.
*   **Idempotent Design:** Automatically skips folders that do not match the expected naming pattern or have already been processed.

---

## How It Works

When run, the script loops through the directories in its current folder. For each matching directory, it displays a structured interface in the terminal:

```text
--------------------------------------------------------
Original Folder: Public Enemy - It Takes a Nation of Millions to Hold Us Back (1988)
Proposed Folder: Public Enemy/Public Enemy - It Takes a Nation of Millions to Hold Us Back (1988)
Options:         [ENTER] to accept proposed folder
                 [Type a custom name] to override
                 [s] to skip this folder
--------------------------------------------------------
Your choice:

```

Response Options:
Press [ENTER]: Accepts the proposal. Creates the Public Enemy/ directory (if it doesn't exist) and moves the album inside.

Type a custom name (e.g., Guns N' Roses): Overrides the artist folder name. Useful if the original folder name lacks punctuation or uses an alias.

Type s or S: Skips the directory entirely, leaving the original folder completely untouched.

# Technical Details & Edge Cases
Hyphen Splitting: The script determines the artist name by splitting the folder string at the first hyphen (-).

Whitespace Trimming: Any trailing whitespace from the auto-split or leading/trailing whitespace from your custom manual input is automatically stripped to keep directory names clean.

Safety Lock: The script explicitly ignores itself (organise.sh) and skips folders that do not contain a hyphen separator.

# License
This project is open-source and free to use.

