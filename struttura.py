from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from pathlib import Path

engine = create_engine(f'sqlite:///{str((Path(__file__).parent / "meta.db").absolute())}', echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class File(Base):
    """
    Struttura della tabella File.
    Rappresenta i file analizzati.
    """

    __tablename__ = 'File'

    identificativo = Column(Integer, primary_key=True, autoincrement=True)
    percorso = Column(String, nullable=False)


class Dichiarazione(Base):
    """
    Struttura della tabella Dichiarazione.
    Rappresenta le dichiarazioni presenti in un file e i loro tipi.
    """

    __tablename__ = 'Dichiarazioni'

    identificativo = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String, nullable=False)
    file = Column(Integer, ForeignKey('File.identificativo'), nullable=False)


class Elemento(Base):
    """
    Struttura della tabella Elemento.
    Rappresenta gli elementi non banali (es spazi, ecc..) che costituiscono una dichiarazione.
    """

    __tablename__ = 'Elementi'

    identificativo = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String, nullable=False)
    valore = Column(String, nullable=False)
    # linea = Column(Integer, nullable=False)
    dichiarazione = Column(Integer, ForeignKey('Dichiarazioni.identificativo'), nullable=False)


def struttura() -> None:
    """
    Genera la struttura della base di dati se necessario.

    :return: None.
    :rtype: None.
    """
    Base.metadata.create_all(engine)