import csv
from src.main.mysql_connector import MySQLConnection
from src.main.utils.constants import ROUTES_CSV_PATH

class RoutesRepository:
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def recreate_routes_table(self):
        cursor = self.connection.connect()
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS routes")

        # Create table
        cursor.execute("""
            CREATE TABLE routes (
                route_id VARCHAR(50) PRIMARY KEY COMMENT 'Unique identifier for transport route',
                origin VARCHAR(100) COMMENT 'Starting city/location of route',
                destination VARCHAR(100) COMMENT 'Ending city/location of route',
                distance_km DECIMAL(10,2) COMMENT 'Distance between origin and destination in kilometers',
                avg_time_hours DECIMAL(5,2) COMMENT 'Average travel time expected for this route'
            )
        """)

        self.connection.commit()
        cursor.close()
        self.connection.close()
        print("routes table recreated successfully.")


    def insert_into_routes_from_csv(self):

       with open(ROUTES_CSV_PATH, newline='', encoding='utf-8') as csvfile:
          reader = csv.DictReader(csvfile)
          data = []
          for row in reader:
             data.append((
                 row["route_id"],
                 row["origin"],
                 row["destination"],
                 row["distance_km"],
                 row["avg_time_hours"]
                ))

       cursor = self.connection.connect()
       cursor.executemany("""
                          INSERT INTO routes (route_id, origin, destination, distance_km,avg_time_hours)
                          VALUES (%s, %s, %s, %s, %s)
                          """, data)

       self.connection.commit()
       cursor.close()
       self.connection.close()
    
    def get_all_routes(self):
        query = "SELECT route_id, origin, destination, distance_km,avg_time_hours FROM routes"
        cursor = self.connection.connect()
        cursor.execute(query)
        return cursor.fetchall()

    def get_routes_by_id(self, route_id):
        query = "SELECT route_id, origin, destination, distance_km,avg_time_hours FROM routes WHERE route_id = %s"
        cursor = self.connection.connect()
        cursor.execute(query, (route_id,))
        return cursor.fetchone()
    
    def get_routes_with_limit_of_records(self, limit):
        if(limit==None):
            limit=1
        query = f"SELECT route_id, origin, destination, distance_km,avg_time_hours FROM routes LIMIT {int(limit)}"
        cursor = self.connection.connect()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return rows