import streamlit as st
import database as db  # đổi tên module database của bạn

def products_page():
    st.title("📦 Quản lý sản phẩm")

    if "selected_product_id" not in st.session_state:
        st.session_state["selected_product_id"] = None
    if "edit_mode" not in st.session_state:
        st.session_state["edit_mode"] = False
    if "show_add_form" not in st.session_state:
        st.session_state["show_add_form"] = False  # trạng thái ẩn/hiện form thêm

    # --- Nút hiện/ẩn form thêm sản phẩm và form thêm ---
    if st.button("➕ Thêm sản phẩm mới"):
        st.session_state["show_add_form"] = not st.session_state["show_add_form"]

    if st.session_state["show_add_form"]:
        with st.form("add_product_form", clear_on_submit=True):
            name = st.text_input("Tên sản phẩm")
            price = st.number_input("Giá bán", min_value=0.0, step=1000.0, format="%.0f")
            stock = st.number_input("Tồn kho ban đầu", min_value=0, step=1)
            submit_add = st.form_submit_button("Thêm sản phẩm")

            if submit_add:
                if name and price > 0:
                    db.add_product(name, price, stock)
                    st.success("✅ Đã thêm sản phẩm thành công!")
                    st.session_state["show_add_form"] = False  # ẩn form sau khi thêm
                else:
                    st.error("❌ Vui lòng nhập đầy đủ thông tin.")

    container = st.empty()

    def show_products_list():
        products = db.get_products()
        st.subheader(f"📋 Danh sách sản phẩm ({len(products)})")

        for p in products:
            if st.button(f"{p[1]} (Giá: {p[2]:,.0f} VND, Tồn kho: {p[3]})", key=f"prod_{p[0]}"):
                st.session_state["selected_product_id"] = p[0]
                st.session_state["edit_mode"] = False
                st.session_state["show_add_form"] = False

    def show_product_detail(product_id):
        product = db.get_product_by_id(product_id)
        if not product:
            st.error("Không tìm thấy sản phẩm!")
            st.session_state["selected_product_id"] = None
            return

        st.header(f"Chi tiết sản phẩm: {product[1]}")

        if not st.session_state["edit_mode"]:
            st.write(f"**Tên:** {product[1]}")
            st.write(f"**Giá:** {product[2]:,.0f} VND")
            st.write(f"**Tồn kho:** {product[3]}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✏️ Chỉnh sửa"):
                    st.session_state["edit_mode"] = True
            with col2:
                if st.button("🔙 Quay về danh sách"):
                    st.session_state["selected_product_id"] = None
                    st.session_state["edit_mode"] = False

        else:
            new_name = st.text_input("Tên sản phẩm", value=product[1])
            new_price = st.number_input("Giá bán", min_value=0.0, step=1000.0, value=product[2], format="%.0f")
            new_stock = st.number_input("Tồn kho", min_value=0, step=1, value=product[3])

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Lưu thay đổi"):
                    db.update_product(product[0], new_name, new_price, new_stock)
                    st.success("✅ Đã cập nhật sản phẩm!")
                    st.session_state["edit_mode"] = False
            with col2:
                if st.button("❌ Hủy bỏ"):
                    st.session_state["edit_mode"] = False

    with container.container():
        if st.session_state["selected_product_id"] is None:
            show_products_list()
        else:
            show_product_detail(st.session_state["selected_product_id"])


if __name__ == "__main__":
    products_page()
