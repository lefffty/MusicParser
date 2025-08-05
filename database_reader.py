from dotenv import load_dotenv
from psycopg2 import connect
import os


load_dotenv()


class DatabaseReader:
    def __init__(self):
        self.db_user = os.getenv('DB_USER')
        self.db_name = os.getenv('DB_NAME')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_port = os.getenv('DB_PORT')
        self.db_host = os.getenv('DB_HOST')

    def get_connection(self):
        connection = connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )
        print('Подключение установлено!')
        connection.close()


dr = DatabaseReader()
dr.get_connection()
