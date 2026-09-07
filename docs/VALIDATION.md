# Validation

## Completed

- Read-only retrieval of active runtime/helper/config/unit files from both installed roles.
- All 20 original-derived files match byte-for-byte after deterministic literal anonymization. Sanitized hashes are recorded in SOURCE-PARITY.json.
- 16 isolated regression tests pass, including Bash syntax, parity hashes, the command surface, status/snapshots aliases, 5% verification arguments, init confirmation flag, positional restore behavior, local rsync exit handling, preserved strict remote behavior, cache defaults, original HTML mail format/escaping, email policy and pipeline structure.
- The original interactive restore host menu and cancellation were exercised using a pseudo-terminal. No restore was performed.
- Original usage/report/email functions generated the synthetic examples; four PNG previews were rendered in Chromium and visually inspected.
- The curated package passed the source-identity scan and archive/manifest checks.

## Limits

Command tests use local doubles for Restic, storage, systemd and sendmail; they are not full backup/restore integration tests. The original runtime was not installed or executed against live data during packaging. Neither server was modified. New Linux installation, end-to-end remote transfer, database import, mail delivery and complete recovery drills remain required before another operator deploys these anonymized examples.

The GitHub workflow runs the isolated tests, checks example regeneration and verifies the distribution manifest. It does not claim to validate an actual production backup.
