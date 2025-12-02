from flask import Flask
import threading
import telebot

TOKEN = "8156062603:AAGPtV0nhKmziDO9KvUjBsvAwk9VExe9Ljc"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Ruta web mínima para que Render mantenga activo el servicio
@app.route("/")
def home():
    return "Bot activo ✅"

# Función para correr Flask en un hilo aparte
def run_webserver():
    app.run(host="0.0.0.0", port=3000)

# Inicia Flask en un hilo
threading.Thread(target=run_webserver).start()

# Inicia el bot de Telegram
bot.infinity_polling()
