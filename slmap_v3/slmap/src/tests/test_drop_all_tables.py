from src.main.mysql_connector import MySQLConnection
from src.main.repositories.drop_all_tables import DropTables

# Create connection object
db_conn = MySQLConnection()   # defaults to resources/db.properties

# Use repository
repo = DropTables(db_conn)
repo.drop_table()