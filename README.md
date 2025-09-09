# Office Hours Calculator

A terminal-based Python tool to track your work hours, lunch breaks, and progress throughout the day.  
It displays your current status, time worked, time remaining, and lunch break details in a visually appealing table using [rich](https://github.com/Textualize/rich).

---

## Features

- **Customizable work and lunch times**
- **Progress bar and status table**
- **Input validation and helpful error messages**
- **Notifications for lunch and end of work day**
- **Cross-day support (handles overnight shifts)**
- **Configurable refresh interval**

---


## Usage

Run the automated script from your terminal (initially: as it takes care of all dependencies):

```
cd Office-Time-Calculator
chmod +x start.sh
./start.sh
```
 If not using automated script, you need to manually create Virtual Environment, then pip install dependencies, then run the script inside virtual environment.

- All times should be in **24-hour format** (e.g., `09:00`, `13:00`, `14:00`).
- Example:

  ```
  python timeCalculator.py --start 09:00 --lunch_start 13:00 --lunch_end 14:00
  ```

- To change the refresh interval (in seconds):

  ```
  python timeCalculator.py --start 09:00 --lunch_start 13:00 --lunch_end 14:00 --refresh 30
  ```

- To see help:

  ```
  python timeCalculator.py --help
  ```

---

## Example Output

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    Office Hours Calculator                            ┃
┡━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Description  │ Time         │ Details                                 │
│ Start Time   │ 09:00        │ Work day begins                         │
│ Lunch Start  │ 13:00        │ Break time                              │
│ Lunch End    │ 14:00        │ Back to work                            │
│ End Time     │ 18:00        │ Work day ends                           │
│ Current Sta… │ Working (Pr… │ As of 10:15:23                          │
│ Worked Time  │ 01:15:23     │ 15.6% complete                          │
│ Remaining T… │ 06:44:37     │ Until work ends                         │
└──────────────┴──────────────┴─────────────────────────────────────────┘
```

---

## Logging

Session logs are saved to `time_calculator.log` in the script directory.

---

## Notes

- If your lunch or work period crosses midnight, the script will handle it automatically.
- If input times are illogical (e.g., lunch before start), you’ll be prompted to confirm.
- Must have python3 and pip3 installed.

---


## Author
[Sushant Pandey](https://github.com/anna-107)
