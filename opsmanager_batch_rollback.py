import requests
import json
import logging
import argparse
import csv
from requests.auth import HTTPDigestAuth

# Configure Logging
logging.basicConfig(
    filename='rollback_log.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# MongoDB Ops Manager API Details
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
USERNAME = "<your-username>"
PASSWORD = "<your-password>"
BACKUP_FILE = "opsmanager_backup.json"

# Read backup data and validate format
def load_backup_data():
    try:
        with open(BACKUP_FILE, 'r') as f:
            data = json.load(f)
        
        # Ensure correct format (dictionary expected)
        if not isinstance(data, dict):
            logging.error("Backup data is not in expected dictionary format. Aborting.")
            return None
        return data
    except Exception as e:
        logging.error(f"Error loading backup data: {e}")
        return None

# Read batch file for group IDs to roll back
def load_batch_group_ids(batch_file):
    try:
        group_ids = []
        with open(batch_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    group_ids.append(row[0])
        return group_ids
    except Exception as e:
        logging.error(f"Error reading batch file {batch_file}: {e}")
        return []

# Perform rollback for a single group
def rollback_group(group_id, backup_data):
    if group_id not in backup_data:
        logging.error(f"Group ID {group_id} not found in backup data. Skipping rollback.")
        return False

    automation_config = backup_data[group_id].get("automationConfig", {})
    if not automation_config:
        logging.error(f"No automationConfig found for Group ID {group_id}. Skipping rollback.")
        return False

    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    
    try:
        response = requests.put(
            url,
            auth=HTTPDigestAuth(USERNAME, PASSWORD),
            json=automation_config
        )
        
        if response.status_code == 200:
            logging.info(f"Successfully rolled back Group ID {group_id}.")
            return True
        else:
            logging.error(f"Rollback failed for Group ID {group_id}. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error during rollback for Group ID {group_id}: {e}")
        return False

# Main function
def main():
    parser = argparse.ArgumentParser(description="Rollback MongoDB Ops Manager Configuration")
    parser.add_argument('--batch_file', required=True, help="CSV file with Group IDs for rollback")
    args = parser.parse_args()

    backup_data = load_backup_data()
    if backup_data is None:
        logging.error("Failed to load backup data. Exiting.")
        return

    group_ids = load_batch_group_ids(args.batch_file)
    if not group_ids:
        logging.error("No valid Group IDs found in batch file. Exiting.")
        return

    failed_rollbacks = []

    for group_id in group_ids:
        success = rollback_group(group_id, backup_data)
        if not success:
            failed_rollbacks.append(group_id)

    # Write failed rollbacks to a JSON file
    if failed_rollbacks:
        with open('rollback_failures.json', 'w') as f:
            json.dump(failed_rollbacks, f, indent=4)
        logging.error(f"Rollback failed for {len(failed_rollbacks)} group(s). See rollback_failures.json.")

    logging.info("Rollback process completed.")

if __name__ == "__main__":
    main()
