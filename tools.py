from langchain_core.tools import tool
import sqlite3
#This tool is to check the inventory
@tool
def check_inventory(keyword: str) -> str:
    """Product ka naam ya keyword de kar stock, price, size, color check karo"""
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + keyword + '%',)) #like is used in sql to find matching text,and ? is the safe way to pass value in sql(save from hacking),'%' + keyword + '%' → % ka matlab hai "kuch bhi is se pehle/baad ho sakta hai" — matlab agar keyword "kurti" hai, to "Women Kurti" bhi match ho jayega
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return "i cannot find the required product."
    
    return str(results)
#This tool is made for the place order
@tool
def placeorder(customer_name: str, customer_phone: str, product_id: int, address:str, quantity: int) -> str:
    """Customer ka order database mein save karta hai. Naam, phone, product id, aur quantity chahiye."""
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (customer_name, customer_phone, product_id, address, quantity, status) VALUES (?, ?, ?, ?, ?,?)",
        (customer_name, customer_phone, product_id, address, quantity, "pending")
    )
    conn.commit()
    conn.close()
    return "Your Order is  successfully place!"
        