import requests
import csv
import logging
import argparse

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.FileHandler("upgrade_success.log"), logging.StreamHandler()])
error_log = logging.FileHandler("upgrade_error.log")
error_log.setLevel(logging.ERROR)
logging.getLogger().addHandler(error_log)

BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
AUTH = ("<your-username>", "<your-password>")
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

def upgrade_group(group_id, version):
    """Upgrades a group to a specified MongoDB version."""
    try:
        response = requests.get(f"{BASE_URL}/groups/{group_id}/automationConfig", headers=HEADERS, auth=AUTH)
        response.raise_for_status()

        config = response.json()
        config["version"] += 1  
        for process in config.get("processes", []):
            process["version"] = version

        response = requests.put(f"{BASE_URL}/groups/{group_id}/automationConfig", headers=HEADERS, auth=AUTH, json=config)
        response.raise_for_status()

        logging.info(f"Upgrade successful for {group_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Upgrade failed for {group_id}: {e}")

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
