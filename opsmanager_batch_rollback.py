import requests
import json

BACKUP_FILE = "opsmanager_backup.json"
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
AUTH = ("<your-username>", "<your-password>")

def rollback():
    with open(BACKUP_FILE, "r") as file:
        backup_data = json.load(file)

    for group in backup_data["results"]:
        requests.put(f"{BASE_URL}/groups/{group['id']}/automationConfig", auth=AUTH, json=group)

rollback()
