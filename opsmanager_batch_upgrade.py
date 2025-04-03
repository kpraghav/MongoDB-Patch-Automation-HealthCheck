import requests
import logging
import csv
import argparse
import time
import json
from requests.auth import HTTPDigestAuth

# Configure Logging
logging.basicConfig(
    filename="upgrade_log.log",
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
    """Fetch automation config for a group."""
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    response = requests.get(url, headers=HEADERS, auth=HTTPDigestAuth(USERNAME, PASSWORD))

    if response.status_code != 200:
        logging.error(f"Failed to fetch automation config for {group_id}: {response.text}")
        return None

    return response.json()

def update_version(group_id, mongodb_version):
    """Upgrade MongoDB version for a group."""
    config = get_automation_config(group_id)

    if not config:
        logging.error(f"Skipping Group {group_id} due to missing config")
        return

    if "processes" not in config or not config["processes"]:
        logging.warning(f"No processes found for Group {group_id}, skipping upgrade.")
        return

    for process in config["processes"]:
        if "version" in process:
            logging.info(f"Updating {process['name']} in {group_id} to {mongodb_version}")
            process["version"] = mongodb_version
        else:
            logging.warning(f"No version field in {process['name']} for Group {group_id}")

    # Increment `automationConfig` version
    if "version" in config:
        config["version"] += 1
    else:
        logging.error(f"No 'version' field found in automationConfig for {group_id}, skipping.")
        return

    # Send updated config
    url = f"{BASE_URL}/groups/{group_id}/automationConfig"
    response = requests.put(url, headers=HEADERS, auth=HTTPDigestAuth(USERNAME, PASSWORD), json=config)

    if response.status_code == 200:
        logging.info(f"Upgrade successful for Group {group_id} to version {mongodb_version}")
    else:
        logging.error(f"Upgrade failed for Group {group_id}: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Upgrade MongoDB for batch groups")
    parser.add_argument("--file", required=True, help="Batch file to process")
    parser.add_argument("--version", required=True, help="MongoDB version to upgrade to")
    args = parser.parse_args()

    with open(args.file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_id, health = row["GroupId"], row["Health"]

            if health == "Healthy":
                update_version(group_id, args.version)
            else:
                logging.warning(f"Skipping upgrade for {group_id} due to poor health")

if __name__ == "__main__":
    main()
