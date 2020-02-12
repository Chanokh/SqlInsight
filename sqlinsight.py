# codifica: utf-8

"""
Analizza ed eventualmente estra dati dai file sorgente SQL di una data cartella.
"""

from elapsed import TimeIt
from argparse import ArgumentParser, Namespace
from typing import Any, List, Callable, Sequence, Optional as Opt
from pathlib import Path
from sys import argv, stderr
from sqlparse import parse as parse_sql
from sqlparse.sql import Statement
from sqlparse.tokens import *
from io import StringIO
from os import walk
from struttura import Session, File, Elemento, Dichiarazione

versione_principale = 1
versione_secondaria = 0
tipo_versione = 0


def autore() -> str:
    """
    Ottiene la stringa che definisce l'autore.

    :return: Vedi la descrizione.
    :rtype str.
    """
    return '(c) 2020 Giovanni Lombardo mailto://g.lombardo@protonmail.com'


def versione() -> str:
    """
    Compone ed ottiene la stringa di versione.

    :return: Vedi la descrizione.
    :rtype: str.
    """
    return f'{versione_principale}.{versione_secondaria}.{tipo_versione}'


def guida(argomenti: List[Any]) -> Namespace:
    """
    Interpreta la riga di comando.

    :param argomenti:    Gli argomenti forniti da linea di comando come ricevuti da sys.argv.
    :type argomenti:     List[str].

    :return: La struttura Namespace contenente gli argomenti forniti da linea di comando.
    :rtype: Namespace
    """
    aiuto = dict(
        posizione='La cartella in cui sono memorizzati i file SQL.',
        modello='Il modello dei dati da ricercare.',
        codifica='La codifica da utilizzare nella lettura dei file SQL.',
    )

    analizzatore = ArgumentParser(description=__doc__)
    analizzatore.add_argument('posizione', help=aiuto['posizione'])
    analizzatore.add_argument('modello', help=aiuto['modello'])
    analizzatore.add_argument('-c', '--codifica', dest='codifica', default='utf-8', help=aiuto['codifica'])

    argomenti = analizzatore.parse_args(argomenti)

    percorso = Path(argomenti.posizione)

    if not percorso.exists():
        stderr.write(f'L\'argomento `posizione` deve essere una cartella esistente.')
        exit(1)

    if not percorso.is_dir():
        stderr.write(f'L\'argomento `posizione` deve essere una cartella.')
        exit(2)

    argomenti.posizione = percorso
    return argomenti


def analizza(sessione: Session, elemento: File, codifica: str) -> None:
    """
    Analizza l'elemento dato utilizzando la codifica richiesta.

    :param sessione:    L'oggetto sessione.
    :type sessione:     Session.

    :param elemento:    L'oggetto file da analizzare.
    :type elemento:     File.

    :param codifica:    La codifica da usare per leggere il file SQL.
    :type codifica:     str.

    :return: Restituisce gli elementi trovati che rispettano il modello dato.
    :rtype: str.
    """
    try:
        with open(elemento.percorso, 'r', encoding=codifica, errors='ignore') as d:
            contenuto = d.read()

        # La variable dati_strutturati è una TokenList di oggetti di tipo Statement
        dati_strutturati = parse_sql(contenuto, encoding=codifica)

        # Iterando su ciascun elemento dei dati strutturati si ottengono istanze di sotto
        # classi di Token. Tutti i token possibili sono definiti in sqlparse.tokens. La
        # classe base Token utilizza la tecnica della sovrascrittura di __getattr__ per
        # creare nuovi membri e in definitiva nuovi token. Il token è una unità sintattica.
        for dichiarazione in dati_strutturati:

            try:
                oggetto_dichiarazione = Dichiarazione(
                    tipo=dichiarazione.get_name(),
                    file=elemento.identificativo
                )

                sessione.add(oggetto_dichiarazione)
                sessione.commit()

                for unita_sintattica in dichiarazione.tokens:
                    if unita_sintattica.is_whitespace:
                        continue
                    unita = Elemento(
                        tipo=str(unita_sintattica.ttype),
                        valore=unita_sintattica.value,
                        dichiarazione=oggetto_dichiarazione.identificativo
                    )

                    sessione.add(unita)
                    sessione.commit()

            except Exception as e:
                print(str(e))
                sessione.rollback()

    except (IOError, OSError, Exception) as e:
        stderr.write(f'Error reading `{elemento.percorso}`: {str(e)}')


def inizio(argomenti: Namespace) -> int:
    """
    La procedura eseguita all'avvio del modulo.

    :param argomenti:   Gli argomenti da linea di comando come ottenuti da guida().
    :type argomenti:    Namespace.

    :return: Restituisce 0.
    :rtype: int.
    """
    sessione = Session()
    for radice, cartelle, files in walk(str(argomenti.posizione.absolute())):
        for f in files:
            if f.endswith('.sql'):
                percorso = Path(radice) / f
                nome_completo = str(percorso.absolute())
                print(f'Analizzando: {nome_completo}')
                file_corrente = File(percorso=nome_completo)
                sessione.add(file_corrente)
                sessione.commit()
                analizza(
                    sessione,
                    file_corrente,
                    argomenti.codifica
                )

    sessione.commit()
    return 0


if __name__ == '__main__':
    print(autore())
    print(f'{str(Path(argv[0]).parts[-1])} version {versione()}')
    trascorsi = TimeIt(lambda: inizio(guida(argv[1:])), logger_name=__name__)
    exit(tuple(trascorsi.return_values().values())[-1])