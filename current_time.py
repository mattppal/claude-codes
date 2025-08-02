#!/usr/bin/env python3
"""
A simple program that prints the current time in a readable format.
"""

from datetime import datetime

def print_current_time():
    """Print the current date and time in a nice format."""
    now = datetime.now()
    
    # Format the time in a readable way
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    day_of_week = now.strftime("%A")
    
    print(f"Current date and time: {formatted_time}")
    print(f"Day of the week: {day_of_week}")

if __name__ == "__main__":
    print("🕒 Current Time Display")
    print("=" * 25)
    print_current_time()