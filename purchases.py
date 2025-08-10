import streamlit as st
import database as db

def purchase_page():
    tab1, tab2 = st.tabs(["📥 Nhập hàng", "📜 Lịch sử nhập hàng"])
    with tab1:
        create_purchase_order()
    with tab2:
        view_purchase_history()

def create_purchase_order():
    st.subheader("📥 Tạo đơn nhập hàng")
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM products")
    products = c.fetchall()

    cart = []
    for p in products:
        qty = st.number_input(f"{p[1]} (Giá nhập: {p[2]} – Tồn: {p[3]})", min_value=0, key=f"purchase_qty_{p[0]}")
        if qty > 0:
            cart.append((p[0], p[1], p[2], qty))

    if st.button("💾 Lưu đơn nhập"):
        total = sum(item[2] * item[3] for item in cart)
        c.execute("INSERT INTO purchase_orders (total) VALUES (?)", (total,))
        order_id = c.lastrowid

        for item in cart:
            c.execute("INSERT INTO purchase_order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                      (order_id, item[0], item[3], item[2]))
            c.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (item[3], item[0]))

        conn.commit()
        st.success(f"✅ Đã lưu đơn nhập #{order_id} – Tổng tiền: {total}")
    conn.close()

def view_purchase_history():
    st.subheader("📜 Lịch sử nhập hàng")
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT id, total FROM purchase_orders ORDER BY id DESC")
    orders = c.fetchall()

    for order in orders:
        with st.expander(f"Đơn nhập #{order[0]} – Tổng tiền: {order[1]}"):
            c.execute("SELECT product_id, quantity, price FROM purchase_order_items WHERE order_id = ?", (order[0],))
            items = c.fetchall()
            for i in items:
                c.execute("SELECT name FROM products WHERE id = ?", (i[0],))
                name = c.fetchone()[0]
                st.write(f"{name} – SL: {i[1]} – Giá nhập: {i[2]}")

    conn.close()
