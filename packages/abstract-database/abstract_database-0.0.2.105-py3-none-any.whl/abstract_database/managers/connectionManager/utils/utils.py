from ..imports import *

                              
def get_safe_password(password):
    safe_password = quote_plus(password)
    return safe_password
# Existing utility functions remain the same
def get_dbType(dbType=None):
    return dbType or 'database'

def get_dbName(dbName=None):
    return dbName or 'abstract'

def get_dbUser(dbUser=None):
    return dbUser

def verify_env_path(env_path=None):
    return env_path or get_env_path()

def get_db_env_key(dbType=None, dbName=None, dbUser=None, key=None):
    dbType = get_dbType(dbType=dbType)
    dbName = get_dbName(dbName=dbName)
    dbUser = get_dbUser(dbUser=dbUser)
    return f"{dbName.upper()}_{dbType.upper()}_{key.upper()}"

def get_env_key_value(dbType=None, dbName=None, dbUser=None, key=None, env_path=None):
    dbType = get_dbType(dbType=dbType)
    dbName = get_dbName(dbName=dbName)
    dbUser = get_dbUser(dbUser=dbUser)
    env_path = verify_env_path(env_path=env_path)
    env_key = get_db_env_key(dbType=dbType,
                             dbName=dbName,
                             dbUser=dbUser,
                             key=key)
    return get_env_value(key=env_key, path=env_path)

def get_db_vars(env_path=None, dbType=None, dbName=None, dbUser=None):
    dbVars = {}
    protocol = 'postgresql'
    if 'rabbit' in dbType.lower():
        protocol = 'amqp'
    db_values = [dbName,dbType,dbUser]
    
    for key in ['user', 'password', 'host', 'port', 'dbname']:
        
        for i in range(2):
            peices = db_values
            if i:
                peices = db_values[:-1]
            peices = [peice for peice in peices if peice]
            piece = '_'.join(peices)
            env_key = f"{piece}_{key}".upper()
            env_value = get_env_value(key=env_key, path=env_path)
            if env_value:
                break

        if is_number(env_value):
            env_value = int(env_value)
   
        dbVars[key] = env_value
    dbVars['dburl'] = f"{protocol}://{dbVars['user']}:{dbVars['password']}@{dbVars['host']}:{dbVars['port']}/{dbVars['dbname']}"
    return dbVars

def safe_load_from_json(file_path=None):
    if file_path:
        return safe_load_from_json(file_path)
