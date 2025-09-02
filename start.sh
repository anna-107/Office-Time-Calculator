#!/bin/bash

# Prompt for timings
read -p "Enter start time (e.g., 09:00): " START
read -p "Enter lunch start time (e.g., 13:00): " LUNCH_START
read -p "Enter lunch end time (e.g., 14:00): " LUNCH_END

# Activate virtual environment
cd T
source venv/bin/activate

# Run the Python script with user-provided timings
python3 timeCalculator.py --start "$START" --lunch_start "$LUNCH_START" --lunch_end "$LUNCH_END"
