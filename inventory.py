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
    st.title("Inventory Management")

    # Display current inventory
    st.header("Current Inventory")
    inventory_query = """
    SELECT l.name as location, i.id, i.item_name, i.item_type, i.quantity, i.status
    FROM inventory i
    JOIN locations l ON i.location_id = l.id
    ORDER BY l.name, i.item_type, i.item_name
    """
    inventory = pd.DataFrame(execute_query(conn, inventory_query),
                             columns=['Location', 'ID', 'Item', 'Type', 'Quantity', 'Status'])
    
    for index, row in inventory.iterrows():
        st.write(f"{row['Item']} - {row['Type']} - Quantity: {row['Quantity']} - Status: {row['Status']}")
        qr_data = f"ID: {row['ID']}, Item: {row['Item']}, Type: {row['Type']}, Quantity: {row['Quantity']}, Status: {row['Status']}"
        qr_code = generate_qr_code(qr_data)
        st.image(qr_code, caption=f"QR Code for {row['Item']}", width=200)

    # Add new item to inventory
    st.header("Add New Item")
    locations = pd.DataFrame(execute_query(conn, "SELECT id, name FROM locations"), columns=['id', 'name'])
    
    location = st.selectbox("Location", locations['name'])
    item_name = st.text_input("Item Name")
    item_type = st.selectbox("Item Type", ["Organ", "Medical Supply", "Equipment"])
    quantity = st.number_input("Quantity", min_value=1, value=1)
    status = st.selectbox("Status", ["Available", "In Use", "Maintenance"])

    if st.button("Add Item"):
        query = """
        INSERT INTO inventory (item_name, item_type, quantity, status, location_id)
        VALUES (%s, %s, %s, %s, (SELECT id FROM locations WHERE name = %s))
        """
        execute_query(conn, query, (item_name, item_type, quantity, status, location))
        st.success("Item added successfully!")

    # Request and approval flow
    st.header("Inventory Requests")
    request_type = st.radio("Request Type", ["New Request", "Pending Approvals"])

    if request_type == "New Request":
        request_item = st.selectbox("Request Item", inventory['Item'].unique())
        request_quantity = st.number_input("Request Quantity", min_value=1, value=1)
        request_reason = st.text_area("Reason for Request")

        if st.button("Submit Request"):
            # In a real application, you'd save this request to a database
            # For this example, we'll just show a success message
            st.success("Request submitted successfully!")

    else:  # Pending Approvals
        # In a real application, you'd fetch pending requests from a database
        # For this example, we'll use dummy data
        pending_requests = pd.DataFrame({
            'Item': ['Surgical Masks', 'Gloves', 'Ventilator'],
            'Quantity': [1000, 500, 2],
            'Requester': ['Dr. Smith', 'Nurse Johnson', 'ICU Department'],
            'Reason': ['Low stock', 'Upcoming surgery', 'Equipment upgrade']
        })

        st.dataframe(pending_requests)

        request_to_approve = st.selectbox("Select Request to Approve", pending_requests['Item'])
        if st.button("Approve Request"):
            st.success(f"Request for {request_to_approve} approved!")

    # Material request and send flow
    st.header("Material Transfer")
    source_location = st.selectbox("Source Location", locations['name'], key="source")
    destination_location = st.selectbox("Destination Location", locations['name'], key="destination")
    transfer_item = st.selectbox("Item to Transfer", inventory['Item'].unique())
    transfer_quantity = st.number_input("Transfer Quantity", min_value=1, value=1)

    if st.button("Initiate Transfer"):
        # In a real application, you'd update the inventory in the database
        # For this example, we'll just show a success message
        st.success(f"Transfer of {transfer_quantity} {transfer_item}(s) from {source_location} to {destination_location} initiated!")
        st.info("Transfer status: In Transit")
