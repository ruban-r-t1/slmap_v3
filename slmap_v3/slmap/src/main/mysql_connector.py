import mysql.connector
import configparser
import os


class MySQLConnection:
    def __init__(self, config_file="../../resources/db.properties"):
        # Build absolute path to resources directory
        config_path = os.path.join(os.path.dirname(__file__), config_file)

        # Read properties file
        config = configparser.ConfigParser()
        config.read(config_path)

        self.host = config["mysql"]["host"]
        self.user = config["mysql"]["user"]
        self.password = config["mysql"]["password"]
        self.database = config["mysql"]["database"]

        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()
        return self.cursor

    def commit(self):
        if self.conn:
            self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()