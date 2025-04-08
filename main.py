import argparse
import logging
import random
import pandas as pd
from datetime import timedelta
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the data age shifter tool.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="Shifts date and time fields in a dataset by a random interval within a specified range, preserving temporal relationships.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    parser.add_argument("--min_days", type=int, default=0, help="Minimum number of days to shift the dates by. Defaults to 0.")
    parser.add_argument("--max_days", type=int, default=365, help="Maximum number of days to shift the dates by. Defaults to 365.")
    parser.add_argument("--date_columns", nargs="+", help="List of column names containing date/time values.  Separate multiple columns with spaces.")
    return parser

def shift_date(date_value, min_days, max_days):
    """
    Shifts a single date/time value by a random number of days.

    Args:
        date_value (datetime): The date/time value to shift.
        min_days (int): The minimum number of days to shift.
        max_days (int): The maximum number of days to shift.

    Returns:
        datetime: The shifted date/time value, or the original value if it's not a valid date.
    """
    try:
        # Generate a random shift value within the specified range
        days_to_shift = random.randint(min_days, max_days)
        
        # Randomly determine whether to shift forward or backward in time
        if random.random() < 0.5:
            days_to_shift = -days_to_shift  # Shift backwards
        
        # Shift the date by the random value
        shifted_date = date_value + timedelta(days=days_to_shift)
        return shifted_date
    except Exception as e:
        logging.error(f"Error shifting date: {e}")
        return date_value  # Return the original value on error


def main():
    """
    Main function to parse arguments, read the CSV, shift dates, and save the output.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    min_days = args.min_days
    max_days = args.max_days
    date_columns = args.date_columns
    
    # Input validation
    if not os.path.exists(input_file):
        logging.error(f"Input file not found: {input_file}")
        sys.exit(1)
    
    if min_days > max_days:
        logging.error("Minimum days must be less than or equal to maximum days.")
        sys.exit(1)
    
    if not date_columns:
        logging.warning("No date columns specified.  The script will run, but no dates will be shifted.")

    try:
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(input_file)
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Process each specified date column
    for col in date_columns:
        if col not in df.columns:
            logging.warning(f"Column '{col}' not found in the DataFrame. Skipping.")
            continue

        # Attempt to convert the column to datetime objects.  Handle errors gracefully.
        try:
             df[col] = pd.to_datetime(df[col], errors='coerce') # Coerce invalid parsing into NaT.
             logging.info(f"Successfully converted column '{col}' to datetime objects.")
        except Exception as e:
            logging.error(f"Error converting column '{col}' to datetime: {e}. Skipping.")
            continue

        # Shift the date/time values in the specified column
        df[col] = df[col].apply(lambda x: shift_date(x, min_days, max_days) if pd.notnull(x) else x) # Only shift if not NaN

    try:
        # Write the modified DataFrame to a new CSV file
        df.to_csv(output_file, index=False)
        logging.info(f"Successfully shifted dates and saved to {output_file}")
    except Exception as e:
        logging.error(f"Error writing to CSV file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()