import telebot
from telebot import types
from flask import Flask
import threading
import json
import os

# ===========================
# Configuración
# ===========================
TOKEN = "8156062603:AAGPtV0nhKmziDO9KvUjBsvAwk9VExe9Ljc"  # Reemplaza con tu token real
ADMINS = [5593967825]  # Reemplaza con tu ID de Telegram como admin

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
DATA_FILE = "data.json"

# ===========================
# Funciones para manejar datos
# ===========================
def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"users": {}, "products": {}, "reset_keys": []}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    else:
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {"users": {}, "products": {}, "reset_keys": []}
    # Asegurar claves
    for k in ["users", "products", "reset_keys"]:
        if k not in data: data[k] = {} if k != "reset_keys" else []
    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===========================
# Flask para Render
# ===========================
@app.route("/")
def home():
    return "Bot activo ✅"

def run_webserver():
    app.run(host="0.0.0.0", port=3000)

threading.Thread(target=run_webserver).start()

# ===========================
# Comandos básicos
# ===========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data["users"]:
        data["users"][user_id] = {"saldo": 0}
        save_data(data)

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_products = types.KeyboardButton("Productos")
    btn_reset = types.KeyboardButton("Resetear Key")
    if user_id in [str(a) for a in ADMINS]:
        btn_admin = types.KeyboardButton("Panel de Admin")
        markup.add(btn_products, btn_reset, btn_admin)
    else:
        markup.add(btn_products, btn_reset)

    bot.send_message(message.chat.id, "Bienvenido a mi tienda, usa /info para ver tus créditos", reply_markup=markup)

@bot.message_handler(commands=["info"])
def info(message):
    user_id = str(message.from_user.id)
    data = load_data()
    saldo = data["users"].get(user_id, {}).get("saldo", 0)
    bot.send_message(message.chat.id, f"Tu saldo es: {saldo}")

# ===========================
# Productos
# ===========================
@bot.message_handler(func=lambda m: m.text == "Productos")
def productos(message):
    data = load_data()
    products = data["products"]
    if not products:
        bot.send_message(message.chat.id, "No hay productos disponibles.")
        return
    markup = types.InlineKeyboardMarkup()
    for p in products:
        markup.add(types.InlineKeyboardButton(p, callback_data=f"prod_{p}"))
    bot.send_message(message.chat.id, "Selecciona un producto:", reply_markup=markup)

# ===========================
# Panel de Admin
# ===========================
@bot.message_handler(func=lambda m: m.text == "Panel de Admin")
def panel_admin(message):
    user_id = str(message.from_user.id)
    if user_id not in [str(a) for a in ADMINS]:
        bot.send_message(message.chat.id, "No tienes permisos para acceder.")
        return
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("Agregar Productos", "Agregar Keys", "Borrar Producto", "Agregar Saldo", "Regresar")
    bot.send_message(message.chat.id, "Panel de Admin:", reply_markup=markup)

# ===========================
# Callback de botones
# ===========================
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    data = load_data()
    user_id = str(call.from_user.id)

    if call.data.startswith("prod_"):
        prod = call.data[5:]
        markup = types.InlineKeyboardMarkup()
        for periodo in ["1 día", "7 días", "30 días"]:
            markup.add(types.InlineKeyboardButton(periodo, callback_data=f"buy_{prod}_{periodo}"))
        markup.add(types.InlineKeyboardButton("Regresar", callback_data="back_products"))
        bot.edit_message_text(f"Selecciona duración de {prod}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("buy_"):
        _, prod, periodo = call.data.split("_")
        stock = len(data["products"].get(prod, {}).get(periodo, []))
        if stock == 0:
            bot.send_message(call.message.chat.id, f"No hay stock disponible para {prod} ({periodo})")
            return
        price = data["products"][prod][periodo][0]["price"]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Confirmar", callback_data=f"confirm_{prod}_{periodo}"))
        markup.add(types.InlineKeyboardButton("Regresar", callback_data=f"prod_{prod}"))
        bot.send_message(call.message.chat.id, f"{prod} ({periodo}) cuesta {price}. ¿Deseas comprar?", reply_markup=markup)

    elif call.data.startswith("confirm_"):
        _, prod, periodo = call.data.split("_")
        user_saldo = data["users"][user_id]["saldo"]
        key_info = data["products"][prod][periodo].pop(0)
        price = key_info["price"]
        key_value = key_info["key"]

        if user_saldo < price:
            bot.send_message(call.message.chat.id, "No tienes suficiente saldo.")
            data["products"][prod][periodo].insert(0, key_info)
        else:
            data["users"][user_id]["saldo"] -= price
            save_data(data)
            bot.send_message(call.message.chat.id, f"Compra realizada ✅\nTu key: {key_value}")

    elif call.data == "back_products":
        productos(call.message)

# ===========================
# Ejecutar bot
# ===========================
bot.infinity_polling()
