from src.main.mysql_connector import MySQLConnection
from src.main.repositories.routes_repository import RoutesRepository

# Create connection object
db_conn = MySQLConnection()   # defaults to resources/db.properties

# Use repository
repo = RoutesRepository(db_conn)

repo.recreate_routes_table()
repo.insert_into_routes_from_csv()
# Fetch all warehouses
courierstaff = repo.get_routes_with_limit_of_records(limit=None)
for w in courierstaff:
    print(f"Tracking_id: {w[0]}, Shipment_id: {w[1]}, status: {w[2]}, timestamp: {w[3]}")

db_conn.close()