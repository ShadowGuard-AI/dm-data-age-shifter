import argparse
import logging
import random
import pandas as pd
from datetime import timedelta
import os
import sys
from pathlib import Path

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
    parser.add_argument("output_file", help="Path to the output CSV file. It must not resolve to the input file.")
    parser.add_argument("--min_days", type=int, default=0, help="Minimum signed number of days to shift the dates by. Defaults to 0.")
    parser.add_argument("--max_days", type=int, default=365, help="Maximum signed number of days to shift the dates by. Defaults to 365.")
    parser.add_argument("--date_columns", nargs="+", help="List of column names containing date/time values.  Separate multiple columns with spaces.")
    return parser

def pick_run_shift(min_days, max_days):
    # One shift is picked for the whole run, not per value and not per
    # column. A shared shift keeps every interval exactly as it was, within
    # each column and between columns; only the whole timeline moves. The
    # signed shift is drawn directly from the range the operator set, with
    # no sign flip, so it always stays inside --min_days to --max_days.
    # There is no seed flag anywhere in this tool, so the draw cannot
    # be repeated: the only record of which shift a run used is the
    # log line in main, and rerunning gives a different timeline.
    return random.randint(min_days, max_days)


def shift_date(date_value, days_to_shift):
    """
    Shifts a single date/time value by an already chosen number of days.

    Args:
        date_value (datetime): The date/time value to shift.
        days_to_shift (int): The signed shift shared by the whole run.

    Returns:
        datetime: The shifted date/time value, or the original value on error.
    """
    try:
        return date_value + timedelta(days=days_to_shift)
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
    # argparse leaves this as None when the flag is absent. Normalise it
    # here: the warning below promises a no-op run, and iterating None
    # further down used to crash with a TypeError instead.
    date_columns = args.date_columns or []

    # Input validation
    if not os.path.exists(input_file):
        logging.error(f"Input file not found: {input_file}")
        sys.exit(1)
    
    if min_days > max_days:
        logging.error("Minimum days must be less than or equal to maximum days.")
        sys.exit(1)

    if Path(input_file).resolve() == Path(output_file).resolve():
        logging.error("Error: Output file cannot be the same file as the input file.")
        sys.exit(1)
    
    if not date_columns:
        logging.warning("No date columns specified.  The script will run, but no dates will be shifted.")

    try:
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(input_file)
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Every named column must exist. A run that shifts nothing must not
    # report success or write a verbatim copy of the input.
    missing_columns = [col for col in date_columns if col not in df.columns]
    if missing_columns:
        logging.error(
            "Error: Date column(s) not found in the input: "
            + ", ".join(missing_columns)
            + ". No dates were shifted."
        )
        sys.exit(1)

    # One shift for the whole run, applied to every named date column.
    run_shift = pick_run_shift(min_days, max_days) if date_columns else 0
    if date_columns:
        logging.info(f"Applying a shift of {run_shift} days to all date columns: {', '.join(date_columns)}")

    # Process each specified date column
    for col in date_columns:
        # Convert the column to datetime objects. A non-empty value that
        # does not parse must not be silently blanked: count such values
        # and refuse the run before any output is written. Empty cells
        # stay empty.
        original = df[col]
        try:
             converted = pd.to_datetime(original, errors='coerce')
        except Exception as e:
            logging.error(f"Error converting column '{col}' to datetime: {e}.")
            sys.exit(1)
        bad_mask = converted.isna() & original.notna() & (original.astype(str).str.strip() != "")
        bad_count = int(bad_mask.sum())
        if bad_count:
            # The +2 turns a zero based position into a CSV line number
            # (one for the header, one for one based counting). It is
            # only right while the frame index is the default position
            # index read_csv produced, which holds for this main flow.
            bad_rows = [int(pos) + 2 for pos in list(df.index[bad_mask])]
            logging.error(
                f"Error: Column '{col}' has {bad_count} non-empty value(s) that do not parse "
                f"as dates, at CSV row(s): {', '.join(str(n) for n in bad_rows)}. "
                "Refusing to blank them."
            )
            sys.exit(1)
        df[col] = converted
        logging.info(f"Successfully converted column '{col}' to datetime objects.")

        df[col] = df[col].apply(lambda x: shift_date(x, run_shift) if pd.notnull(x) else x) # Only shift if not NaN

    try:
        # Write the modified DataFrame to a new CSV file
        # Dates are written in the pandas default datetime form, not
        # in the form they were read in: a column of 31/01/2024 style
        # values comes back as ISO timestamps with a midnight time
        # attached. The values are right; the format is not preserved.
        df.to_csv(output_file, index=False)
        logging.info(f"Successfully shifted dates and saved to {output_file}")
    except Exception as e:
        logging.error(f"Error writing to CSV file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()