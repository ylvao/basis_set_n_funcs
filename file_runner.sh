#!/bin/bash

# 1. Define files to explicitly exclude (space-separated)
EXCLUDE_LIST="file_runner.sh mrchem_runner.sh orca_runner.sh mw_settings.py get_xyz.py parameters.py"
PATTERN=$(echo $EXCLUDE_LIST | sed 's/ /|/g')

# 2. Files to include from the current folder (filtered)
LOCAL_FILES=$(ls *.py *.sh 2>/dev/null | grep -Ev "$PATTERN")

# 3. Explicitly add a file from another folder
# Replace '../other_folder/target_script.py' with your actual path
EXTRA_FILES="results/plotting.py results/extract_error_data.py"

# Combine them into one list
FILES="$LOCAL_FILES $EXTRA_FILES"

# 2. Check if any files exist
if [ -z "$FILES" ]; then
    echo "No .py or .sh files found in the current directory."
    exit 1
fi

echo "------------------------------------------"
echo " Select a file to run:"
echo "------------------------------------------"

# 3. Create the interactive menu
PS3="Enter the number of the file (or 'q' to quit):"

select FILENAME in $FILES; do
    if [ -n "$FILENAME" ]; then
        echo "Running $FILENAME..."
        echo "------------------------------------------"
        
        # 4. Determine how to run the file based on extension
        case $FILENAME in
            *.py)
                python3 "$FILENAME"
                ;;
            *.sh)
                bash "$FILENAME"
                ;;
        esac
        
        echo "------------------------------------------"
        echo "Execution finished."
        break
    elif [ "$REPLY" == "q" ]; then
        echo "Exiting."
        break
    else
        echo "Invalid selection. Please try again."
    fi
done