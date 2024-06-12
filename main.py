import time
import subprocess

from agent import Agent


def master():
    while True:
        status_arbiter = agent.connect_arbiter()
        status_slave = agent.connect_slave()
        if not status_arbiter and not status_slave:
            status_edit_iptables = subprocess.run(["iptables", "-P", "INPUT", "DROP"])
            status_save_iptables = subprocess.run(["iptables-save", ">", "/etc/iptables/rules.v4"])
            if status_edit_iptables == 0 and status_save_iptables == 0:
                print('Входящие подлючения заблокированы')
                break
            else:
                print('Ошибка блока подключений')
        time.sleep(5)


def slave():
    while True:
        status_agent_master = agent.arbiter_connect_master()
        if status_agent_master or status_agent_master is None:
            time.sleep(1)
        else:
            status_master = agent.connect_master
            if not status_master:
                print('Повышаем Slave до Master')
                status_promote = subprocess.run(["touch", "/tmp/promote_me"])
                if status_promote.returncode == 0:
                    print('Успешное повышение')
                    break
                else:
                    print('Ошибка создания триггер файла')


if __name__ == '__main__':
    agent = Agent()

    if agent.role == "Master":
        master()
    elif agent.role == "Slave":
        slave()
