from src.main.mysql_connector import MySQLConnection

class DropTables:
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def drop_table(self):

        cursor = self.connection.connect()
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS shipment_tracking, shipments, courier_staff,routes,warehouses,costs")

        self.connection.commit()
        cursor.close()
        self.connection.close()
        print("All tables are dropped successfully.")