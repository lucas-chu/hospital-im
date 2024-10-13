import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_connection():
    conn = psycopg2.connect(
        host=os.environ['PGHOST'],
        database=os.environ['PGDATABASE'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        port=os.environ['PGPORT']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

def close_connection(conn):
    conn.close()

def execute_query(conn, query, params=None):
    with conn.cursor() as cur:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        try:
            return cur.fetchall()
        except psycopg2.ProgrammingError:
            return None

def get_total_hospitals(conn):
    query = "SELECT COUNT(*) FROM locations WHERE type = 'Hospital'"
    result = execute_query(conn, query)
    return result[0][0] if result else 0

def get_total_donation_centers(conn):
    query = "SELECT COUNT(*) FROM locations WHERE type = 'Donation Center'"
    result = execute_query(conn, query)
    return result[0][0] if result else 0

def get_total_available_organs(conn):
    query = "SELECT SUM(quantity) FROM inventory WHERE item_type = 'Organ' AND status = 'Available'"
    result = execute_query(conn, query)
    return result[0][0] if result else 0

# Add more database functions as needed for other modules

# Initialize database tables
def init_db(conn):
    queries = [
        """
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT NOT NULL,
            blood_type VARCHAR(5) NOT NULL,
            organ_needed VARCHAR(50),
            status VARCHAR(50) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            item_name VARCHAR(100) NOT NULL,
            item_type VARCHAR(50) NOT NULL,
            quantity INT NOT NULL,
            status VARCHAR(50) NOT NULL,
            location_id INT REFERENCES locations(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS schedules (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            description TEXT,
            location_id INT REFERENCES locations(id)
        )
        """
    ]
    
    for query in queries:
        execute_query(conn, query)

# Call this function when setting up the application for the first time
init_db(create_connection())
