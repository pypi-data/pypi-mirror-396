"""Classes for interaction with databases."""

import urllib.parse
import configparser
import os
import pwd
from functools import cached_property
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from _io import TextIOWrapper
from sqlalchemy import MetaData, Engine, create_engine

if TYPE_CHECKING:  # pragma: no cover
    from cyberfusion.DatabaseSupport import DatabaseSupport

import subprocess

from sqlalchemy.sql import text
from sqlalchemy_utils import create_database, database_exists, drop_database

from cyberfusion.Common import get_md5_hash, get_tmp_file, try_find_executable
from cyberfusion.DatabaseSupport.exceptions import ServerNotSupportedError
from cyberfusion.DatabaseSupport.queries import Query
from cyberfusion.DatabaseSupport.tables import Table
from cyberfusion.DatabaseSupport.utilities import (
    _generate_mariadb_dsn,
    get_host_is_socket,
    object_exists,
    object_not_exists,
)


class Database:
    """Abstract representation of database."""

    MYSQLDUMP_BIN = try_find_executable("mysqldump")
    MYSQL_BIN = try_find_executable("mysql")

    PATH_DUMP = os.path.join(os.path.sep, "tmp", "database-support-dumps")

    def __init__(
        self,
        *,
        support: "DatabaseSupport",
        name: str,
        server_software_name: str,
    ) -> None:
        """Set attributes and call functions to handle database."""
        self.support = support
        self.name = name
        self.server_software_name = server_software_name

    @property
    def _mariadb_url(self) -> str:
        """Get database engine URL for MariaDB."""
        return _generate_mariadb_dsn(
            username=self.support.mariadb_server_username,
            host=self.support.mariadb_server_host,
            password=self.support.server_password,
            database_name=self.name,
        )

    @property
    def _postgresql_url(self) -> str:
        """Get database engine URL for PostgreSQL."""
        url = self.server_engine.url.render_as_string(hide_password=False)

        return (
            url.rsplit("/", 1)[  # PostgreSQL URL already contains database name
                0
            ]
            + "/"
            + self.name
        )

    @property
    def url(self) -> str:
        """Get database engine URL."""
        if self.server_software_name == self.support.MARIADB_SERVER_SOFTWARE_NAME:
            return self._mariadb_url

        return self._postgresql_url

    @property
    def exists(self) -> bool:
        """Get database exists locally."""
        return database_exists(self.url)

    @property
    def _mysql_credentials_config_file(self) -> str:
        """Create and set path to file with MySQL credentials config."""
        config = configparser.ConfigParser()

        config["client"] = {}

        if get_host_is_socket(self.support.mariadb_server_host):
            config["client"]["socket"] = self.support.mariadb_server_host
        else:
            url = urllib.parse.urlsplit("//" + self.support.mariadb_server_host)

            config["client"]["host"] = url.hostname

            if url.port:
                config["client"]["port"] = str(url.port)

        config["client"]["user"] = self.support.mariadb_server_username

        if self.support.server_password:
            config["client"]["password"] = self.support.server_password

        path = get_tmp_file()

        with open(path, "w") as f:
            config.write(f)

        return path

    def export(
        self,
        *,
        chown_username: Optional[str] = None,
        exclude_tables: Optional[List[Table]] = None,
        root_directory: str = PATH_DUMP,
    ) -> Tuple[str, str]:
        """Export database.

        Does not load dump into variable (due to possibly large size), but returns
        dump file path.

        The dump is created with the --opt parameter, which includes --add-drop-table.
        Therefore, if the dump is imported into the original database, data in
        existing tables is overwritten.

        The dump is written to a file inside root_directory. The default path
        is are automatically cleaned up using systemd-tmpfiles, if this library
        is installed as a Debian package.
        """
        if self.server_software_name != self.support.MARIADB_SERVER_SOFTWARE_NAME:
            raise ServerNotSupportedError

        # Construct command

        _command = [self.MYSQLDUMP_BIN]
        _command.append(f"--defaults-extra-file={self._mysql_credentials_config_file}")
        _command.extend(["--opt", "--single-transaction", "-a", self.name])

        # Ignore excluded tables

        if exclude_tables:
            for exclude_table in exclude_tables:
                _command.append(
                    f"--ignore-table={exclude_table._table_name_with_schema_name}"
                )

        # Export database

        _stdout_file = get_tmp_file()

        with open(_stdout_file, "w") as f:
            subprocess.run(_command, check=True, stdout=f)

        # Add database name and file extension to name

        stdout_file = os.path.join(
            root_directory,
            self.name
            + "-"
            + os.path.basename(_stdout_file)
            + "."
            + self.support.EXTENSION_FILE_SQL,
        )

        os.rename(_stdout_file, stdout_file)

        # Set permissions of file

        if chown_username:
            passwd = pwd.getpwnam(chown_username)

            os.chown(stdout_file, passwd.pw_uid, passwd.pw_gid)

        return stdout_file, get_md5_hash(stdout_file)

    def load(self, dump_file: TextIOWrapper) -> None:
        """Load (import) database."""
        if self.server_software_name != self.support.MARIADB_SERVER_SOFTWARE_NAME:
            raise ServerNotSupportedError

        _command = [self.MYSQL_BIN]
        _command.append(f"--defaults-extra-file={self._mysql_credentials_config_file}")
        _command.append(self.name)

        subprocess.run(
            _command,
            check=True,
            stdin=dump_file,
        )

    @object_not_exists
    def create(self) -> bool:
        """Create database.

        Note that for PostgreSQL, this does not create a schema.
        """
        create_database(self.url)

        return True

    @object_exists
    def drop(self) -> bool:
        """Drop database."""
        drop_database(self.url)

        return True

    @cached_property
    def server_engine(self) -> Engine:
        if self.server_software_name == self.support.MARIADB_SERVER_SOFTWARE_NAME:
            return self.support.engines.engines[self.support.engines.MYSQL_ENGINE_NAME]

        return self.support.engines.engines[self.support.engines.POSTGRESQL_ENGINE_NAME]

    @cached_property
    def database_engine(self) -> Engine:
        return create_engine(self.url)

    @property
    def _mariadb_size(self) -> int:
        """Get size for MariaDB."""

        # Set data length

        data_length = 0
        data_length_query = text(
            "SELECT data_length FROM information_schema.tables WHERE TABLE_SCHEMA=:name;"
        ).bindparams(name=self.name)

        for result in Query(
            engine=self.server_engine,
            query=data_length_query,
        ).result:
            if result[0] is None:  # None when e.g. view
                continue

            data_length += result[0]

        # Set index length

        index_length = 0
        index_length_query = text(
            "SELECT index_length FROM information_schema.tables WHERE TABLE_SCHEMA=:name;"
        ).bindparams(name=self.name)

        for result in Query(
            engine=self.server_engine,
            query=index_length_query,
        ).result:
            if result[0] is None:  # None when e.g. view
                continue

            index_length += result[0]

        # Set size (data length + index length)

        return data_length + index_length

    @property
    def _postgresql_size(self) -> int:
        """Get size for PostgreSQL."""

        # Get database size

        database_size = 0
        database_size_query = text("SELECT pg_database_size(:name);").bindparams(
            name=self.name
        )

        for result in Query(
            engine=self.server_engine,
            query=database_size_query,
        ).result:
            database_size += result[0]

        return database_size

    @property
    def size(self) -> int:
        """Get size."""
        if self.server_software_name == self.support.MARIADB_SERVER_SOFTWARE_NAME:
            return self._mariadb_size

        return self._postgresql_size

    @property
    def metadata(self) -> MetaData:
        """Get metadata with SQLAlchemy."""
        metadata_obj = MetaData(schema=self.name)

        metadata_obj.reflect(bind=self.database_engine)

        return metadata_obj

    @property
    def tables(self) -> List[Table]:
        """Get tables."""
        tables: List[Table] = []

        for _, sat in self.metadata.tables.items():
            tables.append(Table(database=self, name=sat.name))

        return tables

    def compare(
        self, *, right_database: "Database"
    ) -> Tuple[Dict[str, bool], List[str], List[str]]:
        """Compare database to another database.

        Reports the following:

        * Tables that are present in left and right by name. This is a dict. The
          value is a bool which states if the table (i.e. structure, contents, etc.)
          is identical between the left and right databases.
        * Tables that are only present in left (not in right). These tables can
          be considered added to left.
        * Tables that are only present in right (not in left). These tables can
          be considered removed from left.
        """
        if self.server_software_name != self.support.MARIADB_SERVER_SOFTWARE_NAME:
            raise ServerNotSupportedError

        present_in_left_and_right = {}
        present_in_only_left = []
        present_in_only_right = []

        # Get tables that are only present in right

        for right_table in right_database.tables:
            if any(right_table.name == left_table.name for left_table in self.tables):
                continue

            present_in_only_right.append(right_table.name)

        # Get tables that are only present in left

        for left_table in self.tables:
            if any(
                left_table.name == right_table.name
                for right_table in right_database.tables
            ):
                continue

            present_in_only_left.append(left_table.name)

        # Get tables that are present in left and right

        for right_table in right_database.tables:
            for left_table in self.tables:
                if left_table.name != right_table.name:
                    continue

                # Table is in left and right

                identical = right_table.checksum == left_table.checksum

                present_in_left_and_right[right_table.name] = identical

                break

        for left_table in self.tables:
            for right_table in right_database.tables:
                if right_table.name != left_table.name:
                    continue

                # Table is in left and right

                identical = left_table.checksum == right_table.checksum

                present_in_left_and_right[left_table.name] = identical

                break

        return (
            present_in_left_and_right,
            present_in_only_left,
            present_in_only_right,
        )
