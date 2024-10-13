import streamlit as st
import pandas as pd
from database import execute_query
import qrcode
import io

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def render_page(conn):
    st.title("Patient Management")

    # Display current patients
    st.header("Current Patients")
    patients_query = "SELECT id, name, age, blood_type, organ_needed, status FROM patients ORDER BY name"
    patients = pd.DataFrame(execute_query(conn, patients_query),
                            columns=['ID', 'Name', 'Age', 'Blood Type', 'Organ Needed', 'Status'])
    
    for index, row in patients.iterrows():
        st.write(f"{row['Name']} - Age: {row['Age']} - Blood Type: {row['Blood Type']} - Organ Needed: {row['Organ Needed']} - Status: {row['Status']}")
        qr_data = f"ID: {row['ID']}, Name: {row['Name']}, Age: {row['Age']}, Blood Type: {row['Blood Type']}, Organ Needed: {row['Organ Needed']}, Status: {row['Status']}"
        qr_code = generate_qr_code(qr_data)
        st.image(qr_code, caption=f"QR Code for {row['Name']}", width=200)

    # CRUD operations
    operation = st.radio("Select Operation", ["Add Patient", "Update Patient", "Delete Patient"])

    if operation == "Add Patient":
        st.header("Add New Patient")
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        organ_needed = st.selectbox("Organ Needed", ["None", "Heart", "Liver", "Kidney", "Lung", "Pancreas"])
        status = st.selectbox("Status", ["Waiting", "In Treatment", "Recovered"])

        if st.button("Add Patient"):
            query = """
            INSERT INTO patients (name, age, blood_type, organ_needed, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            execute_query(conn, query, (name, age, blood_type, organ_needed if organ_needed != "None" else None, status))
            st.success("Patient added successfully!")

    elif operation == "Update Patient":
        st.header("Update Patient")
        patient_to_update = st.selectbox("Select Patient to Update", patients['Name'])
        
        # Fetch current patient data
        current_data = patients[patients['Name'] == patient_to_update].iloc[0]
        
        name = st.text_input("Patient Name", value=current_data['Name'])
        age = st.number_input("Age", min_value=0, max_value=120, value=int(current_data['Age']))
        blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(current_data['Blood Type']))
        organ_needed = st.selectbox("Organ Needed", ["None", "Heart", "Liver", "Kidney", "Lung", "Pancreas"], index=["None", "Heart", "Liver", "Kidney", "Lung", "Pancreas"].index(current_data['Organ Needed'] if current_data['Organ Needed'] else "None"))
        status = st.selectbox("Status", ["Waiting", "In Treatment", "Recovered"], index=["Waiting", "In Treatment", "Recovered"].index(current_data['Status']))

        if st.button("Update Patient"):
            query = """
            UPDATE patients
            SET name = %s, age = %s, blood_type = %s, organ_needed = %s, status = %s
            WHERE name = %s
            """
            execute_query(conn, query, (name, age, blood_type, organ_needed if organ_needed != "None" else None, status, patient_to_update))
            st.success("Patient updated successfully!")

    elif operation == "Delete Patient":
        st.header("Delete Patient")
        patient_to_delete = st.selectbox("Select Patient to Delete", patients['Name'])

        if st.button("Delete Patient"):
            query = "DELETE FROM patients WHERE name = %s"
            execute_query(conn, query, (patient_to_delete,))
            st.success("Patient deleted successfully!")

    # Refresh the patient list after any operation
    st.rerun()
