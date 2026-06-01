from src.main.mysql_connector import MySQLConnection
from src.main.repositories.courier_staff_repository import CourierStaffRepository

# Create connection object
db_conn = MySQLConnection()   # defaults to resources/db.properties

# Use repository
repo = CourierStaffRepository(db_conn)

repo.recreate_courierstaff_table()
repo.insert_into_courierstaff_from_csv()
# Fetch all warehouses
courierstaff = repo.get_courierstaff_with_limit_of_records(limit=None)
for w in courierstaff:
    print(f"CourierId: {w[0]}, Name: {w[1]}, Rating: {w[2]}, VehicleType: {w[3]}")

db_conn.close()