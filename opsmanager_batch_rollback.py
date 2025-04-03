import requests
import json
import logging
import argparse
from requests.auth import HTTPDigestAuth

# Constants
BACKUP_FILE = "opsmanager_backup.json"
LOG_FILE = "rollback_log.log"
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
USERNAME = "<your-username>"
PASSWORD = "<your-password>"

# Configure Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load backup data
def load_backup_data():
    """Load backup data from JSON file and detect its structure."""
    try:
        with open(BACKUP_FILE, "r") as file:
            backup_data = json.load(file)

        # If backup has "results" key (expected format)
        if isinstance(backup_data, dict) and "results" in backup_data:
            return {entry["groupId"]: entry["automationConfig"] for entry in backup_data["results"]}

        # If backup is a dictionary with groupId as keys
        elif isinstance(backup_data, dict):
            return {gid: data["automationConfig"] for gid, data in backup_data.items() if "automationConfig" in data}

        else:
            logging.error("Backup JSON is in an unknown format.")
            return None
    except Exception as e:
        logging.error(f"Failed to load backup file: {str(e)}")
        return None

# Load batch file data
def load_batch_file(batch_file):
    """Load the batch file to get group IDs to rollback."""
    try:
        with open(batch_file, "r") as file:
            group_ids = [line.strip().split(",")[0] for line in file.readlines()[1:]]  # Skip header
        return set(group_ids)
    except Exception as e:
        logging.error(f"Failed to load batch file {batch_file}: {str(e)}")
        return None

# Restore automation config
def rollback_group(group_id, config):
    """Send a PUT request to restore the group's automationConfig."""
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    try:
        response = requests.put(url, auth=HTTPDigestAuth(USERNAME, PASSWORD), json=config)
        response.raise_for_status()
        logging.info(f"Successfully rolled back Group {group_id}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to roll back Group {group_id}: {str(e)}")
        return False

# Main execution logic
def main():
    parser = argparse.ArgumentParser(description="Rollback MongoDB Ops Manager automation config")
    parser.add_argument("--batch_file", required=True, help="Path to the batch file containing group IDs for rollback")
    args = parser.parse_args()

    # Load backup data
    backup_data = load_backup_data()
    if not backup_data:
        logging.critical("Backup data is not in expected format. Aborting rollback.")
        return

    # Load batch file data
    batch_group_ids = load_batch_file(args.batch_file)
    if not batch_group_ids:
        logging.critical("Batch file could not be loaded or is empty. Aborting rollback.")
        return

    failed_rollbacks = []

    for group_id in batch_group_ids:
        automation_config = backup_data.get(group_id)

        if not automation_config:
            logging.warning(f"Skipping Group {group_id} - No backup data found")
            continue

        success = rollback_group(group_id, automation_config)
        if not success:
            failed_rollbacks.append({"groupId": group_id, "status": "Failed"})

    if failed_rollbacks:
        with open("rollback_failures.json", "w") as fail_file:
            json.dump(failed_rollbacks, fail_file, indent=4)
        logging.warning("Some rollbacks failed. Check rollback_failures.json.")

if __name__ == "__main__":
    main()
