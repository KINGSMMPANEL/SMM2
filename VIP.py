import os
import requests
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Secure API Credentials (Use environment variables instead of hardcoding)
BOT_TOKEN = os.getenv("BOT_TOKEN", "7704623375:AAHDkuHLGhTRmP9GlDNYHyuIotrMLFbXLwE")
CASHFREE_CLIENT_ID = os.getenv("CASHFREE_CLIENT_ID", "942884321c2ce722f469232225488249")
CASHFREE_CLIENT_SECRET = os.getenv("CASHFREE_CLIENT_SECRET", "cfsk_ma_prod_d94bcd29d95bfdcecf223b26b192ef4c_ede2cde1")

# Payment & Download Links
PAYMENT_LINK = "https://payments.cashfree.com/links/m8be8ucdrqkg"
ZIP_FILE_LINK = "https://www.mediafire.com/file/cow6n960qak0xmy/PhonePe.apk/file"
CASHFREE_STATUS_API = "https://api.cashfree.com/api/v1/order/info/status"

# Database file
DB_FILE = "transactions.db"

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_id TEXT UNIQUE,
                        amount TEXT,
                        status TEXT)''')
    conn.commit()
    conn.close()

def save_transaction(transaction_id, amount, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO payments (transaction_id, amount, status) VALUES (?, ?, ?)", (transaction_id, amount, status))
    conn.commit()
    conn.close()

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("💰 BUY NOW - Secure Payment", url=PAYMENT_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = (
        "🔥 **New PhonePe Spoof - Just ₹49!** 🔥\n\n"
        "✔ Instant Activation\n"
        "✔ Works on Latest Version\n"
        "✔ Secure & Undetectable\n\n"
        "🚀 Grab it now! Click below to buy send utr number."
    )
    update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

def verify_payment(update: Update, context: CallbackContext):
    transaction_id = update.message.text.strip()
    headers = {
        "x-client-id": CASHFREE_CLIENT_ID,
        "x-client-secret": CASHFREE_CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    payload = {"orderId": transaction_id}
    try:
        response = requests.post(CASHFREE_STATUS_API, json=payload, headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("orderStatus") == "PAID" and data.get("orderAmount") == "49":
            save_transaction(transaction_id, data.get("orderAmount"), "PAID")
            update.message.reply_text(f"✅ **Payment Verified!** 🎉\n\n💾 Your file is ready: [Download Now]({ZIP_FILE_LINK})", parse_mode='Markdown')
        else:
            update.message.reply_text("❌ Payment not verified. Please check your UTR number and try again.")
    except Exception as e:
        update.message.reply_text("⚠️ An error occurred. Please try again later.")

def main():
    setup_database()
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, verify_payment))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
