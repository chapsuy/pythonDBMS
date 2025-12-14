import mariadb
import datetime
import calendar 

# --- Connection Function ---
def connect_db():
    try:
        conn = mariadb.connect(
            user="root",
            password="nin1234",
            host="localhost",    
            port=3306,
            database="inventorydb"
        )
        return conn
    except mariadb.Error as e:
        print("Database connection failed:", e)
        return None


def check_user_credentials(username):
    # This function should retrieve the HASHED password from the DB.
    conn = connect_db()
    if not conn:
        return None 
    cursor = conn.cursor()
    # Select only the username and password field
    cursor.execute("SELECT password FROM User WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None # Returns the stored password (hash)


# --- PRODUCT FUNCTIONS ---

def get_products():
    """Fetches all product records, converting price to float."""
    conn = connect_db() 
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, price, stock FROM products")
    result = cursor.fetchall()
    conn.close()
    
    # FIX: Convert Decimal price to float for consistency in application
    formatted_result = []
    for product_id, name, price, stock in result:
        formatted_result.append((product_id, name, float(price), stock))
    return formatted_result


def handle_add_or_update(name, price, stock):
    """Checks if product exists, updates stock/price, or inserts new product."""
    conn = connect_db()
    if not conn:
        return "Database connection failed.", False
        
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT product_id, stock FROM products WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result:
            product_id, current_stock = result
            new_stock = current_stock + stock 
            cursor.execute(
                "UPDATE products SET price = ?, stock = ? WHERE product_id = ?", 
                (price, new_stock, product_id)
            )
            conn.commit()
            return f"Product '{name}' already exists. Stock updated from {current_stock} to {new_stock}.", True
        else:
            cursor.execute(
                "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                (name, price, stock)
            )
            conn.commit()
            return f"Product '{name}' added successfully.", True

    except Exception as e:
        conn.rollback()
        return f"Database Error during Add/Update: {e}", False
    finally:
        if conn:
            conn.close()

def update_product(product_id, name, price, stock):
    """Updates the details of an existing product."""
    conn = connect_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE products SET name = ?, price = ?, stock = ? WHERE product_id = ?",
            (name, price, stock, product_id)
        )
        conn.commit()
        return True
    except mariadb.Error as e:
        print(f"Update error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_product(product_id):
    """Deletes a product by ID."""
    conn = connect_db()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount > 0
    except mariadb.Error as e:
        return False
    finally:
        if conn:
            conn.close()


# --- ORDER MANAGEMENT FUNCTIONS ---

def get_orders():
    """Fetches all order headers, formatting the date and total amount."""
    conn = connect_db()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT order_id, customer_name, order_date, total_amount, payment_status FROM order_header ORDER BY order_date DESC")
    result = cursor.fetchall()
    
    formatted_result = []
    for order_id, customer_name, order_date, total_amount, payment_status in result:
        order_date_str = order_date.strftime("%Y-%m-%d %H:%M") if isinstance(order_date, datetime.datetime) else str(order_date)
        formatted_result.append((
            order_id, 
            customer_name, 
            order_date_str, 
            f"{float(total_amount):.2f}", # FIX: Convert to float for display formatting
            payment_status
        ))
        
    conn.close()
    return formatted_result
    
def get_order_items(order_id):
    """Fetches all items belonging to a specific order ID."""
    conn = connect_db()
    if not conn:
        return []
        
    cursor = conn.cursor()
    # FIX: Changed oi.item_id to oi.order_item_id to match the table schema
    try:
        cursor.execute("""
            SELECT 
                oi.order_item_id,  -- <--- **THIS IS THE FIX**
                p.name, 
                oi.quantity, 
                oi.price_at_sale 
            FROM 
                order_items oi
            JOIN 
                products p ON oi.product_id = p.product_id
            WHERE 
                oi.order_id = ?
        """, (order_id,))
        result = cursor.fetchall()
        return result
        
    except mariadb.Error as e:
        print(f"Error fetching order items: {e}")
        return []
        
    finally:
        if conn:
            conn.close()

def create_new_order(customer_name, order_items_list):
    """Creates new order, calculates total, updates stock, and commits atomically."""
    conn = connect_db()
    if not conn:
        return None, "Database connection failed."

    cursor = conn.cursor()
    
    try:
        # 1. Create Order Header 
        cursor.execute(
            "INSERT INTO order_header (customer_name) VALUES (?)",
            (customer_name,)
        )
        order_id = cursor.lastrowid
        total_amount = 0.0
        
        # 2. Add Order Items and Calculate Total
        for product_id, quantity in order_items_list:
            # Get current product price and stock
            cursor.execute("SELECT price, stock FROM products WHERE product_id=?", (product_id,))
            product_data = cursor.fetchone()
            
            if not product_data:
                raise Exception(f"Product ID {product_id} not found.")

            # FIX: Convert price (Decimal) to float immediately for safe calculations
            price = float(product_data[0]) 
            current_stock = product_data[1]
            
            if quantity > current_stock:
                conn.rollback() 
                return None, f"Insufficient stock for Product ID {product_id}. Available: {current_stock}, Requested: {quantity}."
                
            line_total = price * quantity
            total_amount += line_total
            
            # Insert item into order_items
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price_at_sale) VALUES (?, ?, ?, ?)",
                (order_id, product_id, quantity, price)
            )
            
            # Reduce stock immediately
            new_stock = current_stock - quantity
            cursor.execute(
                "UPDATE products SET stock=? WHERE product_id=?",
                (new_stock, product_id)
            )

        # 3. Update Order Header with Final Total and set to 'Paid'
        cursor.execute(
            "UPDATE order_header SET total_amount=?, payment_status='Paid' WHERE order_id=?",
            (total_amount, order_id)
        )
        
        conn.commit()
        return order_id, f"Order {order_id} placed and Paid (stock reduced)."
        
    except mariadb.Error as e:
        conn.rollback()
        return None, f"Database Error: {e}"
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        if conn:
            conn.close()


