from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from datetime import datetime
from pathlib import Path

DB_DTV = datetime.now().strftime('%Y%m%d')
CWD = Path(__file__).parent
DB_NAME = 'metasql'
DB_EXT = '.db'

Base = declarative_base()
meta_database_name = f'{DB_NAME}_{DB_DTV}{DB_EXT}'
engine = create_engine(
    f'sqlite:///{str((CWD / meta_database_name).absolute())}',
    echo=False
)
Session = sessionmaker(bind=engine)


class File(Base):
    """
    It defines the structure of the Files table.
    Each instance is a parsed SQL file.
    """

    __tablename__ = 'Files'

    identifier = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, nullable=False)


class Statement(Base):
    """
    It defines the structure of the Statements table.
    Each instance is a SQL statement into a SQL source file.
    """

    __tablename__ = 'Statements'

    # The id of the instance.
    identifier = Column(Integer, primary_key=True, autoincrement=True)

    # The name of statement [DML names are usually table names].
    name = Column(String, nullable=False)

    # The identifier of the file containing the statement.
    file = Column(Integer, ForeignKey('Files.identifier'), nullable=False)


class Unit(Base):
    """
    It defines the structure of the Units table.
    Each instance is a Token belonging to a SQL statement in a given SQL source file.
    """

    __tablename__ = 'Units'

    # The id of the instance.
    identifier = Column(Integer, primary_key=True, autoincrement=True)

    # The kind of token the unit represents
    kind = Column(String, nullable=False)

    # The value of the unit
    value = Column(String, nullable=False)

    # The statement this unit belongs to
    statement = Column(Integer, ForeignKey('Statements.identifier'), nullable=False)


def build() -> None:
    """
    It builds the SQL metadata db.

    :return: None.
    :rtype: None.
    """
    Base.metadata.create_all(engine)



