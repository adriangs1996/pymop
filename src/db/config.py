from configparser import ConfigParser
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Integer
from termcolor2 import colored
from sqlalchemy import create_engine
from sqlalchemy.orm.decl_api import declarative_base, declared_attr


class DatabaseConfiguration:
    def __init__(
        self, server="localhost", database="pymop", user="postgres", password="postgres"
    ) -> None:
        self.server = server
        self.database = database
        self.user = user
        self.password = password

    def _connection_string(self):
        return "postgres+psycopg2://{0}:{1}@{2}/{3}".format(
            self.user, self.password, self.server, self.database
        )

    def connect(self):
        """
        Connect to the database
        """
        connection = None
        # Try connect to the PostgreSQL server
        print(colored("Connecting to the PostgreSQL database", "cyan"))
        try:
            connection = create_engine(self._connection_string(), echo=True, future=True)
            print(colored("PostgreSQL Database version:", "cyan"))
            ver = connection.execute("SELECT version()")
            print(ver)

        except Exception as error:
            print(colored(str(error), "red"))

        return connection

    @staticmethod
    def config(
        filename="database.ini", section="postgresql"
    ) -> "DatabaseConfiguration":
        parser = ConfigParser()
        # read config file

        try:
            parser.read(filename)
        except FileNotFoundError:
            return DatabaseConfiguration()

        # get section, default to postgresql
        if parser.has_section(section):
            params = dict(parser.items(section))
            return DatabaseConfiguration(**params)
        else:
            raise Exception(
                "Section {0} not found in the file {1}".format(section, filename)
            )

config = DatabaseConfiguration.config()

class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())

Entity = declarative_base(cls=Base)