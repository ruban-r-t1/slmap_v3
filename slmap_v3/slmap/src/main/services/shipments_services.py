
from main.mysql_connector import MySQLConnection
from main.repositories.shipments_repository import ShipmentsRepository

class ShipmentsService:
    def fetch_Shipment_by_id(self,shipment_id):
        # Create connection object
        db_conn = MySQLConnection()   # defaults to resources/db.properties

        # Use repository
        shipment_repo = ShipmentsRepository(db_conn)

        columns,shipment_data = shipment_repo.get_shipments_by_id(shipment_id)
        return columns,shipment_data
    
    def filter_shipments(self,status,origin,destination,start_date,end_date,courier_id):
        # Create connection object
        db_conn = MySQLConnection()   # defaults to resources/db.properties

        # Use repository
        shipment_repo = ShipmentsRepository(db_conn)

        columns,shipment_data = shipment_repo.filter_shipments(status,origin,destination,start_date,end_date,courier_id)
        return columns,shipment_data
    
    def fetch_total_count_shipments(self):
         # Create connection object
        db_conn = MySQLConnection()   # defaults to resources/db.properties

        # Use repository
        shipment_repo = ShipmentsRepository(db_conn)

        total_count_shipments = shipment_repo.total_count_shipments();
        print(total_count_shipments)
        return total_count_shipments
    
    def fetch_shipments_percentile(self):
         # Create connection object
        db_conn = MySQLConnection()   # defaults to resources/db.properties

        # Use repository
        shipment_repo = ShipmentsRepository(db_conn)

        total_count_shipments,total_delivered_count,total_cancelled_count = shipment_repo.total_count_shipments_and_delivered_cancelled_shipments()
        print(total_count_shipments,total_delivered_count,total_cancelled_count)
        delivered_percentile = str(round((total_delivered_count/total_count_shipments)*100,2)) +'%'
        cancelled_percentile = str(round((total_cancelled_count/total_count_shipments)*100,2)) + '%'
        return total_count_shipments,total_delivered_count,total_cancelled_count,delivered_percentile,cancelled_percentile
    
    def avg_duration_delivered_shipments(self):
        # Create connection object
        db_conn = MySQLConnection()   # defaults to resources/db.properties

        # Use repository
        shipment_repo = ShipmentsRepository(db_conn)

        return shipment_repo.avg_duration_delivered_shipments()
    
    def fetch_filter_options(self):
        db_conn = MySQLConnection()
        shipment_repo = ShipmentsRepository(db_conn)
        origins = shipment_repo.get_distinct_origins()

        db_conn = MySQLConnection()
        shipment_repo = ShipmentsRepository(db_conn)
        destinations = shipment_repo.get_distinct_destinations()

        db_conn = MySQLConnection()
        shipment_repo = ShipmentsRepository(db_conn)
        couriers = shipment_repo.get_distinct_couriers()
        return origins, destinations, couriers

    def fetch_analytics_view(self, query):
        db_conn = MySQLConnection()
        shipment_repo = ShipmentsRepository(db_conn)
        return shipment_repo.fetch_analytics_view(query)

    def total_operational_cost_of_shipment(self):
        # Create connection object
        db_conn = MySQLConnection()   # defaults to resources/db.properties

        # Use repository
        shipment_repo = ShipmentsRepository(db_conn)

        return shipment_repo.total_operational_cost_of_shipment()