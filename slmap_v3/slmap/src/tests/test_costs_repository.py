from src.main.mysql_connector import MySQLConnection
from src.main.repositories.costs_repository import CostsRepository

# Create connection object
db_conn = MySQLConnection()   # defaults to resources/db.properties

# Use repository
repo = CostsRepository(db_conn)

repo.recreate_costs_table()
repo.insert_into_costs_from_csv()
# Fetch all warehouses
costs = repo.get_costs_with_limit_of_records(limit=None)
for w in costs:
    print(f"shipment_id: {w[0]}, fuel_cost: {w[1]}, labor_cost: {w[2]}, misc_cost: {w[3]}")

db_conn.close()