import os
from sqlalchemy import create_engine, text


class TestDB:
    def __init__(self):
        self.db_name = os.environ['DATABASE_NAME'] + '_test'
        self.db_host = os.environ['DB_HOST']
        self.db_root_password = os.environ['MYSQL_ROOT_PASSWORD']
        if self.db_root_password:
            self.db_username = 'root'
            self.db_password = self.db_root_password
        else:
            self.db_username = os.environ['DB_USERNAME']
            self.db_password = os.environ['DB_PASSWORD']
        self.db_uri = 'mysql+pymysql://%s:%s@%s' % (self.db_username, self.db_password, self.db_host)

    def create_db(self):
        if self.db_root_password:
            engine = create_engine(self.db_uri)
            conn = engine.connect()
            conn.execute(text('COMMIT'))
            conn.execute(text(f'CREATE DATABASE {self.db_name}'))
            conn.close()
        return self.db_uri + '/' + self.db_name

    def drop_db(self):
        if self.db_root_password:
            engine = create_engine(self.db_uri)
            conn = engine.connect()
            conn.execute(text('COMMIT'))
            conn.execute(text(f'DROP DATABASE {self.db_name}'))
            conn.close()
