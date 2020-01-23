FROM ubuntu:18.04
MAINTAINER Sanjib Devnath <devnath.sanjib@gmail.com>

# Postgress
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main"'
RUN apt-get update && apt-get install -y gnupg2 wget
RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | apt-key add -
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y -q install postgresql postgresql-contrib libpq-dev zip unzip \
    && apt-get install -y openjdk-8-jdk \
    && apt-get install -y maven \
    && apt-get install ca-certificates-java \
    && apt-get clean \
    && update-ca-certificates -f

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

USER postgres
RUN /etc/init.d/postgresql start && psql --command "CREATE USER pguser WITH SUPERUSER PASSWORD 'pguser';" && createdb -O pguser pgdb

USER root
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/10/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/10/main/postgresql.conf

# install java

# download gremlin
RUN wget https://archive.apache.org/dist/tinkerpop/3.4.6/apache-tinkerpop-gremlin-server-3.4.6-bin.zip
RUN unzip apache-tinkerpop-gremlin-server-3.4.6-bin.zip
RUN rm -rf apache-tinkerpop-gremlin-server-3.4.6-bin.zip
RUN mv apache-tinkerpop-gremlin-server-3.4.6 gremlin-server

WORKDIR /gremlin-server
RUN bin/gremlin-server.sh install org.apache.tinkerpop neo4j-gremlin 3.4.6
RUN echo "gremlin.graph=org.apache.tinkerpop.gremlin.neo4j.structure.Neo4jGraph" > conf/neo4j-empty.properties
RUN echo "gremlin.neo4j.directory=/gremlin-server/data/neo4j.db" >> conf/neo4j-empty.properties
RUN echo "gremlin.neo4j.conf.dbms.auto_index.nodes.enabled=true" >> conf/neo4j-empty.properties
RUN echo "gremlin.neo4j.conf.dbms.auto_index.nodes.keys=true" >> conf/neo4j-empty.properties
RUN echo "gremlin.neo4j.conf.dbms.auto_index.relationships.enabled=true" >> conf/neo4j-empty.properties
RUN echo "gremlin.neo4j.conf.dbms.auto_index.relationships.keys=true" >> conf/neo4j-empty.properties
RUN bin/gremlin-server.sh conf/gremlin-server-neo4j.yaml &>/dev/null &

WORKDIR /

EXPOSE 5432 8182