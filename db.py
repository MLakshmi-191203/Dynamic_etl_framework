import psycopg2
import pymysql

# PostgreSQL connection
def get_pg_conn():
    return psycopg2.connect(
        host="localhost",
        database="etl_db",
        user="postgres",
        password="Postgre@2000"
    )

# MySQL connection
def get_mysql_conn(database):
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Mysql@2000",
        database=database
    )