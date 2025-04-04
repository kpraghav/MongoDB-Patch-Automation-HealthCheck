import requests
import logging
import argparse
import csv
import os
from requests.auth import HTTPDigestAuth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants (replace with your values)
BASE_URL = "https://<ops-manager-url>/api/public/v1.0"
USERNAME = "<your-username>"
PASSWORD = "<your-password>"

# Output directory
OUTPUT_DIR = "batch_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_groups():
    logging.info("Fetching group IDs and names with pagination...")
    groups = []
    page = 1
    limit = 100

    while True:
        response = requests.get(f"{BASE_URL}/groups?pageNum={page}&itemsPerPage={limit}",
                                auth=HTTPDigestAuth(USERNAME, PASSWORD))
        response.raise_for_status()
        results = response.json().get('results', [])

        if not results:
            break

        for group in results:
            groups.append({
                'id': group['id'],
                'name': group.get('name', 'Unknown')
            })

        page += 1

    logging.info(f"Total Groups Found: {len(groups)}")
    return groups

def check_agent_health(group_id):
    try:
        response = requests.get(f"{BASE_URL}/groups/{group_id}/agents", auth=HTTPDigestAuth(USERNAME, PASSWORD))
        response.raise_for_status()
        agents = response.json().get('results', [])

        down_agents = [agent for agent in agents if agent.get('state') != 'ACTIVE']
        return "Healthy" if not down_agents else "Unhealthy"

    except Exception as e:
        logging.error(f"Error checking agent health for group {group_id}: {e}")
        return "Unknown"

def write_batches_to_csv(groups, batch_size):
    total = len(groups)
    for i in range(0, total, batch_size):
        batch = groups[i:i + batch_size]
        filename = os.path.join(OUTPUT_DIR, f"group_batch_{(i // batch_size) + 1}.csv")

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['groupId', 'groupName', 'agentHealth'])

            for group in batch:
                health = check_agent_health(group['id'])
                writer.writerow([group['id'], group['name'], health])

        logging.info(f"Wrote {len(batch)} groups to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Generate group ID batches with health info.")
    parser.add_argument('--batch_size', type=int, default=25, help="Number of group IDs per file")
    args = parser.parse_args()

    try:
        groups = get_groups()
        write_batches_to_csv(groups, args.batch_size)
        logging.info("Batch generation completed successfully.")
    except Exception as e:
        logging.critical(f"Error during batch generation: {e}")

if __name__ == "__main__":
    main()
