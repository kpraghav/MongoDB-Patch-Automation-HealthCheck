import requests
import json
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.FileHandler("backup.log"), logging.StreamHandler()])

BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
AUTH = ("<your-username>", "<your-password>")
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
BACKUP_FILE = "opsmanager_backup.json"

def get_all_groups():
    """Fetch all Ops Manager groups."""
    response = requests.get(f"{BASE_URL}/groups", headers=HEADERS, auth=AUTH)
    response.raise_for_status()
    return response.json()["results"]

def backup_groups():
    """Save all group configurations to a file."""
    groups = get_all_groups()
    with open(BACKUP_FILE, "w") as file:
        json.dump({"results": groups}, file, indent=4)
    logging.info(f"Backup completed: {BACKUP_FILE}")

if __name__ == "__main__":
    backup_groups()
