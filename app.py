import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. PAGE SETTINGS ---
st.set_page_config(page_title="Urban Cloud Kitchen", layout="centered")

# --- 2. DATABASE INITIALIZATION (WITH SAFETY) ---
def init_db():
    try:
        # 'timeout' prevents the "Script Execution Error" during busy times
        conn = sqlite3.connect('urbancloud.db', check_same_thread=False, timeout=20)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS menu (item TEXT, price REAL)')
        c.execute('CREATE TABLE IF NOT EXISTS orders (id TEXT, customer TEXT, items TEXT, total REAL, status TEXT, timestamp TEXT)')
        
        c.execute('SELECT count(*) FROM menu')
        if c.fetchone()[0] == 0:
            default_items = [('Margherita Pizza', 350.0), ('Chicken Burger', 180.0)]
            c.executemany('INSERT INTO menu VALUES (?,?)', default_items)
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Database Initialization Failed: {e}")
        return None

conn = init_db()

# --- 3. THE APP ---
st.title("👨‍🍳 Urban Cloud Kitchen")

if conn is not None:
    tab1, tab2 = st.tabs(["🛍️ Order Now", "🔑 Admin"])

    with tab1:
        try:
            menu_df = pd.read_sql('SELECT * FROM menu', conn)
            with st.form("order_form"):
                name = st.text_input("Name")
                items = st.multiselect("Dishes", menu_df['item'].tolist())
                if st.form_submit_button("Place Order"):
                    if name and items:
                        total = menu_df[menu_df['item'].isin(items)]['price'].sum()
                        order_id = datetime.now().strftime("%H%M%S")
                        c = conn.cursor()
                        c.execute('INSERT INTO orders VALUES (?,?,?,?,?,?)', 
                                  (order_id, name, ", ".join(items), total, 'New', datetime.now().strftime("%H:%M")))
                        conn.commit()
                        st.success(f"Order #{order_id} Placed!")
        except Exception as e:
            st.error(f"Order Error: {e}")

    with tab2:
        pwd = st.text_input("Password", type="password")
        if pwd == "urban786":
            try:
                orders = pd.read_sql('SELECT * FROM orders', conn)
                st.dataframe(orders)
                if st.button("Clear All"):
                    conn.execute('DELETE FROM orders')
                    conn.commit()
                    st.rerun()
            except Exception as e:
                st.error(f"Admin View Error: {e}")
else:
    st.warning("The app is having trouble connecting to its internal database. Please reboot the app from the Streamlit Dashboard.")
