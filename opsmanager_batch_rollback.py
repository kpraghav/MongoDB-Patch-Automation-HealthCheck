import requests
import json
import csv
import logging
import argparse
from requests.auth import HTTPDigestAuth

# Configure Logging
logging.basicConfig(
    filename="rollback_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
USERNAME = "<your-username>"
PASSWORD = "<your-password>"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

BACKUP_FILE = "opsmanager_backup.json"

def restore_config(group_id, backup_data):
    """Restore automationConfig for a given group"""
    if group_id not in backup_data:
        logging.error(f"No backup found for Group {group_id}")
        return False

    config = backup_data[group_id]
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"

    put_response = requests.put(url, headers=HEADERS, auth=HTTPDigestAuth(USERNAME, PASSWORD), json=config)

    if put_response.status_code == 200:
        logging.info(f"Rollback successful for Group {group_id}")
        return True
    else:
        logging.error(f"Rollback failed for Group {group_id}: {put_response.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Rollback MongoDB configurations from backup")
    parser.add_argument("--batch_file", required=True, help="Batch CSV file containing Group IDs to rollback")
    args = parser.parse_args()

    # Load backup data
    try:
        with open(BACKUP_FILE, "r") as file:
            backup_data = json.load(file)
    except Exception as e:
        logging.error(f"Error loading backup file: {e}")
        return

    # Read batch file
    with open(args.batch_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_id = row["GroupId"]
            restore_config(group_id, backup_data)

if __name__ == "__main__":
    main()
