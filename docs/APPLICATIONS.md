# Preparation behavior

The local and remote preparation scripts are the installed scripts after literal anonymization. Both preserve filesystem hierarchy and capture system inventory, application exports and optional Docker volume data. The local script uses one-filesystem rsync copies; the remote helper does not add that flag. Configure separate mounted sources as needed and inspect actual coverage.

Local host config uses INCLUDE_PATHS, EXCLUDE_PATHS, EXTRA_PATHS and BACKUP_LEGACY_DOCKER_BACKUPS. Remote config uses BASE_PATHS, BACKUP_SITES, BACKUP_MAILDIR and an EXTRA_PATHS_FILE. Paths tied to specific applications/accounts have neutral placeholders; adjust them. Missing paths are skipped, exactly as installed.

Local MariaDB/MongoDB/Docker exports run when not disabled, tools exist and their services are active. Local PostgreSQL exports enumerate online clusters. Remote exports use explicit yes/no flags and client availability. Enabled but unavailable integrations can be skipped by these original conditions; review actual export contents rather than treating flags as proof of coverage.

Rsync exit 24 is accepted only in local live copies (filesystem and Docker volumes). Remote live copies and completed-export transfers are strict. No additional error suppression was introduced.

MariaDB logical dumps include routines/events/triggers; transactional consistency still depends on table engines and workload. PostgreSQL all-database and globals dumps are compressed separately. MongoDB's local archive export is not a point-in-time recovery system. Docker metadata can include secrets. Live volume, mail and SQLite copies need workload-specific consistency procedures. Inventory and SHA256SUMS cover exported metadata/dumps, not a complete checksum manifest of every source file.
