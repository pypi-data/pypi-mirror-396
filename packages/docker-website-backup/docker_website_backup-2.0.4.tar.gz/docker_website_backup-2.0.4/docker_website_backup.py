#!/usr/bin/env python3

import os
import shlex
import subprocess
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path
from tempfile import TemporaryDirectory

from contextlib import contextmanager
from textwrap import dedent
from typing import List, Union

# `--log-driver=none` will prevent Docker from saving streamed data in logs,
# otherwise the storage on the remote disk fills up really fast.
DISABLE_DOCKER_LOGGING = '--log-driver=none'
ALPINE_IMAGE = 'alpine:3.22.1'
RSYNC_IMAGE_NAME = 'rsync-image'
POSTGRES_IMAGE = 'postgres:18.0-alpine'
CWD = Path.cwd()
PROJECT_DEFAULT = CWD.name
RSYNC_ARGS = [
    '--archive',
    '--compress',
    '--xattrs',
    '--delete',
    '--progress',
    '--no-motd',
]


def print_line(character: str):
    try:
        print(character * os.get_terminal_size()[0])
    except OSError:  # Not in a terminal
        print(character * 80)


class BackupRestoreRunner:
    def __init__(self, args: Namespace):
        self.args = args

        self.no_input = args.no_input
        self.rsync_base_image = args.rsync_base_image
        self.rsync_image = args.rsync_image
        self.backup_dir = args.backup_dir
        self.backup_media_dir: Path = self.backup_dir / 'media'
        self.backup_media_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dump = self.backup_dir / 'db.dump'
        self.db_only = args.db_only
        self.media_only = args.media_only
        self.db_image = args.db_image
        self.db_socket_volume = args.db_socket_volume
        self.db_user = args.db_user
        self.db_name = args.db_name
        self.media_volume = args.media_volume
        self.media_user = args.media_user
        self.uid = args.uid
        self.gid = args.gid

        self.rsync_dockerfile = dedent(f"""
            FROM {self.rsync_base_image}
            RUN apk add rsync
            RUN adduser -u {self.uid} -g {self.gid} --disabled-password --gecos "" --no-create-home {self.media_user}
            USER {self.media_user}
        """)

    def run_local(self, args: Union[List[str], str], **kwargs):
        print_line('=')
        prefix = ' '.join(
            [
                f'{k}={shlex.quote(v)}'
                for k, v in kwargs.get('env', {}).items()
                if os.environ.get(k) != v
            ]
        )
        command = (
            ' '.join([shlex.quote(str(arg)) for arg in args])
            if isinstance(args, list)
            else args
        )
        print(f'{prefix} {command}' if prefix else command)
        if not self.no_input and input('Run the above command? [yN] ').lower() != 'y':
            sys.exit(1)
        print_line('-')
        subprocess.run(args, check=True, **kwargs)
        print_line('=')
        print()

    def run_remote_docker(self, *args, **kwargs):
        ssh_address = self.args.ssh_address
        env = {**os.environ}
        if ssh_address:
            env['DOCKER_HOST'] = f'ssh://{ssh_address}'
        self.run_local(*args, **kwargs, env=env)

    @contextmanager
    def tmp_rsync_dockerfile(self):
        with TemporaryDirectory() as tmp:
            with open(Path(tmp) / 'Dockerfile', 'w') as f:
                f.write(self.rsync_dockerfile)
            yield tmp

    def build_local_rsync_image(self):
        with self.tmp_rsync_dockerfile() as tmp:
            self.run_local(
                ['docker', 'build', '-t', self.rsync_image, tmp],
                stdin=subprocess.DEVNULL,
            )

    def build_remote_rsync_image(self):
        with self.tmp_rsync_dockerfile() as tmp:
            self.run_remote_docker(
                ['docker', 'build', '-t', self.rsync_image, tmp],
                stdin=subprocess.DEVNULL,
            )

    def dump_postgresql(self):
        self.run_remote_docker(
            f'docker run --read-only --rm -i {DISABLE_DOCKER_LOGGING} '
            f'-v {self.db_socket_volume}:/var/run/postgresql '
            f'{self.db_image} pg_dump -U {self.db_user} '
            f'-Fc -b -v {self.db_name} '
            f'> {self.backup_dump}',
            shell=True,
        )

    def rsync_media_volume_to_backup(self):
        ssh_address = self.args.ssh_address

        if not ssh_address:
            self.rsync_backup_to_media_volume(reverse=True)
            return

        self.build_remote_rsync_image()
        self.run_local(
            [
                'rsync',
                '--rsync-path',
                f'docker run --read-only -v {self.media_volume}:/data:ro --rm -i {DISABLE_DOCKER_LOGGING} '
                f'{self.rsync_image} rsync',
                *RSYNC_ARGS,
                f'{ssh_address}:/data/',
                self.backup_media_dir,
            ],
        )

    def execute_backup(self):
        print(f'Backing up data into {self.backup_dir!r}…')
        self.run_local(['mkdir', '-p', self.backup_dir])

        if not self.media_only:
            self.dump_postgresql()

        if not self.db_only:
            self.rsync_media_volume_to_backup()

    def restore_postgresql(self):
        socket_mount = f'{self.db_socket_volume}:/var/run/postgresql'
        self.run_local(
            [
                'docker',
                'run',
                '--read-only',
                f'-v={socket_mount}',
                '--rm',
                '-i',
                DISABLE_DOCKER_LOGGING,
                self.db_image,
                'psql',
                '-U',
                f'{self.db_user}',
                '-d',
                f'{self.db_name}',
                '-c',
                dedent(f"""
                    DROP SCHEMA public CASCADE;
                    CREATE SCHEMA public;
                    GRANT ALL ON SCHEMA public TO {self.db_user}, public;
                """),
            ]
        )
        self.run_local(
            f'docker run --read-only -v {socket_mount} --rm -i {DISABLE_DOCKER_LOGGING} '
            f'{self.db_image} '
            f'pg_restore -U {self.db_user} -d {self.db_name} --if-exists --clean --exit-on-error -Fc '
            f'< {self.backup_dump}',
            shell=True,
        )

    def rsync_backup_to_media_volume(self, reverse: bool = False):
        from_path = '/backup/'
        to_path = '/data/'
        backup_flags = ':ro'
        data_flags = ''
        if reverse:
            from_path, to_path = to_path, from_path
            backup_flags, data_flags = data_flags, backup_flags

        self.build_local_rsync_image()
        self.run_local(
            [
                'docker',
                'run',
                f'-v={self.backup_media_dir}:/backup{backup_flags}',
                f'-v={self.media_volume}:/data{data_flags}',
                '--rm',
                DISABLE_DOCKER_LOGGING,
                self.rsync_image,
                'rsync',
                f'--chown={self.media_user}:{self.media_user}',
                '--chmod=775',
                *RSYNC_ARGS,
                from_path,
                to_path,
            ]
        )

    def execute_restore(self):
        print(f'Restoring data from {self.backup_dir!r}')
        if not self.media_only:
            self.restore_postgresql()

        if not self.db_only:
            self.rsync_backup_to_media_volume()

    def execute(self):
        if self.args.action in {'clone', 'backup'}:
            self.execute_backup()
        if self.args.action in {'clone', 'restore'}:
            self.execute_restore()


