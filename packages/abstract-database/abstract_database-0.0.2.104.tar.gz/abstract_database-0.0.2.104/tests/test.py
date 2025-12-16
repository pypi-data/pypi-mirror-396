from imports import *
conn_mgr = connectionManager(dbName="abstract_clients",dbType="database", dbUser="ae_ext_rw")
input(conn_mgr.get_db_vars())
conn_mgr.connect_db()
