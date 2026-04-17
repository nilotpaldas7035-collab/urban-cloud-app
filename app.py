import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Basic setup for Urban Cloud
st.set_page_config(page_title="Urban Cloud Kitchen", layout="centered")

# The clean link to your sheet
URL = "https://docs.google.com/spreadsheets/d/1KOluGnPsB518wJMvhTKZVNZessmJlsTioUxpbgv19_E/edit#gid=0"

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("👨‍🍳 Urban Cloud")
st.write("Guwahati's Cloud Kitchen")

# Tab navigation
tab1, tab2 = st.tabs(["🛍️ Customer Menu", "🔑 Admin (Manish)"])

# --- CUSTOMER MENU ---
with tab1:
    try:
        # Load the Menu tab
        # We add 'ttl=0' to make sure it always shows the newest items
        df = conn.read(spreadsheet=URL, worksheet="Menu", ttl=0)
        
        if not df.empty:
            st.subheader("Order Food")
            name = st.text_input("Your Name")
            item_list = df['Item'].tolist()
            choice = st.multiselect("Select your items", item_list)
            
            if st.button("Submit Order"):
                if name and choice:
                    # Create a simple order record
                    order_data = pd.DataFrame([{
                        "Order_ID": datetime.now().strftime("%H%M%S"),
                        "Customer": name,
                        "Items": ", ".join(choice),
                        "Total": df[df['Item'].isin(choice)]['Price'].sum(),
                        "Status": "Pending"
                    }])
                    
                    # Update the 'Orders' tab
                    existing = conn.read(spreadsheet=URL, worksheet="Orders", ttl=0)
                    updated = pd.concat([existing, order_data], ignore_index=True)
                    conn.update(spreadsheet=URL, worksheet="Orders", data=updated)
                    
                    st.success(f"Order placed! Your ID is {order_data['Order_ID'][0]}")
                    st.balloons()
        else:
            st.warning("Menu is empty. Add items to your Google Sheet.")
            
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        st.info("Check if your Sheet tab is named exactly 'Menu' and 'Orders'")

# --- ADMIN DASHBOARD ---
with tab2:
    st.subheader("Manage Kitchen")
    if st.button("🔄 Refresh Orders"):
        st.rerun()
        
    try:
        orders = conn.read(spreadsheet=URL, worksheet="Orders", ttl=0)
        st.write("Live Orders:")
        st.dataframe(orders)
        
        # Simple Logic to Add New Items manually
        st.divider()
        order_to_edit = st.selectbox("Select Order ID to Modify", orders['Order_ID'].unique() if not orders.empty else ["None"])
        add_item = st.selectbox("Add New Dish to this order", df['Item'].tolist() if not df.empty else ["None"])
        
        if st.button("Add Item & Update Bill"):
            st.write(f"Adding {add_item} to {order_to_edit}...")
            # Note: More advanced logic to save this back can be added as you grow!
            
    except:
        st.write("No orders yet or Sheet Error.")

# --- HELP SECTION ---
with st.sidebar:
    st.write("### Troubleshooting")
    if st.button("Clear App Memory"):
        st.cache_data.clear()
        st.success("Memory Cleared!")
