"""
It parses and extract insightful metadata about SQL source files allowing
them to be retrieved by from a new metadata database through SQL queries.
"""

from elapsed import TimeIt
from argparse import ArgumentParser, Namespace
from typing import Any, List, Callable, Sequence, Optional as Opt
from pathlib import Path
from sys import argv, stderr
from sqlparse import parse as parse_sql
from sqlparse.tokens import *
from os import walk
from sqlinsight_data import build, Session, File, Unit, Statement
from logging import getLogger, INFO, DEBUG

version_major = 1
version_minor = 0
version_kind = 0


def author() -> str:
    """
    It gets the authors string.

    :return: See description.
    :rtype str.
    """
    return '(c) 2020 Giovanni Lombardo mailto://g.lombardo@protonmail.com'


def version() -> str:
    """
    It builds and gets the version string.

    :return: See description.
    :rtype: str.
    """
    return f'{version_major}.{version_minor}.{version_kind}'


def usage(arguments: List[Any]) -> Namespace:
    """
    It parses and validates command line arguments.

    :param arguments:    The command line arguments as retrieved from sys.argv.
    :type arguments:     List[str].

    :return: The Namespace instance filled with the parsed and valid command line arguments.
    :rtype: Namespace.
    """
    helps = dict(
        location='The filesystem location where SQL source files are stored.',
        encoding='The encoding to use for reading SQL source files.',
    )

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('location', help=helps['location'])
    parser.add_argument('-e', '--encoding', dest='encoding', default='utf-8', help=helps['encoding'])
    arguments = parser.parse_args(arguments)

    location = Path(arguments.location)

    if not location.exists():
        stderr.write(f'The `location` argument must be an existing folder.')
        exit(1)

    if not location.is_dir():
        stderr.write(f'The `location` argument must be a folder.')
        exit(2)

    arguments.location = location
    return arguments


def acquire_sql_file(session: Session, element: File, encoding: str) -> None:
    """
    It acquires metadata from the given file instance by using the givne encoding.

    :param session:    The Session instance object.
    :type session:     Session.

    :param element:    The File instance object pointing to SQL source file to be acquired.
    :type element:     File.

    :param encoding:   The encoding to use while reading content from the SQL source file.
    :type encoding:    str.

    :return: None
    :rtype: None.
    """

    def acquire_tokens(statement_id: int, current_item: Token) -> None:
        """
        It recursively acquires tokens belonging to the Statement instance with given statement_id from the given
        current item.

        :param statement_id:    The Statement instance object the current item belongs to.
        :type statement_id:     int.

        :param current_item:    The token to be acquired.
        :type current_item:     Token.

        :return: None.
        :rtype: None.
        """
        for item in current_item.tokens:

            # It skips whitespaces and punctuations
            if item.is_whitespace or item.ttype == Punctuation:
                getLogger(__name__).info(f'Skipping {item.ttype} from {statement_id}.')
                continue

            # The current token does not holds sub tokens
            if not item.is_group:
                unit = Unit(
                    kind=str(item.ttype),
                    value=item.value,
                    statement=statement_id
                )
                session.add(unit)
                session.commit()
                continue

            # The current token holds sub tokens
            acquire_tokens(
                statement_id=statement_id,
                current_item=item
            )

    try:
        with open(element.path, 'r', encoding=encoding, errors='ignore') as d:
            content = d.read()

        # TokenList of sql.Statement objects
        root = parse_sql(content, encoding=encoding)

        # Iterating over each item in root we get Token instances. All available Token
        # instances are declared in the source file sqlparse.tokens.
        for stmt in root:
            try:
                statement_obj = Statement(
                    name=stmt.get_name(),
                    file=element.identifier
                )
                session.add(statement_obj)
                session.commit()

                acquire_tokens(
                    statement_id=statement_obj.identifier,
                    current_item=stmt
                )

            except Exception as e:
                print(str(e))
                session.rollback()

    except (IOError, OSError, Exception) as e:
        stderr.write(f'Error reading `{element.path}`: {str(e)}')


def main(arguments: Namespace) -> int:
    """
    The entry point of the custom application logic behaviour.

    :param arguments:   The parsed and validated command line arguments as retrieved from usage.
    :type arguments:    Namespace.

    :return: The value to pass to the OS to communicated how the process ended.
    :rtype: int.
    """
    session = Session()
    build()

    for root, dirs, files in walk(str(arguments.location.absolute())):
        for f in files:
            if f.endswith('.sql'):
                path = Path(root) / f
                full_name = str(path.absolute())
                print(f'Reading: {full_name}')
                file_instance = File(path=full_name)
                session.add(file_instance)
                session.commit()
                acquire_sql_file(
                    session=session,
                    element=file_instance,
                    encoding=arguments.encoding
                )

    session.commit()
    return 0


if __name__ == '__main__':
    print(author())
    print(f'{str(Path(argv[0]).parts[-1])} version {version()}')
    elapsed = TimeIt(lambda: main(usage(argv[1:])), logger_name=__name__)
    exit(tuple(elapsed.return_values().values())[-1])