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
    """Load backup data from JSON file and ensure correct format."""
    try:
        with open(BACKUP_FILE, "r") as file:
            backup_data = json.load(file)

        if isinstance(backup_data, dict) and "results" in backup_data:
            results = backup_data["results"]
            if isinstance(results, list):
                return results
            else:
                logging.error("Expected 'results' to be a list but found different format.")
                return None
        else:
            logging.error("Backup JSON does not contain expected 'results' key.")
            return None
    except Exception as e:
        logging.error(f"Failed to load backup file: {str(e)}")
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
    args = parser.parse_args()

    backup_data = load_backup_data()
    if not backup_data:
        logging.critical("Backup data is not in expected format. Aborting rollback.")
        return

    failed_rollbacks = []

    for entry in backup_data:
        group_id = entry.get("groupId")
        automation_config = entry.get("automationConfig")

        if not group_id or not automation_config:
            logging.error(f"Skipping entry with missing data: {entry}")
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
