import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Urban Cloud Kitchen", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE CONNECTION ---
# Your specific Google Sheet link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1KOluGnPsB518wJMvhTKZVNZessmJlsTioUxpbgv19_E/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Connection Error: Please check your requirements.txt for 'st-gsheets-connection'")

# --- APP LAYOUT ---
st.title("👨‍🍳 Urban Cloud")
st.caption("Guwahati's Finest Wood-fired Pizzas, Burgers & Cakes")

tab1, tab2 = st.tabs(["🛍️ Place Order", "⚙️ Admin Dashboard"])

# --- TAB 1: CUSTOMER ORDERING ---
with tab1:
    try:
        # Load Menu Data
        menu_df = conn.read(spreadsheet=SHEET_URL, worksheet="Menu", ttl=0)
        
        if not menu_df.empty:
            st.subheader("Our Menu")
            
            # Form for ordering
            with st.form("order_form"):
                cust_name = st.text_input("Customer Name", placeholder="Enter your name")
                selected_items = st.multiselect("Select Dishes", menu_df['Item'].tolist())
                
                # Calculate simple total for display
                total_price = menu_df[menu_df['Item'].isin(selected_items)]['Price'].sum()
                st.write(f"### Estimated Total: ₹{total_price}")
                
                submitted = st.form_submit_button("Confirm Order")
                
                if submitted:
                    if cust_name and selected_items:
                        # Prepare data for Google Sheets
                        new_order = pd.DataFrame([{
                            "Order_ID": datetime.now().strftime("%d%m-%H%M"),
                            "Customer": cust_name,
                            "Items": ", ".join(selected_items),
                            "Total": total_price,
                            "Status": "Received"
                        }])
                        
                        # Append to 'Orders' sheet
                        existing_orders = conn.read(spreadsheet=SHEET_URL, worksheet="Orders", ttl=0)
                        updated_orders = pd.concat([existing_orders, new_order], ignore_index=True)
                        conn.update(spreadsheet=SHEET_URL, worksheet="Orders", data=updated_orders)
                        
                        st.success(f"Order Placed! Order ID: {new_order['Order_ID'][0]}")
                        st.balloons()
                    else:
                        st.warning("Please enter your name and select at least one item.")
        else:
            st.info("The menu is currently empty. Add items to the Google Sheet 'Menu' tab.")
            
    except Exception as e:
        st.error(f"Error loading menu: {e}")

# --- TAB 2: KITCHEN ADMIN (FOR MANISH) ---
with tab2:
    st.subheader("Manage Orders")
    
    try:
        orders_df = conn.read(spreadsheet=SHEET_URL, worksheet="Orders", ttl=0)
        
        if not orders_df.empty:
            # Display current orders
            st.dataframe(orders_df, use_container_width=True)
            
            st.divider()
            st.write("### ➕ Add Extra Items / Generate Bill")
            
            selected_id = st.selectbox("Select Order to Modify", orders_df['Order_ID'].tolist())
            extra_item = st.selectbox("Select Item to Add", menu_df['Item'].tolist())
            
            if st.button("Add to Order & Update Bill"):
                # Logic: Find row, add item to text, add price to total
                item_price = menu_df[menu_df['Item'] == extra_item]['Price'].values[0]
                
                # Update logic in the dataframe
                idx = orders_df[orders_df['Order_ID'] == selected_id].index[0]
                orders_df.at[idx, 'Items'] = f"{orders_df.at[idx, 'Items']}, {extra_item}"
                orders_df.at[idx, 'Total'] = orders_df.at[idx, 'Total'] + item_price
                
                # Push back to Sheets
                conn.update(spreadsheet=SHEET_URL, worksheet="Orders", data=orders_df)
                st.success(f"Added {extra_item} to Order {selected_id}!")
                st.rerun()
                
            if st.button("Download PDF Bill (Concept)"):
                st.write("Printing bill for:", selected_id)
                # You can add FPDF library logic here later
        else:
            st.write("No active orders.")
            
    except Exception as e:
        st.error(f"Admin Error: {e}")
