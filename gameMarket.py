import telebot
import sqlite3

from currency_converter import CurrencyConverter
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.market import init_db, add_products


bot = telebot.TeleBot('7952118510:AAFfPnO9-HFYeMOqzv4j0TBtbuMXSieh8Iw')
init_db()
c = CurrencyConverter()


@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛒 Магазин", callback_data="shop"))
    markup.add(InlineKeyboardButton("🛍 Корзина", callback_data="cart"))
    markup.add(InlineKeyboardButton("💵 Курс USD/EUR", callback_data="exchange_rate"))
    bot.send_message(message.chat.id, "Добро пожаловать в магазин ноутбуков!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "shop")
def show_products(call):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    text = "🛒 Доступные ноутбуки:\n"
    markup = InlineKeyboardMarkup()

    for product in products:
        product_id, name, price, description = product
        text += f"\n*{name}*\n💰 {price}$\n📄 {description}\n"
        markup.add(InlineKeyboardButton(f"➕ {name}", callback_data=f"add_{product_id}"))

    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_to_cart(call):
    product_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cart (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "Товар добавлен в корзину! ✅")


@bot.callback_query_handler(func=lambda call: call.data == "cart")
def show_cart_callback(call):
    show_cart(call.message)


@bot.message_handler(commands=['cart'])
def show_cart(message):
    user_id = message.from_user.id
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.id, products.name, products.price 
        FROM cart 
        JOIN products ON cart.product_id = products.id 
        WHERE cart.user_id = ?
    """, (user_id,))
    products = cursor.fetchall()
    conn.close()

    if not products:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")
        return

    total_price = sum([p[2] for p in products])
    text = "🛒 Ваша корзина:\n"
    markup = InlineKeyboardMarkup()

    for product in products:
        product_id, name, price = product
        text += f"- {name} ({price}$)\n"
        markup.add(InlineKeyboardButton(f"❌ Удалить {name}", callback_data=f"remove_{product_id}"))

    text += f"\n💵 Общая стоимость: {total_price}$"
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "exchange_rate")
def show_exchange_rate(call):
    rate = c.convert(1, 'USD', 'EUR')
    bot.send_message(call.message.chat.id, f"Текущий курс доллара: 1 USD = {rate:.2f} EUR")


@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_"))
def remove_from_cart(call):
    product_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "Товар удален из корзины ❌")
    show_cart(call.message)


if __name__ == "__main__":
    init_db()
    add_products()
    bot.polling(none_stop=True)

