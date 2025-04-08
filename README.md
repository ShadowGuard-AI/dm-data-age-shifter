# dm-data-age-shifter
Shifts date and time fields in a dataset by a random interval within a specified range, preserving temporal relationships. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowStrikeHQ/dm-data-age-shifter`

## Usage
`./dm-data-age-shifter [params]`

## Parameters
- `-h`: Show help message and exit
- `--min_days`: Minimum number of days to shift the dates by. Defaults to 0.
- `--max_days`: Maximum number of days to shift the dates by. Defaults to 365.
- `--date_columns`: List of column names containing date/time values.  Separate multiple columns with spaces.

## License
Copyright (c) ShadowStrikeHQ
