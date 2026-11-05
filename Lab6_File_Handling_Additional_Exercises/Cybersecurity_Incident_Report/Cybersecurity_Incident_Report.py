
import csv
import json
import os
import shutil
from collections import Counter

SEED_DIGIT = 8
TARGET_YEAR = 2015 + SEED_DIGIT

INPUT_FILE = "Global_Cybersecurity_Threats_2015-2024.csv"
FILTERED_FILE = "filtered_incidents.csv"
JSON_FILE = "costliest_incidents.json"
BACKUP_FILE = "costliest_incidents_backup.json"
REPORT_FILE = "cybersecurity_report.txt"

total_records = 0
selected_incidents = []
valid_losses = []
attack_counts = Counter()

invalid_loss_count = 0

def find_column(headers, column_name):
    for header in headers:
        if header.strip().lower() == column_name.lower():
            return header

    raise ValueError(
        "Required column not found: " + column_name
    )


try:

    with open(
        INPUT_FILE, "r", newline="", encoding="utf-8-sig"
    ) as csvfile:

        reader = csv.DictReader(csvfile)

        if not reader.fieldnames:
            raise ValueError("Dataset has no column headers.")

        year_col = find_column(
            reader.fieldnames, "Year"
        )

        attack_col = find_column(
            reader.fieldnames, "Attack Type"
        )

        loss_col = find_column(
            reader.fieldnames, "Financial Loss (in Million $)"
        )

        original_fields = reader.fieldnames

        for row in reader:

            total_records += 1

            try:
                year = int(row[year_col].strip())
            except (ValueError, AttributeError):
                continue

            if year != TARGET_YEAR:
                continue

            incident = dict(row)
            incident["_original_order"] = total_records

            selected_incidents.append(incident)

            attack_type = row[attack_col].strip()

            if attack_type:
                attack_counts[attack_type] += 1
            else:
                attack_counts["Unknown"] += 1

            try:
                loss = float(row[loss_col].strip())

                if loss < 0 or not (
                    loss == loss and abs(loss) != float("inf")
                ):
                    raise ValueError("Invalid financial loss")

                valid_losses.append({
                    "order": total_records,
                    "record": incident,
                    "loss": loss
                })

            except (ValueError, TypeError, AttributeError):
                invalid_loss_count += 1

    total_loss = sum(
        item["loss"] for item in valid_losses
    )

    valid_loss_count = len(valid_losses)

    if valid_loss_count > 0:

        average_loss = total_loss / valid_loss_count

    else:

        average_loss = None

    ranked_incidents = sorted(
        valid_losses,
        key=lambda item: (
            -item["loss"],
            item["order"]
        )
    )

    top_five = ranked_incidents[:5]

    json_records = []

    for rank, item in enumerate(top_five, start=1):

        record = {
            key: value
            for key, value in item["record"].items()
            if key != "_original_order"
        }

        record["financial_loss_value"] = item["loss"]
        record["rank"] = rank

        json_records.append(record)

    with open(
        FILTERED_FILE, "w", newline="", encoding="utf-8"
    ) as outputfile:

        writer = csv.DictWriter(
            outputfile,
            fieldnames=original_fields
        )

        writer.writeheader()

        for incident in selected_incidents:

            clean_record = {
                key: value
                for key, value in incident.items()
                if key != "_original_order"
            }

            writer.writerow(clean_record)


    json_summary = {
        "target_year": TARGET_YEAR,
        "total_records_in_dataset": total_records,
        "incidents_in_target_year": len(selected_incidents),
        "valid_financial_loss_records": valid_loss_count,
        "invalid_financial_loss_records": invalid_loss_count,
        "total_financial_loss_million_usd": round(
            total_loss, 2
        ),
        "average_financial_loss_million_usd": (
            round(average_loss, 2)
            if average_loss is not None else None
        ),
        "five_costliest_incidents": json_records
    }

    with open(
        JSON_FILE, "w", encoding="utf-8"
    ) as jsonfile:

        json.dump(json_summary, jsonfile, indent=4)

    shutil.copy2(JSON_FILE, BACKUP_FILE)

    with open(JSON_FILE, "rb") as original:
        original_content = original.read()

    with open(BACKUP_FILE, "rb") as backup:
        backup_content = backup.read()

    backup_verified = (
        os.path.exists(BACKUP_FILE)
        and original_content == backup_content
    )

    backup_size = os.path.getsize(BACKUP_FILE)


    exported_count = 0

    with open(
        FILTERED_FILE, "r", newline="", encoding="utf-8"
    ) as exported_file:

        exported_reader = csv.DictReader(exported_file)

        for row in exported_reader:
            exported_count += 1

    count_verified = (
        exported_count == len(selected_incidents)
    )


    report_lines = []

    report_lines.append("========================================")
    report_lines.append("       CYBERSECURITY INCIDENT REPORT")
    report_lines.append("========================================")

    report_lines.append("")
    report_lines.append("TARGET YEAR: " + str(TARGET_YEAR))

    report_lines.append("")
    report_lines.append("--- DATASET INFORMATION ---")
    report_lines.append(
        "Total records in dataset: " + str(total_records)
    )
    report_lines.append(
        "Incidents in target year: "
        + str(len(selected_incidents))
    )

    report_lines.append("")
    report_lines.append("--- COUNT PER ATTACK TYPE ---")

    if attack_counts:

        for attack, count in sorted(attack_counts.items()):
            report_lines.append(
                attack + ": " + str(count)
            )

    else:

        report_lines.append("No incidents found.")

    report_lines.append("")
    report_lines.append("--- FINANCIAL LOSS ---")

    report_lines.append(
        "Valid financial records: " + str(valid_loss_count)
    )

    report_lines.append(
        "Invalid financial records: " + str(invalid_loss_count)
    )

    report_lines.append(
        "Total financial loss: $"
        + f"{total_loss:.2f} million"
    )

    if average_loss is not None:

        report_lines.append(
            "Average financial loss: $"
            + f"{average_loss:.2f} million"
        )

    else:

        report_lines.append(
            "Average financial loss: N/A"
        )

    report_lines.append("")
    report_lines.append("--- FIVE COSTLIEST INCIDENTS ---")

    if top_five:

        for rank, item in enumerate(top_five, start=1):

            record = item["record"]

            report_lines.append(
                f"{rank}. {record[attack_col]} "
                f"| Loss: ${item['loss']:.2f} million "
                f"| Original record: {item['order']}"
            )

    else:

        report_lines.append(
            "No valid financial loss records found."
        )

    report_lines.append("")
    report_lines.append("--- OUTPUT FILES ---")

    report_lines.append(
        "Filtered CSV: " + FILTERED_FILE
    )

    report_lines.append(
        "JSON Summary: " + JSON_FILE
    )

    report_lines.append(
        "JSON Backup: " + BACKUP_FILE
    )

    report_lines.append(
        "Text Report: " + REPORT_FILE
    )

    report_lines.append(
        "Exported CSV records: " + str(exported_count)
    )

    report_lines.append(
        "CSV count verification: "
        + ("PASSED" if count_verified else "FAILED")
    )

    report_lines.append(
        "Backup verification: "
        + ("PASSED" if backup_verified else "FAILED")
    )

    report_lines.append(
        "Backup file size: " + str(backup_size) + " bytes"
    )

    report_lines.append("")
    report_lines.append("========================================")
    report_lines.append("          END OF REPORT")
    report_lines.append("========================================")

    report_text = "\n".join(report_lines)

    with open(
        REPORT_FILE, "w", encoding="utf-8"
    ) as report_file:

        report_file.write(report_text)

    print(report_text)

    print("\nReport successfully saved.")

except FileNotFoundError:

    print("ERROR: Dataset CSV file not found.")
    print("Place the original CSV in the program folder.")

except (ValueError, KeyError) as error:

    print("DATA ERROR:", error)

except OSError as error:

    print("FILE ERROR:", error)

