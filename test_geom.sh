#!/bin/bash

# Step 1: Create a virtual environment
python3 -m venv venv

# Step 2: Activate the virtual environment
source venv/bin/activate

# Step 3: Install requirements
pip install -r requirements.txt

# Step 4: Run the .py file
python main_test_geom.py

# Step 5: Deactivate the virtual environment
deactivate