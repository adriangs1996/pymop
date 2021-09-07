from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import JSON, String
from src.db.config import Entity

class Scan(Entity):
    target = Column(String(300))
    config = Column(JSON)
    reports = Column(JSON)
    vectors = Column(JSON)