def main():
    local_backup_root_dir = (CWD / 'backup').resolve()

    project_parser = ArgumentParser(add_help=False)
    project_parser.add_argument('--project', default=PROJECT_DEFAULT)
    project = project_parser.parse_known_args()[0].project

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(dest='action', required=True)
    clone_parser = subparsers.add_parser(
        'clone', formatter_class=ArgumentDefaultsHelpFormatter
    )
    backup_parser = subparsers.add_parser(
        'backup', formatter_class=ArgumentDefaultsHelpFormatter
    )
    restore_parser = subparsers.add_parser(
        'restore', formatter_class=ArgumentDefaultsHelpFormatter
    )

    for subparser in [clone_parser, backup_parser, restore_parser]:
        subparser.add_argument(
            '--project', default=PROJECT_DEFAULT, help='Docker Compose project name.'
        )
        subparser.add_argument(
            '--no-input', action='store_true', help='Say yes to all questions.'
        )
        subparser.add_argument(
            '--backup-dir',
            type=Path,
            default=local_backup_root_dir,
            help='Where the backup will be stored, on the machine running this script.',
        )
        subparser.add_argument(
            '--rsync-base-image',
            default=ALPINE_IMAGE,
            help='Base Docker image used for building the rsync image.',
        )
        subparser.add_argument(
            '--rsync-image',
            default=RSYNC_IMAGE_NAME,
            help='Name of the built Docker image for rsync.',
        )
        group = subparser.add_mutually_exclusive_group()
        group.add_argument(
            '--db-only', action='store_true', help='Apply only to the database.'
        )
        group.add_argument(
            '--media-only', action='store_true', help='Apply only to the media.'
        )
        subparser.add_argument(
            '--db-image',
            default=POSTGRES_IMAGE,
            help='Name of the PostgreSQL Docker image.',
        )
        subparser.add_argument(
            '--db-socket-volume',
            default=f'{project}_postgresql-socket',
            help='Name of the Docker volume containing the PostgreSQL UNIX socket.',
        )
        subparser.add_argument(
            '--db-user', default=project, help='PostgreSQL user name.'
        )
        subparser.add_argument(
            '--db-name', default=project, help='PostgreSQL database name.'
        )
        subparser.add_argument(
            '--media-volume',
            default=f'{project}_media',
            help='Docker volume name containing all the uploaded files of the website.',
        )
        subparser.add_argument(
            '--media-user', default='django', help='Docker user of the media volume.'
        )
        subparser.add_argument(
            '--uid',
            default=os.getuid(),
            help='Linux user ID used when copying data in Docker.',
        )
        subparser.add_argument(
            '--gid',
            default=os.getgid(),
            help='Linux group ID used when copying data in Docker.',
        )

    for subparser in [clone_parser, backup_parser]:
        optional_ssh_help = (
            ' Leave empty to use the local Docker instance.'
            if subparser == backup_parser
            else ''
        )
        subparser.add_argument(
            'ssh_address',
            nargs='?' if subparser == backup_parser else None,
            help=(
                f'Remote Docker host SSH address from which the data should be backed up, '
                f'in the `username@host` or `host` form.{optional_ssh_help}'
            ),
        )

    BackupRestoreRunner(args=parser.parse_args()).execute()


if __name__ == '__main__':
    main()
