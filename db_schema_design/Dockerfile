FROM postgres:16

ADD scripts/1_run_ddl_taxi_service_db.sql /docker-entrypoint-initdb.d
ADD scripts/2_copy_clients.sql /docker-entrypoint-initdb.d
ADD scripts/3_copy_cars.sql /docker-entrypoint-initdb.d
ADD scripts/4_copy_drivers.sql /docker-entrypoint-initdb.d
ADD scripts/5_copy_cardrivers.sql /docker-entrypoint-initdb.d

RUN chmod a+r /docker-entrypoint-initdb.d/*

EXPOSE 5432