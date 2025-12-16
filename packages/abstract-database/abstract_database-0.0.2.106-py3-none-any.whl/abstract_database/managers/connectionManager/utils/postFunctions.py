from .main import *

def get_db_vars_from_kwargs(**kwargs):
    """
    Normalize DB-related kwargs into canonical connection variables.

    Accepted aliases (case-insensitive):
        port        -> port
        password    -> password, pass
        dbType      -> type, dbtype
        host        -> host, url, address
        dbUser      -> user, dbuser
        dbName      -> dbname, database, name
    """
    resolved = {}

    key_aliases = {
        "port": ["port"],
        "password": ["password", "pass"],
        "dbType": ["type", "dbtype"],
        "host": ["host", "url", "address"],
        "dbUser": ["user", "dbuser"],
        "dbName": ["dbname", "database", "name"],
    }

    # Normalize incoming kwargs once
    lowered_kwargs = {k.lower(): v for k, v in kwargs.items()}

    for canonical_key, aliases in key_aliases.items():
        for alias in aliases:
            if alias in lowered_kwargs:
                resolved[canonical_key] = lowered_kwargs[alias]
                break  # stop searching aliases, not keys

    return resolved

    
# Functions to interact with the connection manager
def create_connection(env_path=None, dbType=None, dbName=None, dbUser=None):
    return connectionManager(env_path=env_path, dbType=dbType, dbName=dbName,dbUser=dbUser)

def get_db_connection(env_path=None, **kwargs):
    db_vars = get_db_vars_from_kwargs(**kwargs)

    create_connection(
        env_path=env_path,
        dbType=db_vars.get("dbType"),
        dbName=db_vars.get("dbName"),
        dbUser=db_vars.get("dbUser"),
    )

    return connectionManager().get_db_connection()
def put_db_connection(conn):
    connectionManager().put_db_connection(conn)

def connect_db():
    return connectionManager().connect_db()

def get_insert(tableName):
    return connectionManager().get_insert(tableName)

def fetchFromDb(tableName, searchValue):
    return connectionManager().fetchFromDb(tableName, searchValue)

def insertIntoDb(tableName, searchValue, insertValue):
    return connectionManager().insertIntoDb(tableName, searchValue, insertValue)

def search_multiple_fields(query, **kwargs):
    return connectionManager().search_multiple_fields(query, **kwargs)

def get_first_row_as_dict(tableName=None, rowNum=1):
    return connectionManager().get_first_row_as_dict(tableName, rowNum)
def get_cur_conn(use_dict_cursor=True):
    """
    Get a database connection and a RealDictCursor.
    Returns:
        tuple: (cursor, connection)
    """
    conn = connectionManager().get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor) if use_dict_cursor else conn.cursor()
    return cur, conn
