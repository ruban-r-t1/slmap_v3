import json
import os
from src.main.mysql_connector import MySQLConnection
from src.main.utils.constants import WAREHOUSE_JSON_PATH

class WarehouseRepository:
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def recreate_warehouses_table(self):
        cursor = self.connection.connect()
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS warehouses")

        # Create table
        cursor.execute("""
            CREATE TABLE warehouses (
                warehouse_id VARCHAR(50) PRIMARY KEY,
                city VARCHAR(100),
                state VARCHAR(50),
                capacity INT
            )
        """)

        self.connection.commit()
        cursor.close()
        self.connection.close()
        print("Warehouses table recreated successfully.")


    def insert_into_warehouse_from_json(self):

       with open(WAREHOUSE_JSON_PATH, "r") as f:
            data = json.load(f)

       cursor = self.connection.connect()
       for item in data:
            cursor.execute("""
                INSERT INTO warehouses (warehouse_id, city, state, capacity)
                VALUES (%s, %s, %s, %s)
            """, (
                item["warehouse_id"], 
                item["city"], 
                item["state"], 
                int(item["capacity"])
            ))

       self.connection.commit()
       cursor.close()
       self.connection.close()

    def insert_warehouse(self, warehouse_id, city, state, capacity):
        query = """
            INSERT INTO warehouses (warehouse_id, city, state, capacity)
            VALUES (%s, %s, %s, %s)
        """
        cursor = self.connection.connect()
        cursor.execute(query, (warehouse_id, city, state, capacity))
        self.connection.commit()
    
    def get_all_warehouses(self):
        query = "SELECT warehouse_id, city, state, capacity FROM warehouses"
        cursor = self.connection.connect()
        cursor.execute(query)
        return cursor.fetchall()

    def get_warehouse_by_id(self, warehouse_id):
        query = "SELECT warehouse_id, city, state, capacity FROM warehouses WHERE warehouse_id = %s"
        cursor = self.connection.connect()
        cursor.execute(query, (warehouse_id,))
        return cursor.fetchone()
    
    def get_warehouse_with_limit_of_records(self, limit):
        if(limit==None):
            limit=1
        query = f"SELECT warehouse_id, city, state, capacity FROM warehouses LIMIT {int(limit)}"
        cursor = self.connection.connect()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return rows

