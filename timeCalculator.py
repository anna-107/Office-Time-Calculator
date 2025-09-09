from datetime import datetime, timedelta
import time
import os
import platform
import threading
import sys
import signal
import argparse
import logging
from colorama import Fore, Style, init
from plyer import notification
from tabulate import tabulate
from tqdm import tqdm
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.layout import Layout
from rich import box
from rich.theme import Theme
from rich.traceback import install
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.tree import Tree

# Initialize colorama
init(autoreset=True)
# Initialize rich traceback
install()
# Custom theme for rich
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "highlight": "bold yellow"
})
console = Console(theme=custom_theme)

# Configure logging
logging.basicConfig(filename='time_calculator.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Global variables
WORK_HOURS = 8
LUNCH_HOURS = 1
TOTAL_HOURS = WORK_HOURS + LUNCH_HOURS
REFRESH_INTERVAL = 60  # seconds

# Signal handler for graceful exit
def signal_handler(sig, frame):
    console.print("\n[info]Exiting gracefully...[/info]")
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Function to clear console
def clear_console():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Function to parse time input and convert to today's datetime
def parse_time_input(time_str):
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        today = datetime.now().date()
        return datetime.combine(today, time_obj)
    except ValueError:
        console.print("[danger]Invalid time format. Please use HH:MM format.[/danger]")
        sys.exit(1)

# Function to handle cross-day scenarios
def handle_cross_day(start_time, lunch_start, lunch_end):
    """Handle cases where lunch or work extends to the next day"""
    # If lunch start is before start time, assume it's the next day
    if lunch_start.time() < start_time.time():
        lunch_start += timedelta(days=1)
    
    # If lunch end is before lunch start, assume it's the next day
    if lunch_end.time() < lunch_start.time():
        lunch_end += timedelta(days=1)
    
    return start_time, lunch_start, lunch_end

# Function to calculate end time
def calculate_end_time(start_time, lunch_start, lunch_end):
    """Calculate when the work day will end"""
    work_duration = timedelta(hours=TOTAL_HOURS)
    lunch_duration = lunch_end - lunch_start
    
    # If lunch is longer than scheduled, only count the excess as work time
    scheduled_lunch = timedelta(hours=LUNCH_HOURS)
    if lunch_duration < scheduled_lunch:
        # Lunch finished early, remaining lunch time counts as work
        effective_lunch_duration = timedelta(0)
        bonus_work_time = scheduled_lunch - lunch_duration
    else:
        # Lunch took longer than scheduled
        effective_lunch_duration = lunch_duration - scheduled_lunch
        bonus_work_time = timedelta(0)
    
    # Calculate end time: start + work hours + effective lunch duration
    end_time = start_time + work_duration - bonus_work_time
    
    return end_time

# Function to get current time
def get_current_time():
    return datetime.now()

# Function to calculate worked time
def calculate_worked_time(start_time, lunch_start, lunch_end):
    """Calculate how much time has been worked so far"""
    current_time = get_current_time()
    
    # If current time is before start time, no work done yet
    if current_time < start_time:
        return timedelta(0)
    
    # If current time is before lunch start
    if current_time <= lunch_start:
        worked_time = current_time - start_time
    
    # If current time is during lunch break
    elif lunch_start < current_time <= lunch_end:
        worked_time = lunch_start - start_time
    
    # If current time is after lunch break
    else:
        pre_lunch_work = lunch_start - start_time
        post_lunch_work = current_time - lunch_end
        worked_time = pre_lunch_work + post_lunch_work
    
    # Ensure worked time is not negative
    return max(worked_time, timedelta(0))

# Function to calculate remaining time
def calculate_remaining_time(end_time):
    """Calculate how much time is left in the work day"""
    current_time = get_current_time()
    remaining_time = end_time - current_time
    return remaining_time

# Function to format timedelta for display
def format_timedelta(td):
    """Format timedelta to HH:MM:SS format"""
    if td.days < 0:
        return f"-{format_timedelta(-td)}"
    
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Function to get work status
def get_work_status(start_time, lunch_start, lunch_end, end_time):
    """Determine current work status"""
    current_time = get_current_time()
    
    if current_time < start_time:
        return "Not started", "info"
    elif current_time <= lunch_start:
        return "Working (Pre-lunch)", "success"
    elif lunch_start < current_time <= lunch_end:
        return "On lunch break", "warning"
    elif current_time <= end_time:
        return "Working (Post-lunch)", "success"
    else:
        return "Work day completed", "highlight"

# Function to calculate lunch duration and remaining lunch time
def calculate_lunch_info(lunch_start, lunch_end):
    """Calculate lunch duration and any time savings"""
    current_time = get_current_time()
    actual_lunch_duration = lunch_end - lunch_start
    scheduled_lunch = timedelta(hours=LUNCH_HOURS)
    
    if actual_lunch_duration < scheduled_lunch:
        time_saved = scheduled_lunch - actual_lunch_duration
        return actual_lunch_duration, time_saved
    else:
        overtime_lunch = actual_lunch_duration - scheduled_lunch
        return actual_lunch_duration, -overtime_lunch

# Function to display status
def display_status(start_time, lunch_start, lunch_end):
    """Display the current status in a formatted table"""
    end_time = calculate_end_time(start_time, lunch_start, lunch_end)
    worked_time = calculate_worked_time(start_time, lunch_start, lunch_end)
    remaining_time = calculate_remaining_time(end_time)
    status, _ = get_work_status(start_time, lunch_start, lunch_end, end_time)
    _, lunch_savings = calculate_lunch_info(lunch_start, lunch_end)
    
    # Calculate progress percentage
    total_work_seconds = WORK_HOURS * 3600
    worked_seconds = worked_time.total_seconds()
    progress_percentage = min((worked_seconds / total_work_seconds) * 100, 100)
    
    # Create main table
    table = Table(title=" Office Hours Calculator", box=box.ROUNDED, style="cyan")
    table.add_column("Description", style="bold", width=20)
    table.add_column("Time", style="bold green", width=15)
    table.add_column("Details", style="dim", width=25)
    
    # Add rows
    table.add_row("Start Time", start_time.strftime("%H:%M"), "Work day begins")
    table.add_row("Lunch Start", lunch_start.strftime("%H:%M"), "Break time")
    table.add_row("Lunch End", lunch_end.strftime("%H:%M"), "Back to work")
    table.add_row("End Time", end_time.strftime("%H:%M"), "Work day ends")
    table.add_row("Current Status", status, f"As of {datetime.now().strftime('%H:%M:%S')}")
    table.add_row("Worked Time", format_timedelta(worked_time), f"{progress_percentage:.1f}% complete")
    if remaining_time > timedelta(0):
        table.add_row("Remaining Time", format_timedelta(remaining_time), "Until work ends")
    else:
        table.add_row("Overtime", format_timedelta(-remaining_time), "Work day exceeded") 
    # Add lunch information
    if lunch_savings > timedelta(0):
        table.add_row("Lunch Saved", format_timedelta(lunch_savings), "Time gained from short lunch")
    elif lunch_savings < timedelta(0):
        table.add_row("Lunch Overtime", format_timedelta(-lunch_savings), "Extra lunch time")
    
    # Clear console and display
    clear_console()
    console.print(table)
    
    # Add progress bar
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    )
    
    with progress:
        _ = progress.add_task("Work Progress", total=100, completed=progress_percentage)
        time.sleep(0.1)  # Brief pause to show progress bar
    
    # Add notifications for important events
    current_time = get_current_time()
    if abs((current_time - lunch_start).total_seconds()) < 30:
        console.print("[warning] Lunch time![/warning]")
    elif abs((current_time - end_time).total_seconds()) < 300:  # 5 minutes before end
        console.print("[highlight] Work day ending in 5 minutes![/highlight]")
    elif current_time >= end_time:
        console.print("[success] Work day completed! You can go home now.[/success]")

