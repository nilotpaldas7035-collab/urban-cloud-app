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
    .stButton>button { width: 100%; border-radius: 10px; background-color: #ff4b4b; color: white; border: none; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('urbancloud.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS menu (item TEXT, price REAL)')
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
st.caption("Guwahati | Pizzas • Burgers • Cakes")

# Create the two main tabs
tab1, tab2 = st.tabs(["🛍️ Order Online", "🔑 Admin Dashboard"])

# --- TAB 1: CUSTOMER VIEW ---
with tab1:
    st.subheader("Place Your Order")
    menu_df = pd.read_sql('SELECT * FROM menu', conn)
    
    if not menu_df.empty:
        with st.form("customer_order_form"):
            cust_name = st.text_input("Enter Your Name", key="user_name")
            selected_items = st.multiselect("Select Dishes", menu_df['item'].tolist(), key="user_selection")
            
            total_calc = menu_df[menu_df['item'].isin(selected_items)]['price'].sum()
            st.write(f"### Estimated Bill: ₹{total_calc}")
            
            submit_btn = st.form_submit_button("Submit Order")
            
            if submit_btn:
                if cust_name and selected_items:
                    order_id = datetime.now().strftime("%H%M%S")
                    items_str = ", ".join(selected_items)
                    order_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    c = conn.cursor()
                    c.execute('INSERT INTO orders VALUES (?,?,?,?,?,?)', 
                              (order_id, cust_name, items_str, total_calc, 'Preparing', order_time))
                    conn.commit()
                    
                    st.success(f"Order #{order_id} received! Check with us for pickup/delivery.")
                    st.balloons()
                else:
                    st.warning("Please provide your name and pick at least one item!")
    else:
        st.info("Menu is currently empty.")

# --- TAB 2: ADMIN DASHBOARD (FOR MANISH) ---
with tab2:
    st.subheader("Staff Access")
    
    # Password Input
    # Note: You must press ENTER after typing the password
    admin_pwd = st.text_input("Enter Admin Password", type="password", key="admin_access_pwd")
    
    if admin_pwd == "urban786":
        st.success("Welcome, Manish! Access Granted.")
        st.divider()

        # Load fresh orders
        orders_df = pd.read_sql('SELECT * FROM orders ORDER BY timestamp DESC', conn)
        
        if not orders_df.empty:
            st.write("### Live Order List")
            st.dataframe(orders_df, use_container_width=True)
            
            st.divider()
            
            # --- MODIFY ORDER SECTION ---
            st.write("### 📝 Edit Existing Order")
            col1, col2 = st.columns(2)
            
            with col1:
                order_to_fix = st.selectbox("Order ID", orders_df['id'].tolist(), key="mod_order_id")
            with col2:
                item_to_add = st.selectbox("Dish to Add", menu_df['item'].tolist(), key="mod_item_name")
            
            if st.button("Add Item & Recalculate Total", key="mod_btn"):
                # Get item price
                add_price = menu_df[menu_df['item'] == item_to_add]['price'].values[0]
                
                # Get current data
                c = conn.cursor()
                c.execute('
