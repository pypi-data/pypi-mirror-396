from abc import abstractmethod, ABCMeta

from sqlalchemy import text

from cyberfusion.DatabaseSupport.exceptions import ServerNotSupportedError
from cyberfusion.DatabaseSupport.queries import Query
from cyberfusion.DatabaseSupport.servers import Server
from pydantic import BaseModel


class Report(BaseModel):
    pass


class TableInnodbDataLengths(BaseModel):
    name: str
    data_length_bytes: int
    index_length_bytes: int
    total_length_bytes: int


class DatabaseInnodbDataLengths(BaseModel):
    name: str
    total_length_bytes: int
    tables_data_lengths: list[TableInnodbDataLengths]


class InnodbReport(Report):
    innodb_buffer_pool_size_bytes: int
    total_innodb_data_length_bytes: int
    databases_innodb_data_lengths: list[DatabaseInnodbDataLengths]


class ReportGeneratorInterface(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, server: Server) -> None:  # pragma: no cover
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def generate(cls, server: Server) -> Report:  # pragma: no cover
        raise NotImplementedError


class InnodbReportGenerator(ReportGeneratorInterface):
    def __init__(self, server: Server) -> None:
        self.server = server

    def get_innodb_buffer_pool_size_bytes(self) -> int:
        return int(
            Query(
                engine=self.server.support.engines.engines[
                    self.server.support.engines.MYSQL_ENGINE_NAME
                ],
                query=text("SELECT @@innodb_buffer_pool_size;"),
            ).result.first()[0]
        )

    def get_databases_innodb_data_lengths(self) -> list[DatabaseInnodbDataLengths]:
        databases_innodb_data_lengths: dict[str, list[TableInnodbDataLengths]] = {}

        for result in Query(
            engine=self.server.support.engines.engines[
                self.server.support.engines.MYSQL_ENGINE_NAME
            ],
            query=text(
                "SELECT table_schema, table_name, data_length, index_length FROM information_schema.tables WHERE engine='InnoDB';"
            ),
        ).result:
            database_name = result[0]
            table_name = result[1]
            data_length_bytes = result[2]
            index_length_bytes = result[3]

            if database_name not in databases_innodb_data_lengths:
                databases_innodb_data_lengths[database_name] = []

            databases_innodb_data_lengths[database_name].append(
                TableInnodbDataLengths(
                    name=table_name,
                    total_length_bytes=data_length_bytes + index_length_bytes,
                    data_length_bytes=data_length_bytes,
                    index_length_bytes=index_length_bytes,
                )
            )

        result = []

        for (
            database_name,
            tables_data_lengths,
        ) in databases_innodb_data_lengths.items():
            total_length_bytes = 0

            for table_data_lengths in tables_data_lengths:
                total_length_bytes += table_data_lengths.total_length_bytes

            result.append(
                DatabaseInnodbDataLengths(
                    name=database_name,
                    tables_data_lengths=tables_data_lengths,
                    total_length_bytes=total_length_bytes,
                )
            )

        return result

    @classmethod
    def generate(cls, server: Server) -> InnodbReport:
        if (
            server.support.MARIADB_SERVER_SOFTWARE_NAME
            not in server.support.server_software_names
        ):
            raise ServerNotSupportedError

        class_ = cls(server)

        innodb_buffer_pool_size_bytes = class_.get_innodb_buffer_pool_size_bytes()
        databases_innodb_data_lengths = class_.get_databases_innodb_data_lengths()

        total_innodb_data_length_bytes = 0

        for database_innodb_data_lengths in databases_innodb_data_lengths:
            total_innodb_data_length_bytes += (
                database_innodb_data_lengths.total_length_bytes
            )

        return InnodbReport(
            innodb_buffer_pool_size_bytes=innodb_buffer_pool_size_bytes,
            databases_innodb_data_lengths=databases_innodb_data_lengths,
            total_innodb_data_length_bytes=total_innodb_data_length_bytes,
        )
