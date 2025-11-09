from sqlalchemy import ClauseElement
from sqlalchemy.dialects import postgresql


def log_stmt(stmt: ClauseElement) -> str:
    return str(
        stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        ),
    )
