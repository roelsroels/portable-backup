# Installation and setup

## Coordinator

Install dependencies through your distribution. On a Debian-style system:

```bash
sudo apt-get update
sudo apt-get install python3 restic rsync openssh-client tar util-linux zstd
sudo bash install.sh
```

Run the installer from this unpacked repository. It installs code under `/opt/portable-backup`, private configuration under `/etc/portable-backup`, private working data under `/var/lib/portable-backup`, and cache under `/var/cache/portable-backup`. It preserves existing configuration but replaces installed scripts and shipped units. Stop timers and wait for active jobs before upgrading; retain a private copy of the previous installation for rollback. Installation neither initializes storage nor starts timers.

Copy only the sample hosts you actually need:

```bash
sudo install -m 600 config/hosts/server-a.json /etc/portable-backup/hosts/server-a.json
sudoedit /etc/portable-backup/hosts/server-a.json
sudoedit /etc/portable-backup/source.json
sudoedit /etc/portable-backup/extra-paths.txt
```

Host aliases must start with a lowercase letter and contain only lowercase letters, digits and hyphens (maximum 48 characters). They identify snapshots, status and systemd instances. Each source uses one source.json. To back up a different scope from the same machine, merge the desired paths into that scope; multiple independently configured source profiles are not implemented.

For local storage, mount the actual backup volume at your chosen location and adjust `repository` and `required_mount`. Keep `required_mount` enabled to prevent writing backups to the underlying root disk when the volume is absent. Add a systemd drop-in with `RequiresMountsFor=/mnt/backup-storage` under `[Unit]` if appropriate. The example path is a placeholder, not a storage recommendation.

Create a strong random repository password without placing it in shell history:

```bash
sudo sh -c 'umask 077; head -c 48 /dev/urandom | base64 > /etc/portable-backup/secrets/server-a.password'
sudo /opt/portable-backup/bin/pb init server-a
sudo /opt/portable-backup/bin/pb run server-a
sudo /opt/portable-backup/bin/pb snapshots server-a
```

`init` is explicit and only for a NEW repository. Do not regenerate a password for an existing repository. Save passwords, backend credentials and recovery instructions offline. Restic encryption cannot compensate for losing the password.

## Remote source

Install the same package and dependencies on the source, configure `/etc/portable-backup/source.json` there, and leave its coordinator timers disabled. No Restic repository credentials need to be stored on a remote source.

Create a dedicated SSH account using local account-management procedures. Install the coordinator's public key and verify the source's SSH host key through a trusted channel. Use `config/ssh-config.example` as a starting point in root's SSH configuration on the coordinator; private keys must be mode 600. Do not disable host-key verification. Restrict the key with `restrict` in authorized_keys; network address restrictions can be added by the operator.

On the source, install the **exact command** from `config/sudoers.example` with `visudo -f /etc/sudoers.d/portable-backup` and validate with `visudo -cf /etc/sudoers.d/portable-backup`. Scripts, hooks and `/etc/portable-backup` must stay root-owned and not writable by the SSH account. Do not grant arbitrary sudo, arbitrary rsync, a shell, or writable root hooks.

The helper prepares and streams one private export under a source lock and removes the temporary export when the stream ends. A failed transfer never creates a new snapshot. The SSH account can read all selected data through this helper: possession of its private key grants that access. Source systems are trusted: the coordinator extracts their archive as root to preserve metadata. Do not enroll an untrusted source; use isolated collectors for different trust domains.

On the coordinator:

```bash
sudo install -m 600 config/hosts/server-b.json /etc/portable-backup/hosts/server-b.json
sudoedit /etc/portable-backup/hosts/server-b.json
sudo /opt/portable-backup/bin/pb init server-b
sudo /opt/portable-backup/bin/pb run server-b
```

First create server-b's separate password file as above. Configure the `backup-storage` SSH alias and storage permissions for the SFTP example. For another Restic backend, change `repository` and supply that backend's credentials in a root-only environment file or service environment. Ensure manual and scheduled commands receive identical backend credentials. Do not commit them.

## Schedule and reporting

After a successful restore drill:

```bash
sudo systemctl enable --now portable-backup@server-a.timer
sudo systemctl enable --now portable-backup-report.timer
sudo systemctl list-timers --all
```

Stagger different host instances with `systemctl edit portable-backup@server-b.timer`:

```ini
[Timer]
OnCalendar=
OnCalendar=*-*-* 04:00:00
```

Then enable that timer. The coordinator serializes operations and rejects overlaps rather than queues them, so leave enough time for exports, transfer and pruning. Timers use the system's local timezone and persistent catch-up; simultaneous catch-up runs may need a manual retry. Reports should run after backups finish. Test mail delivery by configuring `email_to` in report.json and running `pb report --email`.

## Remove a source / uninstall

Disable and stop its timer, wait for its running service to finish, then remove its host configuration from the coordinator. Revoke the dedicated source SSH key and sudoers entry when no longer needed. This does not delete snapshots. Uninstall by stopping all framework timers/services and removing installed units and `/opt/portable-backup`; preserve credentials and repositories until recovery is no longer required. Never treat uninstall as permission to delete backup storage.
