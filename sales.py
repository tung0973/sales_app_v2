import streamlit as st
import sqlite3
from datetime import datetime

def create_sales_order():
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()

    st.title("🛒 Tạo đơn bán hàng")

    # Khởi tạo giỏ hàng trong session_state
    if "cart" not in st.session_state:
        st.session_state.cart = []

    # --- Khách hàng ---
    c.execute("SELECT id, name FROM customers")
    customers = c.fetchall()
    customer_names = {f"{name} (ID {cid})": cid for cid, name in customers}

    add_new_customer = st.checkbox("➕ Thêm khách hàng mới")

    customer_id = None  # Khởi tạo biến customer_id

    if add_new_customer:
        st.subheader("Thêm khách hàng mới")
        new_name = st.text_input("Tên khách hàng")
        new_phone = st.text_input("Số điện thoại")
        new_address = st.text_input("Địa chỉ")

        if st.button("Lưu khách hàng mới"):
            if new_name.strip() == "":
                st.error("Vui lòng nhập tên khách hàng!")
            else:
                c.execute(
                    "INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)",
                    (new_name, new_phone, new_address),
                )
                conn.commit()
                st.success(f"Đã thêm khách hàng {new_name}")
                customer_id = c.lastrowid
                add_new_customer = False
    else:
        if customers:
            customer_choice = st.selectbox("Chọn khách hàng", list(customer_names.keys()))
            customer_id = customer_names.get(customer_choice)
        else:
            st.warning("Chưa có khách hàng nào, vui lòng thêm khách hàng mới.")
            conn.close()
            return

    # --- Sản phẩm ---
    c.execute("SELECT id, name, price, stock FROM products WHERE stock > 0")
    products = c.fetchall()
    product_dict = {f"{name} - Giá: {price} - Tồn: {stock}": (pid, price, stock) for pid, name, price, stock in products}

    if not product_dict:
        st.warning("Chưa có sản phẩm trong kho hoặc tất cả đều hết hàng.")
        conn.close()
        return

    selected_product = st.selectbox("Sản phẩm", list(product_dict.keys()))
    if selected_product is None:
        st.warning("Vui lòng chọn sản phẩm.")
        conn.close()
        return

    pid, price, stock = product_dict[selected_product]
    qty = st.number_input(f"Số lượng (Tồn: {stock})", min_value=1, max_value=stock, step=1)

    if st.button("Thêm vào giỏ hàng"):
        # Kiểm tra sản phẩm trong giỏ hàng
        exists = False
        for item in st.session_state.cart:
            if item["product_id"] == pid:
                if item["quantity"] + qty > stock:
                    st.error("Tổng số lượng vượt quá tồn kho!")
                    conn.close()
                    return
                item["quantity"] += qty
                exists = True
                break
        if not exists:
            st.session_state.cart.append({
                "product_id": pid,
                "name": selected_product.split(" - ")[0],
                "price": price,
                "quantity": qty
            })
        st.success(f"Đã thêm {qty} x {selected_product.split(' - ')[0]} vào giỏ hàng")

    # Hiển thị giỏ hàng
    st.subheader("Giỏ hàng")
    if st.session_state.cart:
        total = 0
        for item in st.session_state.cart:
            st.write(f"- {item['name']} x {item['quantity']} = {item['price'] * item['quantity']:,} VND")
            total += item['price'] * item['quantity']
        st.write(f"**Tổng tiền: {total:,} VND**")
    else:
        st.info("Giỏ hàng đang trống.")

    # Nhập tiền khách trả
    if st.session_state.cart:
        paid = st.number_input("Tiền khách trả", min_value=0.0, max_value=total, value=total, step=1000.0, format="%.0f")
        debt = total - paid
        st.write(f"**Công nợ: {debt:,} VND**")

        # Lưu đơn hàng
        if st.button("Lưu đơn hàng"):
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                "INSERT INTO sales_orders (customer_id, total, paid, debt, created_at) VALUES (?, ?, ?, ?, ?)",
                (customer_id, total, paid, debt, created_at)
            )
            order_id = c.lastrowid

            for item in st.session_state.cart:
                c.execute(
                    "INSERT INTO sales_order_details (sales_order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                    (order_id, item["product_id"], item["quantity"], item["price"])
                )
                c.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (item["quantity"], item["product_id"])
                )
            conn.commit()
            st.success(f"Đã lưu đơn hàng #{order_id}")

            # Xóa giỏ hàng sau khi lưu
            st.session_state.cart = []

    # --- Lịch sử đơn hàng gần đây ---
    st.subheader("📜 Lịch sử đơn bán gần đây")
    c.execute("""
        SELECT s.id, s.total, s.paid, s.debt, s.created_at, c.name
        FROM sales_orders s
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.created_at DESC
        LIMIT 10
    """)
    orders = c.fetchall()
    for order in orders:
        with st.expander(f"Đơn #{order[0]} | Khách: {order[5]} | Tổng: {order[1]:,} | Trả: {order[2]:,} | Nợ: {order[3]:,} | Ngày: {order[4]}"):
            c.execute("""
                SELECT p.name, d.quantity, d.price
                FROM sales_order_details d
                JOIN products p ON d.product_id = p.id
                WHERE d.sales_order_id = ?
            """, (order[0],))
            items = c.fetchall()
            for name, qty, price in items:
                st.write(f"- {name}: {qty} x {price:,} = {qty*price:,}")

    conn.close()
