import streamlit as st
import pandas as pd
from database import execute_query

def render_page(conn):
    st.title("Organ Management")

    # Organ Donation Form
    st.header("Register Organ Donation")
    donor_name = st.text_input("Donor Name")
    organ_type = st.selectbox("Organ Type", ["Heart", "Liver", "Kidney", "Lung", "Pancreas"])
    blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
    
    if st.button("Register Donation"):
        # Add organ to inventory
        query = """
        INSERT INTO inventory (item_name, item_type, quantity, status, location_id)
        VALUES (%s, 'Organ', 1, 'Available', 
                (SELECT id FROM locations WHERE type = 'Donation Center' ORDER BY RANDOM() LIMIT 1))
        """
        execute_query(conn, query, (f"{organ_type} ({blood_type})",))
        st.success("Organ donation registered successfully!")

    # Waitlist Management
    st.header("Organ Waitlist")
    waitlist_query = """
    SELECT name, age, blood_type, organ_needed, status 
    FROM patients 
    WHERE status = 'Waiting' 
    ORDER BY age DESC
    """
    waitlist = pd.DataFrame(execute_query(conn, waitlist_query), 
                            columns=['Name', 'Age', 'Blood Type', 'Organ Needed', 'Status'])
    st.dataframe(waitlist)

    # Organ Matching
    st.header("Organ Matching")
    if st.button("Run Matching Algorithm"):
        # Simple matching algorithm (can be improved)
        available_organs = pd.DataFrame(
            execute_query(conn, "SELECT id, item_name FROM inventory WHERE item_type = 'Organ' AND status = 'Available'"),
            columns=['id', 'organ']
        )
        
        for _, organ in available_organs.iterrows():
            organ_type, blood_type = organ['organ'].split(' (')
            blood_type = blood_type[:-1]  # Remove closing parenthesis
            
            match_query = """
            SELECT id FROM patients 
            WHERE status = 'Waiting' 
            AND organ_needed = %s 
            AND blood_type = %s 
            ORDER BY age DESC 
            LIMIT 1
            """
            match = execute_query(conn, match_query, (organ_type, blood_type))
            
            if match:
                patient_id = match[0][0]
                execute_query(conn, "UPDATE patients SET status = 'Matched' WHERE id = %s", (patient_id,))
                execute_query(conn, "UPDATE inventory SET status = 'Assigned' WHERE id = %s", (organ['id'],))
                st.success(f"Matched {organ_type} ({blood_type}) to a patient!")
            else:
                st.info(f"No match found for {organ_type} ({blood_type})")

        st.success("Matching complete!")
