# MongoDB-Patch-Automation-HealthCheck

💾 Files Overview
File Name	Purpose

opsmanager_backup.py	Backs up all Ops Manager groups before upgrade.
opsmanager_batch_generator.py	Splits groups into batch CSVs with health checks.
opsmanager_batch_upgrade.py	Upgrades MongoDB only for healthy groups.
opsmanager_batch_rollback.py	Rolls back groups using the original backup.


🛠️ Steps to Run
1️⃣ Take a Backup of Ops Manager Groups

python opsmanager_backup.py

📌 This will create: opsmanager_backup.json

2️⃣ Generate Batch Files with Health Checks

python opsmanager_batch_generator.py --batch-size 25

📌 This will create multiple batch files:

batch_1.csv

batch_2.csv

batch_3.csv

Each file will contain groupId and health status.

3️⃣ Upgrade MongoDB for Groups in a Batch

python opsmanager_batch_upgrade.py --batch-file batch_1.csv --version 7.0.16-ent

📌 This will:

Upgrade MongoDB only for Healthy groups.

Increment Ops Manager version automatically.

Skip unhealthy groups and log them.

Logs:

Successful upgrades → upgrade_success.log

Errors → upgrade_error.log

4️⃣ Rollback Using the Backup

python opsmanager_batch_rollback.py --batch-file batch_1.csv

📌 This will:

Restore the groups in batch_1.csv to their original state using the backup.

Logs:

Successful rollbacks → rollback_success.log

Errors → rollback_error.log
