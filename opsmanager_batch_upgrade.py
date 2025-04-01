import requests
import csv
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.FileHandler("upgrade_success.log"), logging.StreamHandler()])

BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
AUTH = ("<your-username>", "<your-password>")
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

def upgrade_group(group_id, version):
    """Upgrades a group to a specified MongoDB version."""
    response = requests.get(f"{BASE_URL}/groups/{group_id}/automationConfig", headers=HEADERS, auth=AUTH)
    response.raise_for_status()

    config = response.json()
    config["version"] += 1  
    for process in config.get("processes", []):
        process["version"] = version

    response = requests.put(f"{BASE_URL}/groups/{group_id}/automationConfig", headers=HEADERS, auth=AUTH, json=config)
    
    if response.status_code == 200:
        logging.info(f"Upgrade successful for {group_id}")
    else:
        logging.error(f"Upgrade failed for {group_id}: {response.text}")

def upgrade_batch(batch_file, version):
    with open(batch_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["health"] == "Healthy":
                upgrade_group(row["groupId"], version)
            else:
                logging.warning(f"Skipping {row['groupId']} due to poor health.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-file", required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    upgrade_batch(args.batch_file, args.version)
