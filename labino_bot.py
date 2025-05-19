import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# توکن بات تلگرام
TELEGRAM_TOKEN = "7837738652:AAGvDJHX6e2Y6eOvLk9xqb28VWdLalr_g4I"

# آی‌دی مدیر
ADMIN_ID = 71611931  # آی‌دی خودت اینجا وارد شده

# مسیر فایل credentials.json
CREDENTIALS_PATH = os.path.expanduser("~/Desktop/credentials.json")

# احراز هویت Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)

# باز کردن فایل Google Sheet
sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1m0h5olSWPtaCNtEOnMwLOxxeqpI7B7NOJD_2YcEGSCY/edit?gid=0"
).sheet1

# برگه برای ذخیره کاربران (اگر وجود ندارد، ایجاد کن)
try:
    user_sheet = client.open("LABINO Users").sheet1
except:
    spreadsheet = client.create("LABINO Users")
    user_sheet = spreadsheet.sheet1
    user_sheet.append_row(["User ID", "Username", "First Name"])

# تنظیم لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# دستور /start
def start(update, context):
    user = update.message.from_user
    user_data = [str(user.id), user.username or "N/A", user.first_name or "N/A"]

    # بررسی اینکه کاربر قبلاً ثبت شده یا نه
    users = user_sheet.col_values(1)
    if str(user.id) not in users:
        user_sheet.append_row(user_data)

    welcome_message = f"""سلام {user.first_name} عزیز 👋
به بات فروشگاه LABINO خوش اومدی!

نام یا کد محصول مورد نظرت رو بفرست تا اطلاعات کاملش رو دریافت کنی.
"""
    update.message.reply_text(welcome_message)

# پیام‌های متنی برای جستجوی محصول
def handle_message(update, context):
    query = update.message.text.strip().lower()
    rows = sheet.get_all_records()

    for row in rows:
        if query in str(row.get('Product Name', '')).lower() or query in str(row.get('Code', '')).lower():
            response = f"""📦 {row.get('Product Name', 'ناموجود')}
💬 توضیح: {row.get('Description', 'ندارد')}
💵 قیمت: {row.get('Price', 'نامشخص')} تومان
📦 موجودی: {row.get('Stock', 'نامشخص')}"""
            update.message.reply_text(response)
            return

    update.message.reply_text("متأسفم، محصولی با این مشخصات پیدا نشد.")

# دستور /admin فقط برای مدیر
def admin_panel(update, context):
    user = update.message.from_user
    if user.id != ADMIN_ID:
        update.message.reply_text("⛔ دسترسی ندارید.")
        return

    users = user_sheet.get_all_records()
    msg = "📋 لیست کاربران:\n\n"
    for u in users:
        msg += f"- {u['First Name']} | @{u['Username']} | ID: {u['User ID']}\n"
    update.message.reply_text(msg)

# اجرای بات
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_panel))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
