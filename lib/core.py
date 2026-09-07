"""Shared runtime for all commands; configurations are data, never shell code."""
import contextlib, fcntl, json, os, pathlib, re, subprocess, sys
CONFIG = pathlib.Path('/etc/portable-backup')
STATE = pathlib.Path('/var/lib/portable-backup')
def run(args, **kw):
    return subprocess.run([str(a) for a in args], check=True, **kw)
def load(name):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', name):
        raise ValueError('Invalid host alias')
    return json.loads((CONFIG / 'hosts' / (name + '.json')).read_text())
def env(c):
    if c.get('required_mount') and not os.path.ismount(c['required_mount']):
        raise ValueError('Required repository mount is unavailable')
    e = os.environ.copy()
    # Every Restic invocation, including report/restore, gets a cache environment.
    e['HOME'] = e.get('HOME') or '/root'
    e['XDG_CACHE_HOME'] = e.get('XDG_CACHE_HOME') or '/var/cache/portable-backup'
    pathlib.Path(e['XDG_CACHE_HOME']).mkdir(mode=0o700, parents=True, exist_ok=True)
    e['RESTIC_REPOSITORY'] = c['repository']
    e['RESTIC_PASSWORD_FILE'] = c['password_file']
    return e
def restic(c, *args, **kw):
    return run(['restic', '--retry-lock', '2m', *args], env=env(c), **kw)
def filters(name):
    return ['--host', name, '--tag', 'portable-backup']
@contextlib.contextmanager
def lock(name):
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (STATE / (name + '.lock')).open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
def live_copy(args):
    p = subprocess.run(['rsync', *args])
    if p.returncode == 24:
        print('WARNING: source files vanished during live copy; continuing', file=sys.stderr)
    elif p.returncode:
        raise subprocess.CalledProcessError(p.returncode, p.args)
def retention(c):
    policy = c.get('retention', {'daily': 7, 'weekly': 4, 'monthly': 6})
    if not policy or any(k not in ('last','daily','weekly','monthly','yearly') or type(v) is not int or v < 0 for k,v in policy.items()) or not any(policy.values()):
        raise ValueError('Retention must contain at least one positive supported count')
    return [arg for k,v in policy.items() for arg in ('--keep-' + k, str(v))]
