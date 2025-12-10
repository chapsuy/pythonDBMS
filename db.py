import mariadb

def connect_db():
    try:
        conn = mariadb.connect(
            user="root",
            password="nin1234",
            host="localhost",     # or 127.0.0.1
            port=3306,
            database="inventoryDB"
        )
        return conn
    except mariadb.Error as e:
        print("Database connection failed:", e)
        return None


def get_products():
    conn = connect_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    conn.close()
    return rows