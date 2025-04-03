import requests
import logging
import csv
import argparse
import time
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
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

def get_automation_config(group_id):
    """Fetch current automation config for a group."""
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    response = requests.get(url, headers=HEADERS, auth=HTTPDigestAuth(USERNAME, PASSWORD))

    if response.status_code != 200:
        logging.error(f"Failed to fetch automation config for {group_id}: {response.text}")
        return None

    return response.json()

def rollback_version(group_id, backup_config):
    """Rollback MongoDB version for a group using backup config."""
    if not backup_config:
        logging.error(f"No backup config found for {group_id}, skipping rollback.")
        return False

    # Increment `automationConfig` version before rollback
    if "version" in backup_config:
        backup_config["version"] += 1
    else:
        logging.error(f"No 'version' field found in automationConfig for {group_id}, skipping rollback.")
        return False

    # Send rollback request
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    response = requests.put(url, headers=HEADERS, auth=HTTPDigestAuth(USERNAME, PASSWORD), json=backup_config)

    if response.status_code == 200:
        logging.info(f"Rollback successful for Group {group_id}")
        return True
    else:
        logging.error(f"Rollback failed for Group {group_id}: {response.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Rollback MongoDB for batch groups")
    parser.add_argument("--backup_file", required=True, help="Backup file to restore from")
    args = parser.parse_args()

    rollback_status = []

    with open(args.backup_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_id = row["GroupId"]
            backup_config_file = f"backup_data/{group_id}_backup.json"

            try:
                with open(backup_config_file, "r") as backup_file:
                    backup_config = backup_file.read()
                    backup_config = eval(backup_config)  # Convert string back to dict

                success = rollback_version(group_id, backup_config)
                rollback_status.append({"GroupId": group_id, "Status": "Success" if success else "Failed"})

            except Exception as e:
                logging.error(f"Error processing rollback for {group_id}: {str(e)}")
                rollback_status.append({"GroupId": group_id, "Status": "Failed - Exception"})

    # Write rollback status to CSV
    rollback_status_file = f"rollback_status_{int(time.time())}.csv"
    with open(rollback_status_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["GroupId", "Status"])
        writer.writeheader()
        writer.writerows(rollback_status)

    logging.info(f"Rollback status saved to {rollback_status_file}")

if __name__ == "__main__":
    main()
