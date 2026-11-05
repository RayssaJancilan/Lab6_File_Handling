
import csv
import json
import shutil
import os

STUDENT_ID = "TUPM-26-3228"
SEED_DIGIT = "8"

OPERATING_SYSTEM = (
    "Android" if int(SEED_DIGIT) % 2 == 0 else "iOS"
)

TARGET_BEHAVIOR_CLASS = (int(SEED_DIGIT) % 5) + 1

INPUT_FILE = "user_behavior_dataset.csv"
EXPORTED_FILE = "selected_users.csv"
SUMMARY_FILE = "usage_summary.json"
BACKUP_FILE = "selected_users_backup.csv"

total_records = 0
matching_os_records = 0
selected_records = 0

total_battery_drain = 0.0
total_data_usage = 0.0

def find_column(headers, required_name):
    """
    Find a CSV column without depending on
    capitalization or extra spaces.
    """
    for header in headers:
        if header.strip().lower() == required_name.lower():
            return header

    raise ValueError(
        f"Missing required CSV column: {required_name}"
    )

try:

    with open(
        INPUT_FILE, "r", newline="", encoding="utf-8-sig"
    ) as csvfile:

        reader = csv.DictReader(csvfile)

        if not reader.fieldnames:
            raise ValueError("The CSV file has no headers.")

        user_id_col = find_column(
            reader.fieldnames, "User ID"
        )

        device_col = find_column(
            reader.fieldnames, "Device Model"
        )

        os_col = find_column(
            reader.fieldnames, "Operating System"
        )

        battery_col = find_column(
            reader.fieldnames, "Battery Drain (mAh/day)"
        )

        data_col = find_column(
            reader.fieldnames, "Data Usage (MB/day)"
        )

        behavior_col = find_column(
            reader.fieldnames, "User Behavior Class"
        )

        with open(
            EXPORTED_FILE, "w", newline="", encoding="utf-8"
        ) as outputfile:

            fieldnames = [
                "User ID",
                "Device Model",
                "Operating System",
                "Battery Drain (mAh/day)",
                "Data Usage (MB/day)"
            ]

            writer = csv.DictWriter(
                outputfile,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for row in reader:

                total_records += 1

                operating_system = row[os_col].strip()

                if operating_system.lower() != OPERATING_SYSTEM.lower():
                    continue

                matching_os_records += 1

                behavior_class = int(
                    row[behavior_col].strip()
                )

                if behavior_class != TARGET_BEHAVIOR_CLASS:
                    continue

                battery_drain = float(
                    row[battery_col].strip()
                )

                data_usage = float(
                    row[data_col].strip()
                )

                selected_records += 1

                total_battery_drain += battery_drain
                total_data_usage += data_usage

                writer.writerow({
                    "User ID": row[user_id_col],
                    "Device Model": row[device_col],
                    "Operating System": operating_system,
                    "Battery Drain (mAh/day)": battery_drain,
                    "Data Usage (MB/day)": data_usage
                })
    if selected_records > 0:

        average_battery_drain = (
            total_battery_drain / selected_records
        )

        average_data_usage = (
            total_data_usage / selected_records
        )

    else:

        average_battery_drain = None
        average_data_usage = None

    exported_count = 0

    with open(
        EXPORTED_FILE, "r", newline="", encoding="utf-8"
    ) as exported_file:

        exported_reader = csv.DictReader(exported_file)

        for row in exported_reader:
            exported_count += 1

    count_verified = exported_count == selected_records

    summary = {

        "student_id": STUDENT_ID,

        "seed_digit": SEED_DIGIT,

        "assigned_operating_system": OPERATING_SYSTEM,

        "target_behavior_class": TARGET_BEHAVIOR_CLASS,

        "total_records_in_dataset": total_records,

        "records_matching_operating_system":
            matching_os_records,

        "records_in_target_behavior_class":
            selected_records,

        "average_battery_drain_mAh_per_day":
            average_battery_drain,

        "average_data_usage_MB_per_day":
            average_data_usage,

        "exported_record_count": exported_count,

        "count_verification":
            "PASSED" if count_verified else "FAILED",

        "exported_csv_file": EXPORTED_FILE

    }

    with open(
        SUMMARY_FILE, "w", encoding="utf-8"
    ) as jsonfile:

        json.dump(summary, jsonfile, indent=4)

    shutil.copy2(EXPORTED_FILE, BACKUP_FILE)

    backup_exists = os.path.exists(BACKUP_FILE)

    if backup_exists:
        backup_size = os.path.getsize(BACKUP_FILE)
    else:
        backup_size = 0

    
    print("\n======================================")
    print(" MOBILE DEVICE USAGE PROFILING")
    print("======================================")

    print("Student ID:", STUDENT_ID)
    print("SEED_DIGIT:", SEED_DIGIT)

    print("\n--- ASSIGNED CRITERIA ---")

    print("Operating System:", OPERATING_SYSTEM)
    print("Target Behavior Class:", TARGET_BEHAVIOR_CLASS)

    print("\n--- DATA PROCESSING ---")

    print("Total Records in Dataset:", total_records)

    print("Records Matching Operating System:",
          matching_os_records)

    print("Records in Target Behavior Class:",
          selected_records)

    print("\n--- USAGE STATISTICS ---")

    if selected_records > 0:

        print(
            "Average Battery Drain:",
            f"{average_battery_drain:.2f} mAh/day"
        )

        print(
            "Average Data Usage:",
            f"{average_data_usage:.2f} MB/day"
        )

    else:

        print("No matching records found.")
        print("Average Battery Drain: N/A")
        print("Average Data Usage: N/A")

    print("\n--- COUNT VERIFICATION ---")

    print("Selected Records:", selected_records)
    print("Exported Records:", exported_count)

    print(
        "Verification:",
        "PASSED" if count_verified else "FAILED"
    )

    print("\n--- EXPORTED FILES ---")

    print("CSV File:", EXPORTED_FILE)
    print("JSON Summary:", SUMMARY_FILE)
    print("Backup File:", BACKUP_FILE)

    print("\nBackup Verification:",
          "SUCCESS" if backup_exists else "FAILED")

    print("Backup File Size:", backup_size, "bytes")

    print("\n======================================")
    print(" PROFILING COMPLETED")
    print("======================================")

except FileNotFoundError:

    print("ERROR: Dataset file was not found.")
    print("Please place user_behavior_dataset.csv")
    print("in the same folder as this Python program.")

except (ValueError, KeyError, TypeError) as error:

    print("DATA ERROR:", error)

except OSError as error:

    print("FILE ERROR:", error)

