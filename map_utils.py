import pandas as pd
from database import execute_query

def get_locations(conn):
    query = "SELECT name, type, latitude, longitude FROM locations"
    results = execute_query(conn, query)
    return pd.DataFrame(results, columns=['name', 'type', 'latitude', 'longitude'])
