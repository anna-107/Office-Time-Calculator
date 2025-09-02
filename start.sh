#!/bin/bash

# Exit immediately if a command fails
set -e

# Step 1: Create virtual environment
python3 -m venv venv

# Step 2: Activate the virtual environment
source venv/bin/activate

# Step 3: Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Prompt for timings
read -p "Enter start time (e.g., 09:00): " START
read -p "Enter lunch start time (e.g., 13:00): " LUNCH_START
read -p "Enter lunch end time (e.g., 14:00): " LUNCH_END

# Run the Python script with user-provided timings
python3 timeCalculator.py --start "$START" --lunch_start "$LUNCH_START" --lunch_end "$LUNCH_END"
