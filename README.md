![Banner](banner.png)

# dm-data-age-shifter
Shifts date and time fields in a dataset by a random interval within a specified range, preserving temporal relationships. One shift is drawn for the whole run and applied to every named date column, so gaps within a column and between columns are preserved. The signed shift is drawn from --min_days to --max_days as set, with no sign flip, and the applied shift is logged. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowStrikeHQ/dm-data-age-shifter`

## Usage
`./dm-data-age-shifter [params]`

## Parameters
- `-h`: Show help message and exit
- `input_file`: Path to the input CSV file
- `output_file`: Path to the output CSV file. It must not be the input file: if the output path resolves to the input file, the run refuses and exits 1 before any write.
- `--min_days`: Minimum signed number of days to shift the dates by. Defaults to 0.
- `--max_days`: Maximum signed number of days to shift the dates by. Defaults to 365.
- `--date_columns`: List of column names containing date/time values.  Separate multiple columns with spaces.

## Failure rules
- If any named date column is not found, the run exits 1 and writes no output. With no --date_columns at all, the run still logs a warning that no dates will be shifted.
- A non-empty value in a named date column that does not parse as a date refuses the run: the run exits 1 naming the column, the count, and the CSV rows, instead of blanking the value. Empty cells may remain empty.

## License
Copyright (c) ShadowStrikeHQ
