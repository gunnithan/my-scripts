#!/bin/bash

# Navigate to the directory where the script is located
cd "$(dirname "$0")"

# Loop through all directories in the current folder
for dir in */; do
    # Remove trailing slash
    dir="${dir%/}"
    
    # Skip if it's the script itself or if the folder doesn't contain a hyphen
    [[ "$dir" == "organise.sh" ]] && continue
    if [[ "$dir" == *'-'* ]]; then
        
        # Extract artist (everything before the first hyphen, trimmed)
        proposed_artist=$(echo "$dir" | cut -d'-' -f1 | sed 's/[[:space:]]*$//')
        
        # Skip if the directory name is already just the artist name
        [ "$dir" == "$proposed_artist" ] && continue
        
        # Clear, structured display BEFORE making a choice
        echo "--------------------------------------------------------"
        echo "Original Folder: $dir"
        echo "Proposed Folder: $proposed_artist/$dir"
        echo "Options:         [ENTER] to accept proposed folder"
        echo "                 [Type a custom name] to override"
        echo "                 [s] to skip this folder"
        echo "--------------------------------------------------------"
        
        # Prompt user for input
        read -p "Your choice: " user_input
        
        # Handle user choice
        if [[ "$user_input" == "s" || "$user_input" == "S" ]]; then
            echo "--> Skipped. Original Folder: '$dir' was not moved."
            echo ""
            continue
        elif [[ -n "$user_input" ]]; then
            # Trim any accidental whitespace from custom input
            final_artist=$(echo "$user_input" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            echo "--> Overriding. Original Folder: '$dir' -> Moving to: '$final_artist/$dir'"
        else
            final_artist="$proposed_artist"
            echo "--> Accepting. Original Folder: '$dir' -> Moving to: '$final_artist/$dir'"
        fi
        
        # Execute the move
        mkdir -p "$final_artist"
        mv "$dir" "$final_artist/"
        echo "Success!"
        echo ""
    fi
done

echo "All done!"
