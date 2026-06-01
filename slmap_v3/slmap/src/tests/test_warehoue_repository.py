from src.main.mysql_connector import MySQLConnection
from src.main.repositories.warehouse_repository import WarehouseRepository

# Create connection object
db_conn = MySQLConnection()   # defaults to resources/db.properties

# Use repository
repo = WarehouseRepository(db_conn)

repo.recreate_warehouses_table()
repo.insert_into_warehouse_from_json()

# Fetch all warehouses
warehouses = repo.get_warehouse_with_limit_of_records(limit=None)
for w in warehouses:
    print(f"ID: {w[0]}, City: {w[1]}, State: {w[2]}, Capacity: {w[3]}")

# Fetch single warehouse by ID
#warehouse = repo.get_warehouse_by_id("W001")
#print("Single warehouse:", warehouse)

# Close connection
db_conn.close()