"""Classes for interaction with database queries."""

import sqlalchemy as sa
from sqlalchemy import TextClause
from sqlalchemy.engine import ResultProxy


class Query:
    """Abstract representation of database query."""

    def __init__(self, *, engine: sa.engine.base.Engine, query: TextClause) -> None:
        """Set attributes and call functions to handle query."""
        self.engine = engine
        self.query = query

        self._execute()

    def _execute(self) -> None:
        """Execute query."""
        with self.engine.begin() as connection:
            self._result = connection.execute(self.query)

    @property
    def result(self) -> ResultProxy:
        """Get result."""
        return self._result
