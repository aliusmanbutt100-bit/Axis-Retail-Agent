# import sqlite3

# conn = sqlite3.connect("store.db")   # database file se connect (na ho to bana deta hai)
# cursor = conn.cursor()                # queries chalane ka "tool"

# cursor.execute("CREATE TABLE ...")    # normal SQL query, bas cursor.execute() mein daal do
# conn.commit()                         # changes save karna zaroori hai
# conn.close()                          # connection band karna
import sqlite3

conn = sqlite3.connect("store.db")
cursor = conn.cursor()
#create product table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    size TEXT,
    color TEXT,
    price REAL,
    stock_quantity INTEGER
)
""")
#create orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    customer_phone TEXT,
    product_id INTEGER,
    quantity INTEGER,
    address TEXT,
    status TEXT
)
""")
#i add address column later by this method bcz we cant add it directly we have to run it once
# cursor.execute("ALTER TABLE orders ADD COLUMN address TEXT")
conn.commit()
# #jaab data duplicate ho jai phir delete kar ky chalao
# cursor.execute("DELETE FROM products")
# conn.commit()
# #insert value in products table(terminal par run karliya means ye saab values database mei store ho gai hai toh abh ham inko comment out kardy gai,insert ko bs chala lo sahi sy phir comment out kardo bcz data chala jata hai jaab chalta hai)
# cursor.execute("""
# INSERT INTO products (name, category, size, color, price, stock_quantity)
# VALUES ('Men Polo Shirt', 'Shirt', 'M', 'Blue', 1500, 20)
# """)
# #now if we have more than one color of shirt then:
# cursor.execute("""
# INSERT INTO products (name, category, size, color, price, stock_quantity)
# VALUES ('Men Polo Shirt', 'Shirt', 'M', 'Red', 1500, 20)
# """)
# cursor.execute("""
# INSERT INTO products (name, category, size, color, price, stock_quantity)
# VALUES ('Women Kurti', 'Kurti', 'L', 'Red', 2000, 15)
# """)

# cursor.execute("""
# INSERT INTO products (name, category, size, color, price, stock_quantity)
# VALUES ('Men Jeans', 'Pant', 'XL', 'Black', 3500, 10)
# """)

# cursor.execute("""
# INSERT INTO products (name, category, size, color, price, stock_quantity)
# VALUES ('Kids T-Shirt', 'Shirt', 'S', 'Yellow', 800, 25)
# """)
# #same as above more products
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Men Formal Shirt', 'Shirt', 'L', 'White', 1800, 12)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Women Abaya', 'Abaya', 'M', 'Black', 4500, 8)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Men Kurta', 'Kurta', 'L', 'Grey', 2200, 18)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Women Lawn Suit', 'Suit', 'M', 'Pink', 3200, 14)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Men Trouser', 'Pant', 'L', 'Navy', 2500, 20)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Women Scarf', 'Accessory', 'One Size', 'Maroon', 900, 30)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Kids Frock', 'Frock', 'S', 'Purple', 1500, 16)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Men Hoodie', 'Hoodie', 'XL', 'Black', 3000, 9)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Women Heels', 'Shoes', '38', 'Beige', 2800, 7)")
# cursor.execute("INSERT INTO products (name, category, size, color, price, stock_quantity) VALUES ('Kids Sneakers', 'Shoes', '30', 'White', 1700, 22)")

# conn.commit()
# cursor.execute("select * from products ")
# print(cursor.fetchall())
# #To see only all names of the table
# cursor.execute("SELECT name FROM products")
# print(cursor.fetchall())
# To check our tables in database
# import sqlite3

# conn = sqlite3.connect("store.db")
# cursor = conn.cursor()

# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor.fetchall())

# conn.close()

#TO check that the later address column that we add is added or not
# cursor.execute("PRAGMA table_info(orders)")
# print(cursor.fetchall())