"""
User Data Validator
-------------------
Reads a CSV-like file with user records (ID, Name, Age, Email), validates every
field, logs the invalid records to a separate file and lets an administrator
correct them interactively.

Usage:
    python validator.py                      # uses data/userdata.txt
    python validator.py path/to/users.txt    # uses your own file
"""

import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent
DEFAULT_INPUT = BASE_DIR / "data" / "userdata.txt"
OUTPUT_DIR = BASE_DIR / "output"
INVALID_LOG = OUTPUT_DIR / "invalid_users.txt"


# ---------- helper ----------

def clean(raw_value):
    """Remove surrounding whitespace and double quotes."""
    return raw_value.strip().strip('"')


# ---------- one validation function per field ----------

def check_id(raw_id):
    cleaned = clean(raw_id)
    try:
        id_num = int(cleaned)
    except ValueError:
        raise ValueError(f"ID '{cleaned}' is not a whole number")
    if id_num <= 0:
        raise ValueError("ID must be greater than 0")
    return id_num


def check_name(raw_name):
    cleaned = clean(raw_name)
    if cleaned == "" or cleaned == "None":
        raise ValueError("Name is missing")
    return cleaned


def check_age(raw_age):
    cleaned = clean(raw_age)
    if cleaned == "" or cleaned == "None":
        raise ValueError("Age is missing")
    try:
        age_num = int(cleaned)
    except ValueError:
        raise ValueError(f"Age '{cleaned}' is not a number")
    if age_num <= 0 or age_num > 120:
        raise ValueError(f"Age {age_num} is not realistic (must be 1-120)")
    return age_num


def check_email(raw_email):
    cleaned = clean(raw_email)
    if cleaned == "" or cleaned == "None":
        raise ValueError("Email is missing")
    if cleaned.count("@") != 1:
        raise ValueError(f"Email '{cleaned}' must contain exactly one @")

    username, domain = cleaned.split("@")
    if username == "":
        raise ValueError(f"Email '{cleaned}' has nothing before the @")
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError(f"Email '{cleaned}' has an invalid domain")
    return cleaned


def validate_user(raw_id, raw_name, raw_age, raw_email):
    """Validate all fields. Raises ValueError on the first problem found."""
    return {
        "id": check_id(raw_id),
        "name": check_name(raw_name),
        "age": check_age(raw_age),
        "email": check_email(raw_email),
    }


# ---------- reading the file ----------

def load_users(path):
    """Split the file into a list of valid users and a list of invalid ones."""
    valid_users = []
    invalid_users = []

    with path.open("r", encoding="utf-8") as f:
        next(f)  # skip the header line
        for line_number, line in enumerate(f, start=2):
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) != 4:
                print(f"Line {line_number}: skipped, expected 4 fields but got {len(parts)}")
                continue

            raw_id, raw_name, raw_age, raw_email = parts

            try:
                valid_users.append(validate_user(raw_id, raw_name, raw_age, raw_email))
            except ValueError as error:
                print(f"Line {line_number} (ID {clean(raw_id)}): skipped | {error}")
                invalid_users.append({
                    "id": clean(raw_id),
                    "name": clean(raw_name),
                    "age": clean(raw_age),
                    "email": clean(raw_email),
                    "reason": str(error),
                })

    return valid_users, invalid_users


def log_invalid_users(invalid_users, path):
    """Write all invalid entries to a separate file for review."""
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("ID, Name, Age, Email, Reason\n")
        for user in invalid_users:
            f.write(f"{user['id']}, {user['name']}, {user['age']}, "
                    f"{user['email']}, {user['reason']}\n")


def average_age(users):
    if not users:
        return None
    return round(sum(user["age"] for user in users) / len(users), 1)


# ---------- administrator corrections ----------

def show_invalid_users(invalid_users):
    print("\n----- INVALID RECORDS -----")
    for user in invalid_users:
        print(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}, "
              f"Email: {user['email']}  -> {user['reason']}")


def find_invalid_by_id(invalid_users, wanted_id):
    for user in invalid_users:
        if user["id"] == wanted_id:
            return user
    return None


def correct_records(valid_users, invalid_users):
    """Let the administrator fix invalid records one by one."""
    while True:
        if not invalid_users:
            print("\nAll invalid records have been corrected!")
            break

        show_invalid_users(invalid_users)
        choice = input("\nEnter the ID to correct (or 'stop' to finish): ").strip()

        if choice.lower() == "stop":
            break

        record = find_invalid_by_id(invalid_users, choice)
        if record is None:
            print(f"No invalid record with ID '{choice}' was found.")
            continue

        print(f"\nCurrent details: Name: {record['name']}, Age: {record['age']}, "
              f"Email: {record['email']}")
        new_id = input(f"New ID (Enter to keep '{record['id']}'): ").strip() or record["id"]
        new_name = input("New name: ")
        new_age = input("New age: ")
        new_email = input("New email: ")

        try:
            corrected = validate_user(new_id, new_name, new_age, new_email)
        except ValueError as error:
            print(f"Correction rejected: {error}. The record stays invalid, try again.")
            continue

        if any(user["id"] == corrected["id"] for user in valid_users):
            print(f"Correction rejected: ID {corrected['id']} is already used by a valid user.")
            continue

        # Only reached if every check passed
        invalid_users.remove(record)
        valid_users.append(corrected)
        valid_users.sort(key=lambda user: user["id"])
        print(f"Record {corrected['id']} corrected and moved to the valid users!")


def show_valid_users(valid_users):
    print("\n----- ALL VALID USERS -----")
    for user in valid_users:
        print(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}, "
              f"Email: {user['email']}")


# ---------- main program ----------

def main():
    parser = argparse.ArgumentParser(description="Validate and correct user records.")
    parser.add_argument("input_file", nargs="?", default=DEFAULT_INPUT, type=Path,
                        help="path to the user data file (default: data/userdata.txt)")
    args = parser.parse_args()

    try:
        valid_users, invalid_users = load_users(args.input_file)
    except FileNotFoundError:
        print(f"File not found: {args.input_file}. Check the path and try again.")
        return

    print("\n----- RESULTS -----")
    print(f"Valid entries:   {len(valid_users)}")
    print(f"Invalid entries: {len(invalid_users)}")
    print(f"Average age of valid users: {average_age(valid_users)}")

    log_invalid_users(invalid_users, INVALID_LOG)
    print(f"Invalid entries logged to {INVALID_LOG.relative_to(BASE_DIR)}")

    correct_records(valid_users, invalid_users)

    show_valid_users(valid_users)
    print(f"\nFinal number of valid users: {len(valid_users)}")
    print(f"Final average age: {average_age(valid_users)}")


if __name__ == "__main__":
    main()
