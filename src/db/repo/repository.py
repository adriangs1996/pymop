from typing import Any, Dict, Optional, Type, Union
from sqlalchemy import select
from sqlalchemy.orm.session import sessionmaker

from src.db.config import Entity, config

class Repository:
    """
    Repository pattern to interact with the database backend.
    Ensure that the passed table is created on the database.
    """

    def __init__(self, table: Type[Entity]) -> None:
        self.engine = config.connect()
        self.table = table
        assert self.engine is not None
        self.session_factory = sessionmaker(self.engine)

    def get_all(self, where: Optional[Dict[str, Any]] = None):
        """
        Get all objects from the repository table, optionally responding
        to a condition.
        """
        select_statement = select(self.table)
        if where is not None:
            for key, value in where.items():
                if hasattr(self.table, key):
                    select_statement = select_statement.where(
                        getattr(self.table, key) == value
                    )
        with self.session_factory() as session:
            result_set = session.execute(select_statement).scalars()
        return result_set

    def create(self, **values):
        """
        Create a new 'Table' object with the values suplied
        as keyword arguments.
        """
        insert_statement = self.table(**values)
        with self.session_factory() as session:
            session.add(insert_statement)
            session.commit()
        return insert_statement

    def get_by_id(self, id: int):
        stmt = select(self.table).where(self.table.id == id)
        with self.session_factory() as session:
            result = session.execute(stmt).scalars().first()
        return result

    def find(self, cond: Dict[str, Any]):
        stmt = select(self.table)
        for key, value in cond.items():
            if hasattr(self.table, key):
                stmt = stmt.where(getattr(self.table, key) == value)

        with self.session_factory() as session:
            result = session.execute(stmt).scalars().first()
        return result
