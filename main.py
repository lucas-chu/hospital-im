import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

import database as db
import map_utils

# Initialize the database connection
conn = db.create_connection()

# Set page config
st.set_page_config(page_title="Hospital Inventory Platform", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Organ Management", "Scheduling", "Inventory", "Patient Management"])

if page == "Home":
    st.title("Hospital Inventory Platform")
    st.write("Welcome to the comprehensive Hospital Inventory Platform.")

    # Display list of locations
    st.header("Hospital and Organ Donation Center Locations")
    locations_df = map_utils.get_locations(conn)
    st.dataframe(locations_df)

    # Display key statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Hospitals", db.get_total_hospitals(conn))
    with col2:
        st.metric("Total Organ Donation Centers", db.get_total_donation_centers(conn))
    with col3:
        st.metric("Organs Available", db.get_total_available_organs(conn))

elif page == "Organ Management":
    import organ_management
    organ_management.render_page(conn)

elif page == "Scheduling":
    import scheduling
    scheduling.render_page(conn)

elif page == "Inventory":
    import inventory
    inventory.render_page(conn)

elif page == "Patient Management":
    import patient_management
    patient_management.render_page(conn)

# Close the database connection
db.close_connection(conn)
