import csv
from src.main.mysql_connector import MySQLConnection
from src.main.utils.constants import COSTS_CSV_PATH

class CostsRepository:
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def recreate_costs_table(self):
        cursor = self.connection.connect()
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS costs")

        # Create table
        cursor.execute("""
            CREATE TABLE costs (
                       shipment_id VARCHAR(50) PRIMARY KEY COMMENT 'Shipment linked to cost record (FK to shipments)',
                       fuel_cost DECIMAL(15,2) COMMENT 'Fuel cost incurred for shipment delivery',
                       labor_cost DECIMAL(15,2) COMMENT 'Courier labor cost for shipment',
                       misc_cost DECIMAL(15,2) COMMENT 'Additional operational costs (handling, packaging, etc.)',
                       CONSTRAINT fk_costs_shipment
                            FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
            )
        """)

        self.connection.commit()
        cursor.close()
        self.connection.close()
        print("costs table recreated successfully.")


    def insert_into_costs_from_csv(self):

       with open(COSTS_CSV_PATH, newline='', encoding='utf-8') as csvfile:
          reader = csv.DictReader(csvfile)
          data = []
          for row in reader:
             data.append((
                 row["shipment_id"],
                 float(row["fuel_cost"]),
                 float(row["labor_cost"]),
                 float(row["misc_cost"])
                ))

       cursor = self.connection.connect()
       cursor.executemany("""
                          INSERT INTO costs (shipment_id, fuel_cost, labor_cost, misc_cost)
                          VALUES (%s, %s, %s, %s)
                          """, data)

       self.connection.commit()
       cursor.close()
       self.connection.close()
    
    def get_all_costs(self):
        query = "SELECT shipment_id, fuel_cost, labor_cost, misc_cost FROM costs"
        cursor = self.connection.connect()
        cursor.execute(query)
        return cursor.fetchall()

    def get_costs_by_id(self, shipment_id):
        query = "SELECT shipment_id, fuel_cost, labor_cost, misc_cost WHERE shipment_id = %s"
        cursor = self.connection.connect()
        cursor.execute(query, (shipment_id,))
        return cursor.fetchone()
    
    def get_costs_with_limit_of_records(self, limit):
        if(limit==None):
            limit=1
        query = f"SELECT shipment_id, fuel_cost, labor_cost, misc_cost FROM costs LIMIT {int(limit)}"
        cursor = self.connection.connect()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return rows