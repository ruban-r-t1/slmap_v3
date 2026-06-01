import csv
from src.main.mysql_connector import MySQLConnection
from src.main.utils.constants import COURIER_STAFF_CSV_PATH

class CourierStaffRepository:
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def recreate_courierstaff_table(self):
        cursor = self.connection.connect()
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS courier_staff")

        # Create table
        cursor.execute("""
            CREATE TABLE courier_staff (
                courier_id varchar(50) NOT NULL COMMENT 'Unique identifier for courier employee',
                name varchar(150) NOT NULL COMMENT 'Full name of courier',
                rating decimal(3,1) DEFAULT NULL COMMENT 'Courier performance rating (scale)',
                vehicle_type varchar(50) DEFAULT NULL COMMENT 'Type of delivery vehicle used (Bike, Van, Truck, Car)',
                PRIMARY KEY (courier_id)
            )
        """)

        self.connection.commit()
        cursor.close()
        self.connection.close()
        print("courier_staff table recreated successfully.")


    def insert_into_courierstaff_from_csv(self):

       with open(COURIER_STAFF_CSV_PATH, newline='', encoding='utf-8') as csvfile:
          reader = csv.DictReader(csvfile)
          data = []
          for row in reader:
             data.append((
                 row["courier_id"],
                 row["name"],
                 float(row["rating"]),   # ensure rating is numeric
                 row["vehicle_type"]
                ))

       cursor = self.connection.connect()
       cursor.executemany("""
                          INSERT INTO courier_staff (courier_id, name, rating, vehicle_type)
                          VALUES (%s, %s, %s, %s)
                          """, data)

       self.connection.commit()
       cursor.close()
       self.connection.close()
    
    def get_all_courierstaff(self):
        query = "SELECT courier_id, name, rating, vehicle_type FROM courier_staff"
        cursor = self.connection.connect()
        cursor.execute(query)
        return cursor.fetchall()

    def get_courierstaff_by_id(self, courier_id):
        query = "SELECT courier_id, name, rating, vehicle_type FROM courier_staff WHERE courier_id = %s"
        cursor = self.connection.connect()
        cursor.execute(query, (courier_id,))
        return cursor.fetchone()
    
    def get_courierstaff_with_limit_of_records(self, limit):
        if(limit==None):
            limit=1
        query = f"SELECT courier_id, name, rating, vehicle_type FROM courier_staff LIMIT {int(limit)}"
        cursor = self.connection.connect()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return rows