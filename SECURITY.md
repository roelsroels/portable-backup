# Security

Treat all shell configs and helpers as root-trusted code. Keep exports, staging, credentials and reports private. The remote account can read prepared backup data and invoke the named root helpers. Only trusted sources belong in this coordinator's trust domain.

The runtime's existing safeguards and limitations are preserved for source parity. Review PARITY.md and operational recovery procedures before adoption. Use isolated restore drills and independent protected copies. Never contribute live inventory, emails, raw diagnostic logs, passwords or keys.
