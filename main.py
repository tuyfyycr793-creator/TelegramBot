from flask import Flask
import threading
import telebot

TOKEN = "8156062603:AAGPtV0nhKmziDO9KvUjBsvAwk9VExe9Ljc"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot activo ✅"

def run_webserver():
    app.run(host="0.0.0.0", port=3000)

threading.Thread(target=run_webserver).start()
bot.infinity_polling()
