import os
import time

import requests
import psycopg2


def connect_db(dbname, user, password, host, port=5432):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        print('Успешное соединение с {}:{}'.format(host, port))
        return conn
    except psycopg2.OperationalError as err:
        print('Ошибка подключения к {}: {}'.format(host, err))
        return None


class Agent:
    def __init__(self):
        self.role = os.environ.get('ROLE')
        self.user = os.environ.get('POSTGRES_USER')
        self.password = os.environ.get('POSTGRES_PASSWORD')
        self.dbname = os.environ.get('POSTGRES_DB')
        self.master_host = os.environ.get('MASTER_HOST')
        self.slave_host = os.environ.get('SLAVE_HOST')
        self.arbiter_host = os.environ.get('ARBITER_HOST')

        self.conn_master = None
        self.conn_slave = None

        if self.role != 'Arbiter':
            self.init_connections()

    def init_connections(self):
        print('Проверка подключений!')

        if self.role == 'Writer':
            self.conn_master = connect_db(self.dbname, self.user, self.password, self.master_host)
            self.conn_slave = connect_db(self.dbname, self.user, self.password, self.slave_host, 5433)
        else:
            for _ in range(4):
                if self.master_host and self.conn_master is None:
                    self.conn_master = connect_db(self.dbname, self.user, self.password, self.master_host)
                if self.slave_host and self.conn_slave is None:
                    self.conn_slave = connect_db(self.dbname, self.user, self.password, self.slave_host)

                if (self.master_host and not self.conn_master) or (self.slave_host and not self.conn_slave):
                    time.sleep(5)
                else:
                    break

    def check_connect(self, conn_attr, host):
        try:
            connect = getattr(self, conn_attr)
            if connect is None:
                connect = connect_db(self.dbname, self.user, self.password, host)
                setattr(self, conn_attr, connect)
            cursor = connect.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as err:
            print("Ошибка подключения к {}: {}".format(conn_attr.split('_')[-1].capitalize(), err))
            setattr(self, conn_attr, None)
            return False

    def connect_master(self):
        return self.check_connect('conn_master', self.master_host)

    def connect_slave(self):
        return self.check_connect('conn_slave', self.slave_host)

    def arbiter_connect_master(self):
        try:
            r = requests.get('http://{}:8000/status/master'.format(self.arbiter_host))
            status = r.json().get('Master alive')
            print('Успешное подключение Арбитра к Мастеру: {}'.format(status))
            return status
        except Exception as err:
            print('Ошибка подключения Арбитра к Мастеру: {}'.format(err))
            return None

    def connect_arbiter(self):
        try:
            r = requests.get('http://{}:8000/status/arbiter'.format(self.arbiter_host))
            status = r.json().get('Arbiter alive')
            print('Успешное подключение к Арбитру: {}'.format(status))
            return status
        except Exception as err:
            print('Ошибка подключения к Арбитру: {}'.format(err))
            return False
