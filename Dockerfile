FROM postgres:9.6

WORKDIR /app

COPY agent.py ./
COPY main.py ./

RUN echo "" > /etc/apt/sources.list.d/pgdg.list
RUN echo 'deb http://archive.debian.org/debian/ stretch main contrib non-free' > /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y iputils-ping
RUN apt-get install python3 -y
RUN apt-get -y install python3-pip
RUN pip3 install psycopg2-binary
RUN pip3 install requests

RUN apt-get install iptables -y
RUN debconf-set-selections <<EOF
iptables-persistent iptables-persistent/autosave_v4 boolean true
iptables-persistent iptables-persistent/autosave_v6 boolean true
EOF
RUN apt-get install iptables-persistent -y

ENV PG_MAX_WAL_SENDERS 8
ENV PG_WAL_KEEP_SEGMENTS 8

COPY setup-replication.sh /docker-entrypoint-initdb.d/
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint-initdb.d/setup-replication.sh /docker-entrypoint.sh
