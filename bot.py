import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- شناسه‌های شما در اینجا قرار داده شده است ---
ADMIN_ID = 448466260
GROUP_ID = -1003179248243

# تنظیمات لاگ برای دیباگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پیام خوش‌آمدگویی را ارسال می‌کند"""
    await update.message.reply_text(
        "سلام. شما می‌توانید پیام متنی، عکس یا پیام صوتی خود را به صورت ناشناس برای ادمین ارسال کنید."
    )

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """انواع پیام کاربر را برای تایید به ادمین ارسال می‌کند"""
    
    # ساخت دکمه‌های تایید و رد
    keyboard = [
        [
            InlineKeyboardButton("✅ انتشار در گروه", callback_data="publish"),
            InlineKeyboardButton("❌ رد کردن", callback_data="reject"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # ارسال پیام برای ادمین بر اساس نوع آن (عکس، ویس، یا متن)
    if update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id, # بهترین کیفیت عکس
            caption="یک عکس ناشناس برای تایید دریافت شد.",
            reply_markup=reply_markup
        )
    elif update.message.voice:
        await context.bot.send_voice(
            chat_id=ADMIN_ID,
            voice=update.message.voice.file_id,
            caption="یک پیام صوتی ناشناس برای تایید دریافت شد.",
            reply_markup=reply_markup
        )
    elif update.message.text:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"یک پیام متنی ناشناس برای تایید دریافت شد:\n\n---\n{update.message.text}",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("فقط پیام متنی، عکس و ویس پشتیبانی می‌شود.")
        return

    # اطلاع‌رسانی به کاربر
    await update.message.reply_text("پیام شما برای ادمین ارسال شد و در صف بررسی قرار گرفت.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """کلیک دکمه‌های ادمین را مدیریت می‌کند"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    original_message = query.message # پیام اصلی که ادمین دریافت کرده
    
    if action == "publish":
        try:
            # انتشار پیام در گروه بر اساس نوع آن
            if original_message.photo:
                await context.bot.send_photo(
                    chat_id=GROUP_ID,
                    photo=original_message.photo[-1].file_id
                )
            elif original_message.voice:
                await context.bot.send_voice(
                    chat_id=GROUP_ID,
                    voice=original_message.voice.file_id
                )
            elif original_message.text:
                # جدا کردن متن اصلی از هدر
                clean_text = original_message.text.split("---\n", 1)[1]
                await context.bot.send_message(chat_id=GROUP_ID, text=clean_text)

            # ویرایش پیام ادمین برای نمایش نتیجه
            await query.edit_message_text(text="✅ پیام با موفقیت در گروه منتشر شد.")
            
        except Exception as e:
            await query.edit_message_text(text=f"خطا در انتشار پیام: {e}")
            logging.error(f"Error publishing message: {e}")
            
    elif action == "reject":
        # ویرایش پیام ادمین برای نمایش نتیجه
        await query.edit_message_text(text="❌ پیام رد شد و منتشر نشد.")

def main() -> None:
    """ربات را اجرا می‌کند"""
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise ValueError("توکن ربات در متغیرهای محیطی Render یافت نشد (TELEGRAM_TOKEN)")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    # این بخش تغییر کرده تا عکس و ویس را هم شامل شود
    application.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VOICE) & ~filters.COMMAND, 
        forward_to_admin
    ))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Anonymous message bot (with media support) is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
