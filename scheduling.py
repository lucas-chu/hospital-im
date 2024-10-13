import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import execute_query

def render_page(conn):
    st.title("Scheduling")

    # Display current schedule
    st.header("Current Schedule")
    schedule_query = """
    SELECT l.name, s.event_type, s.start_time, s.end_time, s.description
    FROM schedules s
    JOIN locations l ON s.location_id = l.id
    WHERE s.start_time >= NOW()
    ORDER BY s.start_time
    """
    schedule = pd.DataFrame(execute_query(conn, schedule_query),
                            columns=['Location', 'Event Type', 'Start Time', 'End Time', 'Description'])
    st.dataframe(schedule)

    # Add new event
    st.header("Add New Event")
    locations = pd.DataFrame(execute_query(conn, "SELECT id, name FROM locations"), columns=['id', 'name'])
    
    location = st.selectbox("Location", locations['name'])
    event_type = st.selectbox("Event Type", ["Organ Retrieval", "Organ Transplant", "Inventory Check", "Staff Meeting"])
    start_time = st.date_input("Start Date")
    start_hour = st.time_input("Start Time", value=datetime.now().time())
    duration = st.number_input("Duration (hours)", min_value=1, max_value=24, value=2)
    description = st.text_area("Description")

    if st.button("Add Event"):
        start_datetime = datetime.combine(start_time, start_hour)
        end_datetime = start_datetime + timedelta(hours=duration)
        
        query = """
        INSERT INTO schedules (event_type, start_time, end_time, description, location_id)
        VALUES (%s, %s, %s, %s, (SELECT id FROM locations WHERE name = %s))
        """
        execute_query(conn, query, (event_type, start_datetime, end_datetime, description, location))
        st.success("Event added successfully!")

    # Simple delivery schedule
    st.header("Delivery Schedule")
    delivery_query = """
    SELECT l.name, i.item_name, i.quantity, s.start_time
    FROM schedules s
    JOIN locations l ON s.location_id = l.id
    JOIN inventory i ON l.id = i.location_id
    WHERE s.event_type = 'Organ Retrieval' AND s.start_time >= NOW()
    ORDER BY s.start_time
    """
    deliveries = pd.DataFrame(execute_query(conn, delivery_query),
                              columns=['Destination', 'Item', 'Quantity', 'Estimated Arrival'])
    st.dataframe(deliveries)
