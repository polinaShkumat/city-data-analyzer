# User Data Validator

A command-line tool in Python that cleans up a user list: it checks every record, separates valid and invalid users, logs the problems to a file, and lets an administrator fix broken records interactively.

## Features

- Validates each field with its own function:
  - **ID** – positive whole number
  - **Name** – not empty
  - **Age** – a number between 1 and 120
  - **Email** – exactly one `@`, a username, and a valid domain
- Skips lines with the wrong number of fields and reports the line number
- Writes all invalid records with the reason to `output/invalid_users.txt`
- Calculates the average age of valid users
- Interactive correction mode: pick an invalid record by ID, enter new values, and the record is re-validated before it moves to the valid list (duplicate IDs are rejected)

## How to run

Requires Python 3.8+ and no external libraries.

```bash
python validator.py                    # uses the sample file data/userdata.txt
python validator.py path/to/users.txt  # or your own file
```

## Input format

```
ID,Name,Age,Email
"1","Anna","24","anna@gmail.com"
"3","Chloe","abc","chloe@gmail.com"
```

## Example output

```
Line 4 (ID 3): skipped | Age 'abc' is not a number
Line 5 (ID 4): skipped | Email 'daan.example.com' must contain exactly one @
Line 14: skipped, expected 4 fields but got 3

----- RESULTS -----
Valid entries:   4
Invalid entries: 9
Average age of valid users: 42.5
```

## What I practised

File handling with `pathlib`, exception handling (`try` / `except` / `raise`), splitting a program into small single-purpose functions, and input validation, which is the first line of defence against bad or malicious data.
