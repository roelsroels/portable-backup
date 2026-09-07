# Package review and provenance

## Available evidence and reconstruction

The supplied conversation and an available diagnostic attachment contained the local preparation implementation, a remote preparation implementation, host configuration examples, unit excerpts, retention settings and confirmed rsync/cache/stale-lock corrections. The complete original administration script, interactive restore browser, original installer and long-form recovery manual were not available. This package reconstructs their generic responsibilities; it is not an export of all original source files or a drop-in upgrade for an existing deployment.

Python command orchestration and JSON configuration replace the partly available shell framework. This makes configuration non-executable data and provides one common cache and Restic invocation path. The remote workflow uses a locked SSH tar stream instead of a published remote directory plus later rsync/cleanup commands. The lock lasts through transfer, and source cleanup is scoped to a generated private temporary directory. Coordinator staging uses a stable per-host path under its global lock to preserve Restic path grouping. Rsync remains responsible for live source and Docker-volume copies.

## Anonymization

All personal names, usernames, hostnames, email addresses, domains, account identities, original framework/repository names, IP addresses, network topology, storage-provider names and storage paths have been omitted or replaced. Examples use server-a/server-b, reserved `.invalid` domains, role-based account names and generic Linux locations. No original-to-placeholder mapping is included, because that mapping would itself disclose the removed identities.

Original journals, report messages, shell prompts, attachment filenames, timestamps, snapshot/repository identifiers, backup sizes, hardware descriptions, service inventories, named application directories and old script backup filenames are absent. Original vendor/application-specific infrastructure lists are replaced by explicit optional generic hooks. Generic database product names remain only to explain supported export methods.

No actual credentials, keys, repository data, exports, inventories, real Git remotes, Git history or authorship metadata are included. Archive metadata uses fixed neutral file times and generic ownership. Any externally created GitHub repository ownership is separate from the downloadable content and is not embedded in its files.

## Assumptions and intentional differences

- Linux/systemd, root-managed operation, Python 3.11+, GNU tools, trusted sources and private writable staging.
- One source scope per machine; distinct coordinator host entries for separate sources.
- One Restic repository per source recommended; no provider-specific quota API or original storage layout.
- Sample retention and schedules are newly chosen neutral defaults. The 5/2/3 policy is documented as an optional configurable example.
- Database exports are explicitly enabled, with no silent skip on unavailable clients.
- Interactive restore browsing is replaced by snapshots, ls and restore commands.
- Live container/SQLite files require application-specific consistency handling.
- MIT is the proposed license for this newly assembled generic implementation; review it before public distribution.
- No production host was accessed, no existing backup configuration was changed and no archive content was uploaded as part of package preparation.

Review code, source scope, credentials, retention preview and a disposable Linux restore before production installation. See VALIDATION.md for checks actually run and remaining acceptance work.
