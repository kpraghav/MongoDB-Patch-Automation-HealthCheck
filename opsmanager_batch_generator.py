import requests
import csv
import logging
import argparse

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.FileHandler("batch_generator.log"), logging.StreamHandler()])

BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
AUTH = ("<your-username>", "<your-password>")
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

def get_all_groups():
    """Fetch all group IDs."""
    response = requests.get(f"{BASE_URL}/groups", headers=HEADERS, auth=AUTH)
    response.raise_for_status()
    return [group["id"] for group in response.json()["results"]]

def check_health(group_id):
    """Check if all agents in a group are healthy."""
    response = requests.get(f"{BASE_URL}/groups/{group_id}/agents", headers=HEADERS, auth=AUTH)
    response.raise_for_status()
    unhealthy = [agent for agent in response.json()["results"] if agent["state"] != "ACTIVE"]
    return "Healthy" if len(unhealthy) == 0 else "Unhealthy"

def generate_batches(batch_size):
    """Creates batch CSV files with health status."""
    group_ids = get_all_groups()
    total_batches = (len(group_ids) + batch_size - 1) // batch_size
    
    for i in range(total_batches):
        batch = group_ids[i * batch_size:(i + 1) * batch_size]
        batch_file = f"batch_{i + 1}.csv"

        with open(batch_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["groupId", "health"])

            for group_id in batch:
                writer.writerow([group_id, check_health(group_id)])
        
        logging.info(f"Batch {i+1} created: {batch_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, required=True, help="Batch size")
    args = parser.parse_args()
    generate_batches(args.batch_size)
