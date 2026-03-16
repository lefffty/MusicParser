from dotenv import load_dotenv
from psycopg2 import (
    connect,
    OperationalError,
    IntegrityError,
    DataError,
)
import os

from db_config import DatabaseConfig, QueryType

load_dotenv()


class DatabaseManager:
    def __init__(self, db_config: DatabaseConfig):
        self.user = os.getenv('DB_USER')
        self.name = os.getenv('DB_NAME')
        self.password = os.getenv('DB_PASSWORD')
        self.port = os.getenv('DB_PORT')
        self.host = os.getenv('DB_HOST')
        self.schema_name = os.getenv('SCHEMA_NAME')
        self.db_config = db_config

    def __enter__(self):
        try:
            self.connection = connect(
                dbname=self.name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print('Подключение установлено!')
            return self
        except OperationalError as e:
            print(f'Ошибка подключения или неверный пароль/логин: {e}')
            raise

    def get_many(self, relation) -> list[str]:
        query = self.db_config.get_query(relation, QueryType.selectMany)
        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
            )
            objects = cursor.fetchall()
        return objects

    def get_object_id(self, relation: str, params: tuple):
        query = self.db_config.get_query(relation, QueryType.selectOne)
        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                params
            )
            id, *_ = cursor.fetchone()
        return id

    def insert_object(self, relation: str, params: dict):
        query = self.db_config.get_query(relation, QueryType.insertOne)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(
                    query,
                    params
                )
                self.connection.commit()
                print('{} with params {} was inserted'.format(
                    relation.capitalize(), params))
            except TypeError as err:
                print('Error: {}'.format(err))
            except IntegrityError as err:
                print('Error: {}'.format(err))
            except DataError as err:
                print('Error: {}'.format(err))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        print('Подключение разорвано!')
