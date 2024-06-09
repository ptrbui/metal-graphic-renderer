#!/bin/bash

# Step 0: Check if width and height are specified
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <width> <height>"
    exit 1
fi

width=$1
height=$2

# Step 1: Create a virtual environment
python3 -m venv venv

# Step 2: Activate the virtual environment
source venv/bin/activate

# Step 3: Install requirements
pip install -r requirements.txt

# Step 4: Run the .py file
python main_cli.py "$width" "$height"

# Step 5: Deactivate the virtual environment
deactivate