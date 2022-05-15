import argparse
import csv
import configparser
import platform
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
        '-T',
        dest='trust_server_certificate',
        help="Trust the server certificate",       
        action='store_true'
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
        '-a',
        dest='count',
        help="Max. # of errors before abort ",
        type=int
    )

    parser.add_argument(
        '-d',
        dest='severity_display',
        help="Min. severity level to display",
        type=int
    )

    parser.add_argument(
        '-f',
        dest='severity_failure',
        help="Min. severity level for failure",
        type=int
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
    odbcinst_path = ''
    if platform.system() == 'Darwin':
        odbcinst_path = '/usr/local/etc/odbcinst.ini'
    elif platform.system() == 'Linux':
        odbcinst_path = '/etc/odbcinst.ini'
    else:
        raise Exception(f"Unsupported system: {platform.system()}")

    config.read(odbcinst_path)
    for section in config.sections():
        if 'msodbcsql' in config[section].get('Driver'):
            return section
    raise Exception("No Microsoft ODBC Driver for SQL Server detected. " + \
                    "Search for driver file `msodbcsql` in config was not found")


def translate_ftds_alias(alias: str):
    config = configparser.ConfigParser()
    freetds_path = ''
    if platform.system() == 'Darwin':
        freetds_path = '/usr/local/etc/freetds.conf'
    elif platform.system() == 'Linux':
        freetds_path = '/etc/freetds/freetds.conf'
    else:
        raise Exception(f"Unsupported system: {platform.system()}")

    config.read(freetds_path)
    if alias in config:
        dsn = []
        if 'port' in config[alias]:
            dsn.append(f"PORT={config[alias]['port']}")
        if 'host' in config[alias]:
            dsn.append(f"SERVER={config[alias]['host']}")
        if 'client charset' in config[alias]:
            dsn.append(f"CHARSET={config[alias]['client charset']}")
        return dsn
    raise Exception(f"Unknown alias '{alias}' in {freetds_path}")


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
    # Clean up sqsh escape sequences from query
    query = query.replace('\\\\$', '$')

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

    if args.trust_server_certificate:
        dsn += [f'TrustServerCertificate=YES']

    conn = pyodbc.connect(';'.join(dsn))
    cur = conn.cursor()

    writer = csv.writer(sys.stdout)
    cur.execute(query)
    writer.writerow([d[0] for d in cur.description])
    for row in cur:
        writer.writerow(row)


if __name__ == '__main__':
    main()
