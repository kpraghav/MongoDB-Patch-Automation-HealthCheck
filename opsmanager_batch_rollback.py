import requests
import json
import csv
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.FileHandler("rollback_success.log"), logging.StreamHandler()])
error_log = logging.FileHandler("rollback_error.log")
error_log.setLevel(logging.ERROR)
logging.getLogger().addHandler(error_log)

BACKUP_FILE = "opsmanager_backup.json"
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
AUTH = ("<your-username>", "<your-password>")

def rollback(group_id, backup_data):
    """Rolls back a group to its previous configuration."""
    original_config = next((g for g in backup_data["results"] if g["id"] == group_id), None)
    if original_config:
        response = requests.put(f"{BASE_URL}/groups/{group_id}/automationConfig", auth=AUTH, json=original_config)
        response.raise_for_status()
        logging.info(f"Rollback successful for {group_id}")

if __name__ == "__main__":
    with open(BACKUP_FILE, "r") as file:
        backup_data = json.load(file)
    
    rollback("some_group_id", backup_data)  # Use batch file logic
