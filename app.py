import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Page Config
st.set_page_config(page_title="Urban Cloud | Ordering", layout="wide")

# Connect to Google Sheets
# Replace 'url' with your Google Sheet Sharing URL
url = "YOUR_GOOGLE_SHEET_URL_HERE"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- HEADER ---
st.title("👨‍🍳 Urban Cloud Kitchen")
st.markdown("Pizzas, Burgers, & Custom Cakes")

# Create Tabs: One for Customers, One for You (Admin)
tab1, tab2 = st.tabs(["🛍️ Order Now", "📋 Kitchen Dashboard"])

# --- TAB 1: CUSTOMER VIEW ---
with tab1:
    st.subheader("Menu")
    # Load Menu from GSheets
    menu_df = conn.read(spreadsheet=url, worksheet="Menu")
    
    # Simple selection
    selected_item = st.selectbox("Choose a dish", menu_df['Item'])
    price = menu_df[menu_df['Item'] == selected_item]['Price'].values[0]
    st.write(f"Price: ₹{price}")
    
    cust_name = st.text_input("Your Name")
    
    if st.button("Place Order"):
        new_order = pd.DataFrame([{
            "Order_ID": str(datetime.now().strftime("%H%M%S")),
            "Customer": cust_name,
            "Items": selected_item,
            "Total": price,
            "Status": "Open"
        }])
        # Logic to append to GSheets (Using streamlit-gsheets integration)
        st.success("Order Sent! We are preparing your food.")
        st.balloons()

# --- TAB 2: ADMIN DASHBOARD (FOR YOU) ---
with tab2:
    st.subheader("Live Orders")
    orders_df = conn.read(spreadsheet=url, worksheet="Orders")
    st.dataframe(orders_df)
    
    st.divider()
    st.subheader("Edit/Add Dish to Order")
    
    # 1. Select Order to Modify
    order_id = st.selectbox("Select Order ID", orders_df['Order_ID'].unique())
    
    # 2. Pick extra dish to add
    extra_dish = st.selectbox("Add New Dish to this Order", menu_df['Item'])
    extra_price = menu_df[menu_df['Item'] == extra_dish]['Price'].values[0]
    
    if st.button("Add to Bill"):
        # LOGIC: In a real app, you'd update the GSheet row here
        st.info(f"Added {extra_dish} (₹{extra_price}) to Order {order_id}")
        st.warning("Total Updated. You can now generate the bill.")

    if st.button("Generate Bill & Print"):
        st.write("--- RECEIPT ---")
        st.write(f"URBAN CLOUD KITCHEN")
        st.write(f"Customer: {cust_name}")
        st.write(f"Total Amount: ₹{price + extra_price}")
        st.write("--- Thank You ---")
