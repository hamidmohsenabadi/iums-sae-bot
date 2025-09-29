import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- شناسه‌های شما در اینجا قرار داده شده است ---
ADMIN_ID = 448466260
# شناسه گروه شما با فرمت صحیح API
GROUP_ID = -1001003179248243

# این هدر برای تشخیص پیام اصلی در زمان تایید است
ADMIN_MESSAGE_HEADER = "یک پیام ناشناس جدید برای تایید دریافت شد:\n\n---\n"

# تنظیمات لاگ برای دیباگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پیام خوش‌آمدگویی را ارسال می‌کند"""
    await update.message.reply_text(
        "سلام. شما می‌توانید پیام خود را به صورت ناشناس برای ادمین ارسال کنید. در صورت تایید، پیام شما در گروه منتشر خواهد شد."
    )

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پیام کاربر را برای تایید به ادمین ارسال می‌کند"""
    if not update.message.text:
        await update.message.reply_text("لطفاً فقط پیام متنی ارسال کنید.")
        return

    user_message = update.message.text
    
    # ساخت دکمه‌های تایید و رد
    keyboard = [
        [
            InlineKeyboardButton("✅ انتشار در گروه", callback_data="publish"),
            InlineKeyboardButton("❌ رد کردن", callback_data="reject"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # ارسال پیام کاربر به همراه هدر و دکمه‌ها به ادمین
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"{ADMIN_MESSAGE_HEADER}{user_message}",
        reply_markup=reply_markup
    )
    
    # اطلاع‌رسانی به کاربر
    await update.message.reply_text("پیام شما برای ادمین ارسال شد و در صف بررسی قرار گرفت.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """کلیک دکمه‌های ادمین را مدیریت می‌کند"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    # جدا کردن پیام اصلی از هدر
    original_message = query.message.text.replace(ADMIN_MESSAGE_HEADER, "")
    
    if action == "publish":
        try:
            # انتشار پیام اصلی در گروه
            await context.bot.send_message(chat_id=GROUP_ID, text=original_message)
            # ویرایش پیام ادمین برای نمایش نتیجه
            await query.edit_message_text(text=f"✅ پیام زیر با موفقیت در گروه منتشر شد:\n\n---\n{original_message}")
        except Exception as e:
            await query.edit_message_text(text=f"خطا در انتشار پیام: {e}")
            logging.error(f"Error publishing message: {e}")
            
    elif action == "reject":
        # ویرایش پیام ادمین برای نمایش نتیجه
        await query.edit_message_text(text=f"❌ پیام زیر رد شد و منتشر نشد:\n\n---\n{original_message}")

def main() -> None:
    """ربات را اجرا می‌کند"""
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise ValueError("توکن ربات در متغیرهای محیطی Render یافت نشد (TELEGRAM_TOKEN)")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Anonymous message bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
