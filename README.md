# MongoDB-Patch-Automation-HealthCheck

💾 Files Overview
File Name	Purpose
opsmanager_backup.py	Backs up all Ops Manager groups before upgrade.
opsmanager_batch_generator.py	Splits groups into batch CSVs with health checks.
opsmanager_batch_upgrade.py	Upgrades MongoDB only for healthy groups.
opsmanager_batch_rollback.py	Rolls back groups using the original backup.
