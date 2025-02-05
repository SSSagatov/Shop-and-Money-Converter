import sqlite3



def init_db():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY, 
                        name TEXT, 
                        price INTEGER, 
                        description TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cart (
                        user_id INTEGER, 
                        product_id INTEGER)''')
    conn.commit()
    conn.close()

def add_products():
    products = [
        ('Lenovo IdeaPad 3', 500, 'Бюджетный ноутбук с 8ГБ ОЗУ и SSD 256ГБ'),
        ('ASUS VivoBook 15', 700, 'Легкий и стильный, Intel i5, 512GB SSD'),
        ('MacBook Air M1', 1200, 'Производительный M1 чип, 8GB RAM, 256GB SSD'),
        ('HP Pavilion 14', 650, 'AMD Ryzen 5, 16GB RAM, 512GB SSD'),
        ('Acer Aspire 5', 600, 'Intel i3, 8GB RAM, 256GB SSD'),
        ('Dell XPS 13', 1400, 'Intel i7, 16GB RAM, 1TB SSD'),
        ('MSI GF63', 1100, 'Геймерский ноутбук, RTX 3050, 16GB RAM'),
        ('Razer Blade 15', 2000, 'Премиальный ноутбук для игр, RTX 3070, 32GB RAM'),
        ('Samsung Galaxy Book', 900, 'Легкий, компактный, 16GB RAM, 512GB SSD'),
        ('Microsoft Surface Laptop', 1300, 'Стильный, Intel i7, 16GB RAM, 512GB SSD')
    ]
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany('INSERT INTO products (name, price, description) VALUES (?, ?, ?)', products)
    conn.commit()
    conn.close()