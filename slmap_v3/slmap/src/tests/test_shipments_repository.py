from src.main.mysql_connector import MySQLConnection
from src.main.repositories.shipments_repository import ShipmentsRepository

# Create connection object
db_conn = MySQLConnection()   # defaults to resources/db.properties

# Use repository
repo = ShipmentsRepository(db_conn)

repo.recreate_shipments_table()
repo.insert_into_shipments_from_csv()
# Fetch all warehouses
shipments = repo.get_shipments_with_limit_of_records(limit=None)
for w in shipments:
    print(f"shipment_id: {w[0]}, order_date: {w[1]}, origin: {w[2]}, destination: {w[3]}, weight: {w[4]}, courier_id: {w[5]}, status: {w[6]}, delivery_date: {w[7]}")

db_conn.close()