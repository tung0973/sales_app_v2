import streamlit as st
st.set_page_config(page_title="Quản lý kho hàng", page_icon="📦", layout="wide")

from database import init_db
import products
import sales
import purchases

# Khởi tạo database khi chạy app
init_db()

# Giao diện chính

# Menu chính ở sidebar
menu = ["📦 Quản lý sản phẩm", "🛒 Bán hàng", "📥 Nhập hàng"]
choice = st.sidebar.radio("Chọn chức năng:", menu)

if choice == "📦 Quản lý sản phẩm":
    products.products_page()

elif choice == "🛒 Bán hàng":
    sales.create_sales_order()

elif choice == "📥 Nhập hàng":
    purchases.purchase_page()

# Footer
st.sidebar.markdown("---")