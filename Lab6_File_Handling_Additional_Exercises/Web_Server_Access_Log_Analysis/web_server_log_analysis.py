
import csv
import json
import shutil
import os
from collections import Counter

STUDENT_ID = "TUPM-26-3228"
ID_SUM = "23"
SEED_DIGIT = "8"

RECORD_LIMIT = f"{(1000 + int(ID_SUM))}"
TARGET_CLASS = (int(SEED_DIGIT) % 4) + 2

DATASET_FILE = "weblog.csv"
FILTERED_FILE = "filtered_logs.csv"
SUMMARY_FILE = "log_summary.json"
BACKUP_FILE = "log_summary_backup.json"


records_processed = 0
target_records = 0

status_counts = Counter()
url_counts = Counter()

status_class_counts = {
    "2xx": 0,
    "3xx": 0,
    "4xx": 0,
    "5xx": 0
}


try:
    with open(DATASET_FILE, "r", newline="", encoding="utf-8-sig") as csvfile:

        reader = csv.DictReader(csvfile)

        reader.fieldnames = [
            name.strip().lower() for name in reader.fieldnames
        ]

        required_columns = {"ip", "time", "url", "staus"}

        if not required_columns.issubset(set(reader.fieldnames)):
            raise ValueError(
                "CSV must contain IP, Time, URL, and Staus columns."
            )

        with open(
            FILTERED_FILE, "w", newline="", encoding="utf-8"
        ) as outputfile:

            writer = csv.DictWriter(
                outputfile,
                fieldnames=["IP", "Time", "URL", "Staus"]
            )

            writer.writeheader()

            for row in reader:

                if records_processed >= int(RECORD_LIMIT):
                    break

                records_processed += 1

                ip = row["ip"].strip()
                time = row["time"].strip()
                url = row["url"].strip()
                status = int(row["staus"].strip())

                status_counts[str(status)] += 1

                status_class = status // 100

                if status_class in (2, 3, 4, 5):
                    class_name = str(status_class) + "xx"
                    status_class_counts[class_name] += 1

                if status_class == TARGET_CLASS:

                    target_records += 1

                    url_counts[url] += 1

                    writer.writerow({
                        "IP": ip,
                        "Time": time,
                        "URL": url,
                        "Staus": status
                    })

    
    top_five_urls = url_counts.most_common(5)

    
    summary = {
        "student_id": STUDENT_ID,
        "id_sum": ID_SUM,
        "seed_digit": SEED_DIGIT,
        "records_processed": records_processed,
        "target_status_class": str(TARGET_CLASS) + "xx",
        "target_records": target_records,

        "status_class_counts": status_class_counts,

        "status_code_counts": dict(status_counts),

        "top_5_requested_urls": [
            {
                "url": url,
                "requests": count
            }
            for url, count in top_five_urls
        ],

        "filtered_csv_file": FILTERED_FILE
    }

    with open(SUMMARY_FILE, "w", encoding="utf-8") as jsonfile:
        json.dump(summary, jsonfile, indent=4)

    
    shutil.copy2(SUMMARY_FILE, BACKUP_FILE)

    backup_verified = os.path.exists(BACKUP_FILE)

    print("\n======================================")
    print(" WEB SERVER ACCESS LOG ANALYSIS")
    print("======================================")

    print("Student ID:", STUDENT_ID)
    print("ID_SUM:", ID_SUM)
    print("SEED_DIGIT:", SEED_DIGIT)

    print("\n--- DATA PROCESSING ---")
    print("Records Processed:", records_processed)
    print("Target Status Class:", str(TARGET_CLASS) + "xx")
    print("Target Records:", target_records)

    print("\n--- STATUS CLASS COUNTS ---")

    for name, count in status_class_counts.items():
        print(name + ":", count)

    print("\n--- REQUESTS PER STATUS CODE ---")

    for code, count in sorted(status_counts.items()):
        print(code + ":", count)

    print("\n--- TOP 5 REQUESTED URLS ---")

    if top_five_urls:
        for rank, (url, count) in enumerate(top_five_urls, start=1):
            print(f"{rank}. {url} - {count} requests")
    else:
        print("No matching URLs found.")

    print("\n--- EXPORTED FILES ---")
    print("Filtered CSV:", FILTERED_FILE)
    print("JSON Summary:", SUMMARY_FILE)
    print("JSON Backup:", BACKUP_FILE)

    print("\nBackup Verification:",
          "SUCCESS" if backup_verified else "FAILED")

    print("\n======================================")
    print("ANALYSIS COMPLETED")
    print("======================================")

except FileNotFoundError:
    print("ERROR: weblog.csv was not found.")
    print("Place the dataset in the same folder as this program.")

except (ValueError, KeyError) as error:
    print("DATA ERROR:", error)

except OSError as error:
    print("FILE ERROR:", error)

