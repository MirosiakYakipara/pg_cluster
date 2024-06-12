import random
import subprocess
import time
from agent import Agent
from dotenv import load_dotenv
from psycopg2 import sql


load_dotenv("docker/writer.env")


def create_table(table_name):
    cursor = agent.connect_master.cursor()
    cursor.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name)))
    cursor.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {}(id integer PRIMARY KEY)").format(sql.Identifier(table_name)))

    agent.connect_master.commit()
    cursor.close()


def test_number(conn, number, table_name):
    global success, fail
    try:
        cursor = conn.cursor()
        cursor.execute(sql.SQL("INSERT INTO {} (id) VALUES (%s)").format(sql.Identifier(table_name)), (number, ))
        conn.commit()
        cursor.close()
        success += 1
        print("Получено число {}".format(number))
        return True
    except Exception as err:
        print("Ошибка получения данных {}: {}".format(number, err))
        conn.rollback()
        fail += 1
        return False


if __name__ == '__main__':
    agent = Agent()
    success = 0
    fail = 0

    create_table("test")
    for i in range(10000):
        if i == 5000:
            subprocess.runn(["docker", "compose", "stop", "pg-slave"])
        test_number(agent.connect_master, i, "test")
        time.sleep(random.choice([0.1, 0.2, 0.3, 0.4, 0.5]))
    print("Тесты закончилисью Успешно: {}. Провалено: {}".format(success, fail))
    subprocess.run(["docker", "compose", "start", "pg-slave"])

    time.sleep(15)
    agent.init_connections()
    success = 0
    fail = 0
    conn = agent.connect_master

    create_table("test")
    for i in range(1000000):
        if i == 500000:
            subprocess.runn(["docker", "compose", "stop", "pg-master"])
            conn = agent.connect_slave
        test_number(conn, i, "test")
        time.sleep(random.choice([0.1, 0.2, 0.3, 0.4, 0.5]))
    print("Тесты закончилисью Успешно: {}. Провалено: {}".format(success, fail))
    subprocess.run(["docker", "compose", "start", "pg-master"])
