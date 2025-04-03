import requests
import logging
import csv
import os
import argparse

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
AUTH = ("<your-username>", "<your-password>")
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

BATCH_DIR = "batch_files"

os.makedirs(BATCH_DIR, exist_ok=True)

def get_all_groups():
    """Fetch all group IDs."""
    try:
        response = requests.get(f"{BASE_URL}/groups", headers=HEADERS, auth=AUTH)
        response.raise_for_status()
        return [group["id"] for group in response.json().get("results", [])]
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch groups: {e}")
        return []

def check_health(group_id):
    """Check if all agents in a group are healthy."""
    try:
        response = requests.get(f"{BASE_URL}/groups/{group_id}/agents", headers=HEADERS, auth=AUTH)
        response.raise_for_status()
        unhealthy = [agent for agent in response.json().get("results", []) if agent["state"] != "ACTIVE"]
        return "Healthy" if not unhealthy else "Unhealthy"
    except requests.exceptions.RequestException as e:
        logging.error(f"Health check failed for {group_id}: {e}")
        return "Unknown"

def generate_batches(batch_size):
    """Creates batch CSV files with health status."""
    group_ids = get_all_groups()
    batches = [group_ids[i : i + batch_size] for i in range(0, len(group_ids), batch_size)]

    for i, batch in enumerate(batches):
        file_path = os.path.join(BATCH_DIR, f"batch_{i+1}.csv")
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["GroupId", "Health"])
            for group_id in batch:
                writer.writerow([group_id, check_health(group_id)])
        
        logging.info(f"Created batch file: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate batch files with health status")
    parser.add_argument("--batch-size", type=int, required=True, help="Batch size")
    args = parser.parse_args()

    generate_batches(args.batch_size)

if __name__ == "__main__":
    main()