def update_payment_status(order_id, new_status):
    """Updates the payment status of an order."""
    if new_status not in ['Pending', 'Paid', 'Cancelled']:
        return False, "Invalid status."

    conn = connect_db()
    if not conn:
        return False, "Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE order_header SET payment_status=? WHERE order_id=?",
            (new_status, order_id)
        )
        conn.commit()
        return True, f"Order {order_id} status updated to {new_status}."
    except mariadb.Error as e:
        return False, f"Database error: {e}"
    finally:
        if conn:
            conn.close()


def delete_order(order_id):
    """Deletes an order and handles related stock adjustments."""
    conn = connect_db()
    if not conn:
        return False, "Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT payment_status FROM order_header WHERE order_id=?", (order_id,))
        status_row = cursor.fetchone()
        
        if status_row and status_row[0] == 'Paid':
            cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id=?", (order_id,))
            items = cursor.fetchall()
            
            for product_id, quantity in items:
                cursor.execute(
                    "UPDATE products SET stock = stock + ? WHERE product_id = ?",
                    (quantity, product_id)
                )
        
        cursor.execute("DELETE FROM order_header WHERE order_id=?", (order_id,))
        conn.commit()
        return True, f"Order {order_id} deleted successfully (stock adjusted)."
        
    except mariadb.Error as e:
        conn.rollback()
        return False, f"Error deleting order: {e}"
    finally:
        if conn:
            conn.close()


# --- INCOME REPORTING FUNCTIONS ---
    
def get_income_summary(date_range_days=30):
    conn = connect_db()
    if not conn:
        return {'total_sales': 0.0, 'last_30_days': 0.0}
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(total_amount) FROM order_header WHERE payment_status = 'Paid'")
    total_sales = cursor.fetchone()[0] or 0.0
    
    thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=date_range_days)
    cursor.execute(
        "SELECT SUM(total_amount) FROM order_header WHERE order_date >= ? AND payment_status = 'Paid'",
        (thirty_days_ago,)
    )
    last_30_days = cursor.fetchone()[0] or 0.0

    conn.close()
    
    return {
        'total_sales': float(total_sales),
        'last_30_days': float(last_30_days)
    }

def get_income_report_details():
    conn = connect_db()
    if not conn:
        return []
    cursor = conn.cursor()
    
    sixty_days_ago = datetime.datetime.now() - datetime.timedelta(days=60)
    cursor.execute("""
        SELECT 
            DATE_FORMAT(order_date, '%Y-%m-%d') AS date_period, 
            COUNT(order_id), 
            SUM(total_amount)
        FROM order_header
        WHERE order_date >= ? AND payment_status = 'Paid'
        GROUP BY date_period
        ORDER BY date_period DESC
    """, (sixty_days_ago,))
    
    details = []
    for row in cursor.fetchall():
        date_period, count, income = row
        details.append((date_period, count, f"{float(income):.2f}"))

    conn.close()
    return details

def get_income_report():
    summary = get_income_summary()
    details = get_income_report_details()
    
    return {
        'total_sales': summary['total_sales'],
        'last_30_days': summary['last_30_days'],
        'details': details
    }