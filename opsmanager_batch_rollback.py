import requests
import logging
import argparse
import json
import csv
from requests.auth import HTTPDigestAuth

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("rollback_log.log"),
        logging.StreamHandler()
    ]
)

# MongoDB Ops Manager API details
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
USERNAME = "<your-username>"
PASSWORD = "<your-password>"
auth = HTTPDigestAuth(USERNAME, PASSWORD)

# Paths
BACKUP_FILE = "opsmanager_backup.json"  # Backup data for rollback
ROLLBACK_STATUS_FILE = "rollback_status.csv"  # Rollback results

def load_backup_data():
    """Load backup data from JSON file."""
    try:
        with open(BACKUP_FILE, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Failed to load backup file: {str(e)}")
        return None

def rollback(group_id, backup_data):
    """Restore automationConfig for a given Group ID."""
    try:
        logging.info(f"Rolling back Group ID: {group_id}")

        # Fetch original config from backup
        original_config = next((item for item in backup_data if item['groupId'] == group_id), None)
        if not original_config:
            logging.error(f"No backup found for Group {group_id}. Skipping rollback.")
            return False

        # Restore automationConfig via API
        response = requests.put(
            f"{BASE_URL}/groups/{group_id}/automationConfig",
            headers={"Content-Type": "application/json"},
            auth=auth,
            json=original_config["automationConfig"]
        )
        response.raise_for_status()

        logging.info(f"Rollback successful for Group {group_id}")
        return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Rollback failed for Group {group_id}: {str(e)}")
        return False

def read_batch_file(batch_file):
    """Read group IDs from the batch file."""
    group_ids = []
    try:
        with open(batch_file, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    group_ids.append(row[0])  # Assuming Group ID is in the first column
    except Exception as e:
        logging.error(f"Error reading batch file {batch_file}: {str(e)}")
    
    return group_ids

def main():
    parser = argparse.ArgumentParser(description="MongoDB Ops Manager Batch Rollback Script")
    parser.add_argument("--batch_file", required=True, help="CSV file containing batch Group IDs")
    args = parser.parse_args()

    # Load backup data
    backup_data = load_backup_data()
    if not backup_data:
        logging.critical("Backup data missing. Aborting rollback.")
        return

    # Read Group IDs from batch file
    group_ids = read_batch_file(args.batch_file)
    if not group_ids:
        logging.critical(f"No valid Group IDs found in {args.batch_file}. Exiting.")
        return

    rollback_results = []

    for group_id in group_ids:
        success = rollback(group_id, backup_data)
        rollback_results.append({"groupId": group_id, "status": "Success" if success else "Failed"})

    # Write rollback results to CSV
    try:
        with open(ROLLBACK_STATUS_FILE, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["groupId", "status"])
            writer.writeheader()
            writer.writerows(rollback_results)
        logging.info(f"Rollback status written to {ROLLBACK_STATUS_FILE}")
    except Exception as e:
        logging.error(f"Failed to write rollback status CSV: {str(e)}")

if __name__ == "__main__":
    main()
