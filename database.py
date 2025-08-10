import sqlite3

DB_NAME = "inventory.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Bảng sản phẩm
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # Bảng khách hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
    ''')

    # Bảng đơn bán hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_code TEXT,
            total REAL NOT NULL,
            paid REAL DEFAULT 0,
            debt REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')

    # Chi tiết đơn bán hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales_order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sales_order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Đơn nhập hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Chi tiết đơn nhập hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchase_order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES purchase_orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    

    def get_sales_history_product(product_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT s.order_code, s.created_at, d.quantity, d.price
            FROM sales_order_details d
            JOIN sales_orders s ON d.sales_order_id = s.id
            WHERE d.product_id = ?
            ORDER BY s.created_at DESC
            LIMIT 20
        """, (product_id,))
        rows = c.fetchall()
        conn.close()
        return [
            {"order_code": r[0], "date": r[1], "qty": r[2], "price": r[3]} for r in rows
        ]   

    def get_purchase_history_product(product_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT p.order_code, p.created_at, d.quantity, d.price
            FROM purchase_order_items d
            JOIN purchase_orders p ON d.order_id = p.id
            WHERE d.product_id = ?
            ORDER BY p.created_at DESC
            LIMIT 20
        """, (product_id,))
        rows = c.fetchall()
        conn.close()
        return [
            {"order_code": r[0], "date": r[1], "qty": r[2], "price": r[3]} for r in rows
        ]

    conn.commit()
    conn.close()


# Ví dụ các hàm thao tác cơ bản

def add_product(name, price, stock):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    conn.commit()
    conn.close()

def get_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM products")
    rows = c.fetchall()
    conn.close()
    return rows

def update_product(product_id, name, price, stock):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (name, price, stock, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

# Hàm lấy lịch sử bán hàng đơn giản (có thể chỉnh theo app bạn)
def get_sales_history(start_date, end_date):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT s.id, s.order_code, s.created_at, c.name, s.total, s.paid, s.debt
        FROM sales_orders s
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE date(s.created_at) BETWEEN date(?) AND date(?)
        ORDER BY s.created_at DESC
    """, (start_date, end_date))
    orders = c.fetchall()

    sales_list = []
    for order in orders:
        order_id, order_code, created_at, customer_name, total, paid, debt = order
        c.execute("""
            SELECT p.name, d.quantity, d.price
            FROM sales_order_details d
            JOIN products p ON d.product_id = p.id
            WHERE d.sales_order_id = ?
        """, (order_id,))
        items = [{"name": name, "qty": qty, "price": price} for name, qty, price in c.fetchall()]

        sales_list.append({
            "order_code": order_code,
            "date": created_at,
            "customer": customer_name,
            "total": total,
            "paid": paid,
            "debt": debt,
            "items": items,
        })

    conn.close()
    return sales_list

def get_purchase_history(product_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT created_at as date, quantity, price
        FROM purchase_order_items i
        JOIN purchase_orders o ON i.order_id = o.id
        WHERE product_id = ?
        ORDER BY date DESC
    """, (product_id,))
    rows = c.fetchall()
    conn.close()
    return [{"date": r[0], "quantity": r[1], "price": r[2]} for r in rows]

def get_sales_history_by_product(product_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.created_at as date, d.quantity, d.price
        FROM sales_order_details d
        JOIN sales_orders s ON d.sales_order_id = s.id
        WHERE d.product_id = ?
        ORDER BY date DESC
    """, (product_id,))
    rows = c.fetchall()
    conn.close()
    return [{"date": r[0], "quantity": r[1], "price": r[2]} for r in rows]

def get_product_by_id(product_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()
    return product

import database  # file bạn lưu code DB ở đây

