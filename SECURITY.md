# Security

Keep source configurations, hooks, credentials, staging and reports root-controlled. Never contribute runtime backup data, command output, database exports or secrets. A source helper grants read access to the configured data; its SSH credentials are sensitive. Remote sources are trusted to supply archives that are extracted as root. Use isolation for separate trust domains.

Restic repository access can permit deletion; preserve independent immutable/offline copies. Report vulnerabilities privately to the repository maintainer using the hosting platform's private security reporting when enabled. No personal contact address is embedded.
