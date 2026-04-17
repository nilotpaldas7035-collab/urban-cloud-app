import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE LOGIC ---
# This creates a local file named 'kitchen.db' to store your data
def init_db():
    conn = sqlite3.connect('kitchen.db', check_same_thread=False)
    c = conn.cursor()
    # Create Menu table
    c.execute('CREATE TABLE IF NOT EXISTS menu (item TEXT, price REAL)')
    # Create Orders table
    c.execute('CREATE TABLE IF NOT EXISTS orders (id TEXT, customer TEXT, items TEXT, total REAL, status TEXT)')
    
    # Add some starting items if the menu is empty
    c.execute('SELECT count(*) FROM menu')
    if c.fetchone()[0] == 0:
        sample_menu = [('Margherita Pizza', 299), ('Veg Burger', 149), ('Chocolate Cake', 450)]
        c.executemany('INSERT INTO menu VALUES (?,?)', sample_menu)
    conn.commit()
    return conn

conn = init_db()

# --- APP INTERFACE ---
st.title("👨‍🍳 Urban Cloud Kitchen")

tab1, tab2 = st.tabs(["🛍️ Order Food", "🔑 Admin Dashboard"])

with tab1:
    st.subheader("Menu")
    menu_data = pd.read_sql('SELECT * FROM menu', conn)
    
    with st.form("order_form"):
        name = st.text_input("Your Name")
        choices = st.multiselect("Pick your items", menu_data['item'].tolist())
        submit = st.form_submit_button("Place Order")
        
        if submit and name and choices:
            total = menu_data[menu_data['item'].isin(choices)]['price'].sum()
            order_id = datetime.now().strftime("%H%M%S")
            items_str = ", ".join(choices)
            
            # Save to the local database
            c = conn.cursor()
            c.execute('INSERT INTO orders VALUES (?,?,?,?,?)', (order_id, name, items_str, total, 'New'))
            conn.commit()
            st.success(f"Order #{order_id} placed! Total: ₹{total}")
            st.balloons()

with tab2:
    st.subheader("Kitchen Management")
    orders_data = pd.read_sql('SELECT * FROM orders', conn)
    st.dataframe(orders_data)
    
    if st.button("Clear All Orders"):
        conn.execute('DELETE FROM orders')
        conn.commit()
        st.rerun()

    st.divider()
    st.write("### Add New Menu Item")
    new_item = st.text_input("Item Name")
    new_price = st.number_input("Price", min_value=0)
    if st.button("Add to Menu"):
        conn.execute('INSERT INTO menu VALUES (?,?)', (new_item, new_price))
        conn.commit()
        st.success(f"Added {new_item} to menu!")
        st.rerun()
