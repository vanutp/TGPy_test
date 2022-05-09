import getpass
import importlib.metadata
import os
import re
import shlex
import socket
from contextlib import contextmanager
from pathlib import Path
from subprocess import PIPE, Popen

import appdirs

from tgpy import version

ENV_TGPY_DATA = os.getenv('TGPY_DATA')
if ENV_TGPY_DATA:
    DATA_DIR = Path(os.getenv('TGPY_DATA'))
else:
    # noinspection PyTypeChecker
    DATA_DIR = Path(appdirs.user_config_dir('tgpy', appauthor=False))
MODULES_DIR = DATA_DIR / 'modules'
WORKDIR = DATA_DIR / 'workdir'
CONFIG_FILENAME = DATA_DIR / 'config.yml'
SESSION_FILENAME = DATA_DIR / 'TGPy.session'
REPO_ROOT = Path(__file__).parent.parent
if not os.path.exists(REPO_ROOT / '.git'):
    REPO_ROOT = None

filename_prefix = 'tgpy://'


@contextmanager
def execute_in_repo_root():
    if not REPO_ROOT:
        raise ValueError('No repository found')
    old_cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def create_config_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    MODULES_DIR.mkdir(exist_ok=True)
    WORKDIR.mkdir(exist_ok=True)


class RunCmdException(Exception):
    def __init__(self, process: Popen):
        self.process = process

    def __str__(self):
        return f'Command {shlex.join(self.process.args)} exited with code {self.process.returncode}'


def run_cmd(args: list[str]):
    proc = Popen(args, stdout=PIPE)
    output, _ = proc.communicate()
    if proc.returncode:
        raise RunCmdException(proc)
    return output.decode('utf-8').strip()


def installed_as_package():
    try:
        importlib.metadata.version('tgpy')
        return True
    except importlib.metadata.PackageNotFoundError:
        return False


def running_in_docker():
    return os.path.exists('/.dockerenv')


def get_user():
    try:
        return getpass.getuser()
    except KeyError:
        return str(os.getuid())


DOCKER_DEFAULT_HOSTNAME_RGX = re.compile(r'[0-9a-f]{12}')


def get_hostname():
    real_hostname = socket.gethostname()
    if running_in_docker() and DOCKER_DEFAULT_HOSTNAME_RGX.fullmatch(real_hostname):
        return 'docker'
    return real_hostname


def get_version():
    if not version.IS_DEV_BUILD:
        return version.__version__

    if REPO_ROOT:
        with execute_in_repo_root():
            try:
                return 'git@' + run_cmd(['git', 'rev-parse', '--short', 'HEAD'])
            except (RunCmdException, FileNotFoundError):
                pass

    if version.COMMIT_HASH:
        return 'git@' + version.COMMIT_HASH[:7]

    return 'unknown'


__all__ = [
    'DATA_DIR',
    'MODULES_DIR',
    'WORKDIR',
    'CONFIG_FILENAME',
    'SESSION_FILENAME',
    'REPO_ROOT',
    'run_cmd',
    'get_version',
    'create_config_dirs',
    'installed_as_package',
    'RunCmdException',
    'filename_prefix',
    'execute_in_repo_root',
    'get_user',
    'get_hostname',
    'running_in_docker',
]