# Function to validate input times
def validate_times(start_time, lunch_start, lunch_end):
    """Validate that the input times make logical sense"""
    errors = []
    
    # Check if lunch start is reasonable (at least 1 hour after start)
    if lunch_start < start_time + timedelta(hours=1):
        errors.append("Lunch start should be at least 1 hour after work start")
    
    # Check if lunch duration is reasonable (between 15 minutes and 2 hours)
    lunch_duration = lunch_end - lunch_start
    if lunch_duration < timedelta(minutes=15):
        errors.append("Lunch duration should be at least 15 minutes")
    elif lunch_duration > timedelta(hours=2):
        errors.append("Lunch duration seems too long (>2 hours)")
    
    # Check if the total work day is reasonable (not more than 12 hours)
    total_day_duration = calculate_end_time(start_time, lunch_start, lunch_end) - start_time
    if total_day_duration > timedelta(hours=12):
        errors.append("Total work day duration exceeds 12 hours")
    
    return errors

# Main function to run the calculator
def main():
    parser = argparse.ArgumentParser(
        description="Office Hours Calculator - Track your work hours with lunch breaks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python office_hours.py --start 09:00 --lunch_start 13:00 --lunch_end 14:00
  python office_hours.py --start 10:30 --lunch_start 14:30 --lunch_end 15:15
        """
    )
    parser.add_argument("--start", required=True, 
                       help="Work start time in HH:MM format (24-hour)")
    parser.add_argument("--lunch_start", required=True, 
                       help="Lunch start time in HH:MM format (24-hour)")
    parser.add_argument("--lunch_end", required=True, 
                       help="Lunch end time in HH:MM format (24-hour)")
    parser.add_argument("--refresh", type=int, default=60,
                       help="Refresh interval in seconds (default: 60)")
    
    args = parser.parse_args()
    
    # Parse times
    start_time = parse_time_input(args.start)
    lunch_start = parse_time_input(args.lunch_start)
    lunch_end = parse_time_input(args.lunch_end)
    
    # Handle cross-day scenarios
    start_time, lunch_start, lunch_end = handle_cross_day(start_time, lunch_start, lunch_end)
    
    # Validate times
    errors = validate_times(start_time, lunch_start, lunch_end)
    if errors:
        console.print("[danger] Input validation errors:[/danger]")
        for error in errors:
            console.print(f"[danger]• {error}[/danger]")
        console.print("\n[info]Do you want to continue anyway? (y/n)[/info]")
        if input().lower() != 'y':
            sys.exit(1)
    
    # Set refresh interval
    global REFRESH_INTERVAL
    REFRESH_INTERVAL = args.refresh
    
    # Log the session start
    logger.info(f"Session started: Start={args.start}, Lunch={args.lunch_start}-{args.lunch_end}")
    
    console.print("[success] Office Hours Calculator started![/success]")
    console.print("[info]Press Ctrl+C to exit[/info]\n")
    
    try:
        while True:
            display_status(start_time, lunch_start, lunch_end)
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

# Entry point   
if __name__ == "__main__":
    main()
