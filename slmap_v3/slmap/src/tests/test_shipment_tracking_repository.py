from src.main.mysql_connector import MySQLConnection
from src.main.repositories.shipment_tracking_repository import ShipmentTrackingRepository

# Create connection object
db_conn = MySQLConnection()   # defaults to resources/db.properties

# Use repository
repo = ShipmentTrackingRepository(db_conn)

repo.recreate_shipment_tracking_table()
repo.insert_into_shipment_tracking_from_csv()
# Fetch all warehouses
shipment_tracking = repo.get_shipment_tracking_with_limit_of_records(limit=None)
for w in shipment_tracking:
    print(f"tracking_id: {w[0]}, shipment_id: {w[1]}, status: {w[2]}, timestamp: {w[3]}")

db_conn.close()