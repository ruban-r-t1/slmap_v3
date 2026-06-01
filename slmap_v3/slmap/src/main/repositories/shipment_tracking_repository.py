import csv
from src.main.mysql_connector import MySQLConnection
from src.main.utils.constants import SHIPMENT_TRACKING_CSV_PATH

class ShipmentTrackingRepository:
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def recreate_shipment_tracking_table(self):
        cursor = self.connection.connect()
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS shipment_tracking")

        # Create table
        cursor.execute("""
            CREATE TABLE shipment_tracking (
                       tracking_id  INT PRIMARY KEY COMMENT 'Unique identifier for tracking event',
                       shipment_id  VARCHAR(50) NOT NULL COMMENT 'Shipment linked to this event (FK to shipments)',
                       status       VARCHAR(50) NOT NULL COMMENT 'Status update at this stage (Picked Up, In Transit, Delivered, etc.)',
                       timestamp    DATETIME NOT NULL COMMENT 'Date & time when this tracking event occurred',
                       CONSTRAINT fk_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
                       )
            """)

        self.connection.commit()
        cursor.close()
        self.connection.close()
        print("shipment_tracking table recreated successfully.")


    def insert_into_shipment_tracking_from_csv(self):

       with open(SHIPMENT_TRACKING_CSV_PATH, newline='', encoding='utf-8') as csvfile:
          reader = csv.DictReader(csvfile)
          data = []
          for row in reader:
             data.append((
                 int(row["tracking_id"]),
                 row["shipment_id"],
                 row["status"],
                 row["timestamp"]
                ))

       cursor = self.connection.connect()
       cursor.executemany("""
                          INSERT INTO shipment_tracking (tracking_id, shipment_id, status, timestamp)
                          VALUES (%s, %s, %s, %s)
                          """, data)

       self.connection.commit()
       cursor.close()
       self.connection.close()
    
    def get_all_shipment_tracking(self):
        query = "SELECT tracking_id, shipment_id, status, timestamp FROM shipment_tracking"
        cursor = self.connection.connect()
        cursor.execute(query)
        return cursor.fetchall()

    def get_shipment_tracking_by_id(self, tracking_id):
        query = "SELECT tracking_id, shipment_id, status, timestamp FROM shipment_tracking WHERE courier_id = %s"
        cursor = self.connection.connect()
        cursor.execute(query, (tracking_id,))
        return cursor.fetchone()
    
    def get_shipment_tracking_with_limit_of_records(self, limit):
        if(limit==None):
            limit=1
        query = f"SELECT tracking_id, shipment_id, status, timestamp FROM shipment_tracking LIMIT {int(limit)}"
        cursor = self.connection.connect()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return rows