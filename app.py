import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. PAGE SETTINGS ---
st.set_page_config(page_title="Urban Cloud Kitchen", page_icon="🍕", layout="centered")

# Custom CSS for a better look
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #ff4b4b; color: white; border: none; }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
def init_db():
    # Connect to local SQLite file
    conn = sqlite3.connect('urbancloud.db', check_same_thread=False)
    c = conn.cursor()
    # Create Menu table
    c.execute('CREATE TABLE IF NOT EXISTS menu (item TEXT, price REAL)')
    # Create Orders table
    c.execute('CREATE TABLE IF NOT EXISTS orders (id TEXT, customer TEXT, items TEXT, total REAL, status TEXT, timestamp TEXT)')
    
    # Check if menu is empty, if so, add default items
    c.execute('SELECT count(*) FROM menu')
    if c.fetchone()[0] == 0:
        default_items = [
            ('Wood-fired Margherita', 350.0),
            ('Chicken Burger', 180.0),
            ('Paneer Sandwich', 120.0),
            ('Customized Cake (1kg)', 1200.0)
        ]
        c.executemany('INSERT INTO menu VALUES (?,?)', default_items)
    conn.commit()
    return conn

conn = init_db()

# --- 3. THE APP INTERFACE ---
st.title("👨‍🍳 Urban Cloud Kitchen")
st.write("Guwahati's Premier Digital Kitchen")

tab1, tab2 = st.tabs(["🛍️ Order Online", "🔑 Admin Dashboard"])

# --- TAB 1: CUSTOMER ORDERING ---
with tab1:
    st.subheader("Place Your Order")
    
    # Load menu from database
    menu_df = pd.read_sql('SELECT * FROM menu', conn)
    
    if not menu_df.empty:
        with st.form("customer_order"):
            cust_name = st.text_input("Enter Your Name")
            selected_items = st.multiselect("Select Dishes", menu_df['item'].tolist())
            
            # Simple math for price display
            estimated_total = menu_df[menu_df['item'].isin(selected_items)]['price'].sum()
            st.write(f"### Total: ₹{estimated_total}")
            
            submit_btn = st.form_submit_button("Submit Order")
            
            if submit_btn:
                if cust_name and selected_items:
                    order_id = datetime.now().strftime("%H%M%S")
                    items_str = ", ".join(selected_items)
                    order_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # Insert into Database
                    c = conn.cursor()
                    c.execute('INSERT INTO orders VALUES (?,?,?,?,?,?)', 
                              (order_id, cust_name, items_str, estimated_total, 'Preparing', order_time))
                    conn.commit()
                    
                    st.success(f"Order #{order_id} received! We'll start cooking right away.")
                    st.balloons()
                else:
                    st.warning("Please enter your name and select at least one item.")
    else:
        st.info("The menu is empty. Please contact the kitchen.")

# --- TAB 2: MANISH'S ADMIN DASHBOARD ---
with tab2:
    st.subheader("Staff Login")
    
    # 🔒 Password Gate
    pwd = st.text_input("Enter Password", type="password")
    
    if pwd == "urban786": # Change this to your secret password
        st.success("Access Granted. Hi Manish!")
        
        # Display All Orders
        orders_df = pd.read_sql
