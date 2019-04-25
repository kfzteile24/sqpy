import argparse
import csv
import configparser
import pyodbc
import select
import sys


def setup_args():
    parser = argparse.ArgumentParser(description="Outputs MSSQL query results as proper CSV, similar to sqsh.")

    parser.add_argument(
        '-U',
        dest='user',
        help="Database user (default: None)",
        type=str,
        default=''
    )

    parser.add_argument(
        '-P',
        dest='password',
        help="Database user password (default: None)",
        type=str,
        default=''
    )

    parser.add_argument(
        '-S',
        dest='ftds_server',
        help="Server alias, as defined in freetds config (/etc/freetds/freetds.conf usually)",
        type=str,
        default=''
    )

    parser.add_argument(
        '-H',
        dest='hostname',
        help="Database host name",
        type=str,
        default=''
    )

    parser.add_argument(
        '-D',
        dest='database',
        help="Name of the database to use",
        type=str,
    )

    parser.add_argument(
        '-C',
        dest='sql',
        help="SQL command to execute (can also be passed in via STDIN)",
        type=str,
        default=''
    )

    parser.add_argument(
        '-J',
        dest='charset',
        help="ODBC client charset",
        type=str,
        default=''
    )

    parser.add_argument(
        '-m',
        dest='display_mode',
        help="Set display mode",
        type=str,
        required=True,
        choices=['csv']
    )

    return parser.parse_args()


def detect_mssql_odbc():
    config = configparser.ConfigParser()
    # TODO: Ensure this also works on other distros and maybe even Mac OS
    config.read('/etc/odbcinst.ini')
    for section in config.sections():
        if 'msodbcsql' in config[section].get('Driver'):
            return section
    raise Exception("No Microsoft ODBC Driver for SQL Server detected. " + \
                    "Search for driver file `msodbcsql` in config was not found")


def translate_ftds_alias(alias: str):
    config = configparser.ConfigParser()
    config.read('/etc/freetds/freetds.conf')
    if alias in config:
        dsn = []
        if 'port' in config[alias]:
            dsn.append(f"PORT={config[alias]['port']}")
        if 'host' in config[alias]:
            dsn.append(f"SERVER={config[alias]['host']}")
        if 'client charset' in config[alias]:
            dsn.append(f"CHARSET={config[alias]['client charset']}")
        return dsn
    raise Exception(f"Unknown alias '{alias}' in /etc/freetds/freetds.conf")


def main():
    """CLI entry point"""
    args = setup_args()
    if args.sql == '':
        if select.select([sys.stdin,],[],[],0.0)[0]:
            query = sys.stdin.read()
        else:
            raise Exception("Need a query to execute")
    else:
        query = args.sql

    # Clean up \go from the end of the query
    query = query.strip()
    if query[-3:].lower()=='\\go':
        query = query[:-3].strip()

    dsn = [f'DRIVER={{{detect_mssql_odbc()}}}']
    if args.ftds_server:
        dsn += translate_ftds_alias(args.ftds_server)
    elif args.hostname:
        dsn += [f'SERVER={args.hostname}']
        if args.charset:
            dsn += [f'CHARSET={args.charset}']

    if args.database:
        dsn += [f'DATABASE={args.database}']

    if args.user:
        dsn += [f'UID={args.user}']

    if args.password:
        dsn += [f'PWD={args.password}']

    conn = pyodbc.connect(';'.join(dsn))
    cur = conn.cursor()

    writer = csv.writer(sys.stdout)
    cur.execute(query)
    writer.writerow([d[0] for d in cur.description])
    for row in cur:
        writer.writerow(row)


if __name__ == '__main__':
    main()
