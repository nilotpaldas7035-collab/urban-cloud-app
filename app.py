import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Urban Cloud Kitchen", layout="centered")

def init_db():
    conn = sqlite3.connect('urbancloud.db', check_same_thread=False, timeout=20)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS menu (item TEXT, price REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS orders (id TEXT, customer TEXT, items TEXT, total REAL, status TEXT, timestamp TEXT)')
    conn.commit()
    return conn

conn = init_db()

st.title("👨‍🍳 Urban Cloud Kitchen")

tab1, tab2 = st.tabs(["🛍️ Customer Menu", "🔑 Admin (Manish)"])

with tab1:
    menu_df = pd.read_sql('SELECT * FROM menu', conn)
    if menu_df.empty:
        st.info("The menu is empty. Manish, please add items in the Admin tab!")
    else:
        with st.form("order_form"):
            name = st.text_input("Customer Name")
            items = st.multiselect("Select Dishes", menu_df['item'].tolist())
            if st.form_submit_button("Place Order"):
                if name and items:
                    total = menu_df[menu_df['item'].isin(items)]['price'].sum()
                    order_id = datetime.now().strftime("%H%M%S")
                    conn.execute('INSERT INTO orders VALUES (?,?,?,?,?,?)', 
                                (order_id, name, ", ".join(items), total, 'New', datetime.now().strftime("%H:%M")))
                    conn.commit()
                    st.success(f"Order #{order_id} Placed!")

with tab2:
    pwd = st.text_input("Admin Password", type="password")
    if pwd == "urban786":
        st.success("Welcome, Manish!")
        
        # --- SECTION 1: MANAGE MENU ---
        st.subheader("🍱 Manage Your Menu")
        col1, col2 = st.columns(2)
        with col1:
            m_item = st.text_input("Dish Name (e.g. Cheese Pizza)")
        with col2:
            m_price = st.number_input("Price (₹)", min_value=0.0)
            
        if st.button("➕ Add to Menu"):
            if m_item:
                conn.execute('INSERT INTO menu VALUES (?,?)', (m_item, m_price))
                conn.commit()
                st.rerun()

        # Show current menu with a delete option
        current_menu = pd.read_sql('SELECT * FROM menu', conn)
        if not current_menu.empty:
            st.write("Current Menu:")
            st.table(current_menu)
            item_to_del = st.selectbox("Select item to remove", current_menu['item'].tolist())
            if st.button("🗑️ Delete Selected Item"):
                conn.execute('DELETE FROM menu WHERE item=?', (item_to_del,))
                conn.commit()
                st.rerun()

        st.divider()

        # --- SECTION 2: LIVE ORDERS ---
        st.subheader("📋 Live Orders")
        orders = pd.read_sql('SELECT * FROM orders', conn)
        st.dataframe(orders)
        if st.button("🗑️ Clear All Orders"):
            conn.execute('DELETE FROM orders')
            conn.commit()
            st.rerun()
