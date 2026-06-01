import json
from main.mysql_connector import MySQLConnection
from main.utils.constants import SHIPMENTS_JSON_PATH
from main.utils.constants import SEARCH_BY_SHIPMENT_ID
from main.utils.constants import TOTAL_SHIPMENTS
from main.utils.constants import TOTAL_DELIVERED_SHIPMENTS
from main.utils.constants import TOTAL_CANCELLED_SHIPMENTS
from main.utils.constants import AVERAGE_DELIVERY_TIME
from main.utils.constants import TOTAL_OPERATIONAL_COST_OF_SHIPMENTS
from main.utils.constants import DISTINCT_ORIGINS
from main.utils.constants import DISTINCT_DESTINATIONS
from main.utils.constants import DISTINCT_COURIERS

class ShipmentsRepository:
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def recreate_shipments_table(self):
        cursor = self.connection.connect()
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS shipments")

        # Create table
        cursor.execute("""
            CREATE TABLE shipments (
                shipment_id   VARCHAR(50) PRIMARY KEY COMMENT 'Unique identifier for each shipment/order',
                order_date    DATE NOT NULL COMMENT 'Date when the shipment order was created',
                origin        VARCHAR(100) NOT NULL COMMENT 'City/location where shipment starts',
                destination   VARCHAR(100) NOT NULL COMMENT 'Delivery city/location',
                weight        DECIMAL(10,2) NOT NULL COMMENT 'Weight of the shipment in kg',
                courier_id    VARCHAR(50) COMMENT 'Courier responsible for delivery (FK to courier_staff)',
                status        VARCHAR(50) NOT NULL COMMENT 'Current shipment status (Delivered, In Transit, Cancelled, etc.)',
                delivery_date DATE NULL COMMENT 'Date when shipment was delivered (NULL if not delivered yet)',
                CONSTRAINT fk_courier FOREIGN KEY (courier_id) REFERENCES courier_staff(courier_id)
            )
        """)

        self.connection.commit()
        cursor.close()
        self.connection.close()
        print("shipments table recreated successfully.")


    def insert_into_shipments_from_csv(self):

       with open(SHIPMENTS_JSON_PATH) as f:
          data = json.load(f)

       cursor = self.connection.connect()
       for item in data:
           cursor.execute("""
                          INSERT INTO shipments (shipment_id, order_date, origin, destination, weight, courier_id, status, delivery_date)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                          """, (
                              item["shipment_id"],
                              item["order_date"],
                              item["origin"],
                              item["destination"],
                              item["weight"],
                              item["courier_id"],
                              item["status"],
                              item["delivery_date"]
                          ))

       self.connection.commit()
       cursor.close()
       self.connection.close()

    def get_shipments_by_id(self, shipment_id):
        query = SEARCH_BY_SHIPMENT_ID
        cursor = self.connection.connect()
        cursor.execute(query, (shipment_id,))
        shipment_data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        self.connection.close()
        return columns,shipment_data
    
    def get_shipments_with_limit_of_records(self, limit):
        if(limit==None):
            limit=1
        query = f"SELECT shipment_id, order_date, origin, destination, weight, courier_id, status, delivery_date FROM shipments LIMIT {int(limit)}"
        cursor = self.connection.connect()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return rows
    
    def filter_shipments(self, status,origin,destination,start_date,end_date,courier_id):
        
        base_query = "SELECT * FROM shipments"
        params = []
        conditions = []

        if status:
            conditions.append("status = %s")
            params.append(status)
        if origin:
            conditions.append("origin = %s")
            params.append(origin)
        if destination:
            conditions.append("destination = %s")
            params.append(destination)
        if start_date and end_date:
            conditions.append("order_date BETWEEN %s AND %s")
            params.extend([start_date, end_date])
        if courier_id:
            conditions.append("courier_id = %s")
            params.append(courier_id)

        # Build final query
        if conditions:
            query = base_query + " WHERE " + " AND ".join(conditions)
        else:
            query = base_query

        print("filter query: ",query)
        print("params: ",params)

        cursor = self.connection.connect()
        cursor.execute(query, tuple(params))
        filtered_data=cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        self.connection.close()
        return columns,filtered_data
    
    def total_count_shipments(self):
        query = TOTAL_SHIPMENTS
        cursor = self.connection.connect()
        cursor.execute(query)
        total_shipment_count=cursor.fetchone()[0]
        print("from repositor: ",total_shipment_count)
        cursor.close()
        self.connection.close()
        return total_shipment_count
    
    def total_count_shipments_and_delivered_cancelled_shipments(self):
        query = TOTAL_SHIPMENTS
        cursor = self.connection.connect()
        cursor.execute(query)
        total_shipment_count=cursor.fetchone()[0]
        print("from repository total_delivered_count: ",total_shipment_count)

        query = TOTAL_DELIVERED_SHIPMENTS
        cursor.execute(query)
        total_delivered_count=cursor.fetchone()[0]
        print("from repository delivered: ",total_delivered_count)

        query = TOTAL_CANCELLED_SHIPMENTS
        cursor.execute(query)
        total_cancelled_count=cursor.fetchone()[0]
        print("from repository cancelled: ",total_cancelled_count)

        cursor.close()
        self.connection.close()
        return total_shipment_count,total_delivered_count,total_cancelled_count
    
    def avg_duration_delivered_shipments(self):
        query = AVERAGE_DELIVERY_TIME
        cursor = self.connection.connect()
        cursor.execute(query)
        avg_delivered_time=cursor.fetchone()
        print("from repository avg_duration_delivered_shipments: ",avg_delivered_time)
        cursor.close()
        self.connection.close()
        return avg_delivered_time
    
    def get_distinct_origins(self):
        cursor = self.connection.connect()
        cursor.execute(DISTINCT_ORIGINS)
        rows = [r[0] for r in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return rows

    def get_distinct_destinations(self):
        cursor = self.connection.connect()
        cursor.execute(DISTINCT_DESTINATIONS)
        rows = [r[0] for r in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return rows

    def get_distinct_couriers(self):
        cursor = self.connection.connect()
        cursor.execute(DISTINCT_COURIERS)
        rows = cursor.fetchall()  # list of (courier_id, name)
        cursor.close()
        self.connection.close()
        return rows

    def fetch_analytics_view(self, query):
        cursor = self.connection.connect()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        self.connection.close()
        return columns, rows

    def total_operational_cost_of_shipment(self):
        query = TOTAL_OPERATIONAL_COST_OF_SHIPMENTS
        cursor = self.connection.connect()
        cursor.execute(query)
        total_operational_cost=cursor.fetchone()[0]
        print("from repository total_operational_cost_of_shipment: ",total_operational_cost)
        cursor.close()
        self.connection.close()
        return total_operational_cost
