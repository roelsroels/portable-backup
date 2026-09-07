# Validation record

## Completed locally

- 20 Python unit/regression tests passed.
- Bash syntax checks passed for the installer and all three database hooks.
- Python source compilation and sample JSON parsing passed.
- Package content and filenames scanned for source-specific identity/infrastructure terms, real snapshot IDs and personal paths; no matches remained.
- Archive contents use only the curated repository tree, with no raw references, logs, caches, Git metadata or private configuration.
- ZIP and tar.gz readability, file manifests and SHA-256 archive checksums verified.

Tests exercise rsync exit 24 versus other failures, cache variables across Restic operations, invalid retention and aliases, mount absence, checksum corruption/traversal, concurrent locking, failed transfer handling, missing source/report state, existing restore target rejection, pipeline ordering, strict tar/source exit handling, incomplete Restic backup handling and prune failure propagation.

## Not yet executed

The preparation environment is macOS and does not contain Restic, Linux systemd or database servers. Real Linux ACL/xattr restoration, the source-to-coordinator stream, SSH/sudo restrictions, database imports, email delivery, timers and storage quotas have not been verified here. This is a review package, not a production-tested release.

A disposable real Restic round-trip test is included as `tests/integration.py` and wired into the proposed GitHub Actions workflow. That test covers snapshot creation, retention/check and restoration of a file, mode and symlink. It has not run here or on GitHub. The remote source transport and application consistency still require the acceptance drill below even when CI passes.

## Linux acceptance checklist

1. Use disposable VMs and synthetic data; verify dependencies and run the unit and integration tests.
2. Install/configure a local source, run a full export/backup, inspect stored paths and restore bytes, symlinks, modes, ACLs, xattrs and hard links.
3. Repeat through SSH with a dedicated account. Verify the account cannot modify scripts/config or invoke arbitrary sudo commands.
4. Interrupt a test transfer, simulate unavailable storage and trigger a hook failure; confirm no success state or retention follows the failed export.
5. Run two coordinator/source jobs and confirm overlap rejection. Exercise ordinary stale-lock removal only in a disposable idle repository.
6. Test all enabled database restores and application startup in isolation.
7. Exercise stale/failed report conditions, mail delivery and systemd timer schedules, including catch-up behavior.
8. Review retention preview and confirm recovery credentials exist offline before real deployment.

HTML email checks cover multipart MIME structure, preferred HTML rendering, status variants, escaped runtime data and recipient header injection rejection. Actual mail-client rendering and delivery remain deployment acceptance checks.
