# Disaster recovery

Maintain an offline copy of repository locations, credentials/passwords, SSH trust records, source configuration, installation instructions and storage-provider recovery procedures. These private records belong outside this public source repository. Maintain independent offsite/immutable recovery copies; a single writable backup repository is one failure domain.

## Source loss

Provision replacement hardware/OS, restore required accounts and numeric IDs, install compatible applications, recover to a new directory, validate files and database imports, then cut services over deliberately. Review networking, mounts, firewall and secrets for the replacement system. Re-enroll its verified SSH key and schedule only after a recovery drill passes.

## Coordinator loss

Install a clean Linux coordinator and this package. Recover private configs and passwords from offline custody, reconnect storage without initializing it, and establish trusted SSH host keys. Use the original logical source aliases to browse prior snapshots. Run `pb snapshots`, repository checks and a representative restore. Re-create report delivery and timers last. Status files can be absent after rebuild; the report remains critical until a full pipeline run succeeds.

## Corruption or compromise

Preserve the suspect repository and logs. Restore from a known-good independent copy or work on a duplicate repository. Avoid pruning before diagnosis. Rotate compromised credentials and rebuild compromised hosts before restoring trusted application data. Do not assume snapshots made after compromise are trustworthy.

## Recurring drills

At least annually, rehearse both source loss and coordinator loss, including offline credential retrieval, full data checks, database imports and email delivery. Also rehearse after major application/storage changes. Keep measured recovery objectives and drill evidence in private operational documentation. No historical dates, infrastructure inventories or personal review deadlines are included here.
