# --- TAB 2: MANISH'S ADMIN DASHBOARD ---
with tab2:
    st.subheader("Staff Login")
    
    # Using a key="admin_pwd" helps Streamlit track this specific box
    pwd = st.text_input("Enter Password", type="password", key="admin_pwd")
    
    if pwd == "urban786": 
        st.success("Access Granted. Hi Manish!")
        
        # We wrap this in an 'empty' container to help with smooth refreshing
        admin_container = st.container()
        
        with admin_container:
            orders_df = pd.read_sql('SELECT * FROM orders ORDER BY timestamp DESC', conn)
            
            st.write("### Active Orders")
            if not orders_df.empty:
                st.dataframe(orders_df, use_container_width=True)
                
                st.divider()
                st.write("### 📝 Modify an Order")
                # Add a unique key to every widget to prevent "Duplicate Widget" errors
                order_to_fix = st.selectbox("Select Order ID", orders_df['id'].tolist(), key="fix_id")
                item_to_add = st.selectbox("Add New Dish", menu_df['item'].tolist(), key="fix_item")
                
                if st.button("Add Item & Update Bill", key="add_btn"):
                    add_price = menu_df[menu_df['item'] == item_to_add]['price'].values[0]
                    c = conn.cursor()
                    c.execute('SELECT items, total FROM orders WHERE id=?', (order_to_fix,))
                    current_data = c.fetchone()
                    
                    new_items_list = current_data[0] + ", " + item_to_add
                    new_total = current_data[1] + add_price
                    
                    c.execute('UPDATE orders SET items=?, total=? WHERE id=?', (new_items_list, new_total, order_to_fix))
                    conn.commit()
                    st.toast(f"Updated Order {order_to_fix}!") # Small popup notification
                    st.rerun()

                if st.button("🗑️ Clear All Orders", key="clear_btn"):
                    c = conn.cursor()
                    c.execute('DELETE FROM orders')
                    conn.commit()
                    st.rerun()
            else:
                st.info("No orders found in the database.")
            
            st.divider()
            st.write("### ➕ Add Menu Item")
            m_item = st.text_input("New Dish Name", key="new_m_item")
            m_price = st.number_input("Dish Price", min_value=0.0, key="new_m_price")
            if st.button("Update Menu", key="update_m_btn"):
                if m_item:
                    c = conn.cursor()
                    c.execute('INSERT INTO menu VALUES (?,?)', (m_item, m_price))
                    conn.commit()
                    st.rerun()

    elif pwd != "":
        st.error("Access Denied. Please try again.")
