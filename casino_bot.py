import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# =============================================
# Token və Admin ID mühit dəyişənlərindən oxunur
# Railway-də Variables bölməsindən təyin edin
# =============================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Söhbət vəziyyətləri
CHOOSING, VOUCHER_CHAT, WITHDRAW_CHAT = range(3)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ana menyu klaviaturası
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [["🎟 Kod almaq istəyirəm", "💸 Pulumu çıxartmaq istəyirəm"]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"Salam, {user.first_name}! 👋\n\n"
        "Aşağıdakı seçimlərdən birini edin:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING

# İstifadəçi "Kod almaq istəyirəm" seçdikdə
async def voucher_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user

    await update.message.reply_text(
        "🎟 *Voucher (Kod) alışı*\n\n"
        "Zəhmət olmasa, almaq istədiyiniz kod məbləğini və ya sualınızı yazın.\n"
        "Operator tezliklə sizinlə əlaqə saxlayacaq.\n\n"
        "_(Əsas menyuya qayıtmaq üçün /menu yazın)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 *Yeni müraciət: Voucher alışı*\n\n"
            f"👤 Ad: {user.full_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📱 Username: @{user.username if user.username else 'yoxdur'}\n\n"
            f"İstifadəçi ilə danışmaq üçün: tg://user?id={user.id}"
        ),
        parse_mode="Markdown"
    )

    return VOUCHER_CHAT

# İstifadəçi "Pulumu çıxartmaq istəyirəm" seçdikdə
async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user

    await update.message.reply_text(
        "💸 *Pul çıxarma*\n\n"
        "Zəhmət olmasa, çıxarmaq istədiyiniz məbləği və ödəniş məlumatlarınızı yazın.\n"
        "Operator tezliklə sizinlə əlaqə saxlayacaq.\n\n"
        "_(Əsas menyuya qayıtmaq üçün /menu yazın)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 *Yeni müraciət: Pul çıxarma*\n\n"
            f"👤 Ad: {user.full_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📱 Username: @{user.username if user.username else 'yoxdur'}\n\n"
            f"İstifadəçi ilə danışmaq üçün: tg://user?id={user.id}"
        ),
        parse_mode="Markdown"
    )

    return WITHDRAW_CHAT

# Voucher söhbəti zamanı mesajları ötür
async def voucher_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💬 *Voucher - İstifadəçi mesajı*\n"
            f"👤 {user.full_name} (`{user.id}`):\n\n"
            f"{text}"
        ),
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "✅ Mesajınız operatora göndərildi. Tezliklə cavab alacaqsınız."
    )

    return VOUCHER_CHAT

# Pul çıxarma söhbəti zamanı mesajları ötür
async def withdraw_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💬 *Pul çıxarma - İstifadəçi mesajı*\n"
            f"👤 {user.full_name} (`{user.id}`):\n\n"
            f"{text}"
        ),
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "✅ Mesajınız operatora göndərildi. Tezliklə cavab alacaqsınız."
    )

    return WITHDRAW_CHAT

# /menu komutu ilə ana menyuya qayıt
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Ana menyuya qayıtdınız. Seçiminizi edin:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING

# Bilinməyən mesajlar
async def unknown_in_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Zəhmət olmasa aşağıdakı düymələrdən birini seçin:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^🎟 Kod almaq istəyirəm$"), voucher_start),
                MessageHandler(filters.Regex("^💸 Pulumu çıxartmaq istəyirəm$"), withdraw_start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_in_menu),
            ],
            VOUCHER_CHAT: [
                CommandHandler("menu", menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, voucher_message),
            ],
            WITHDRAW_CHAT: [
                CommandHandler("menu", menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_message),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("menu", menu),
        ],
    )

    app.add_handler(conv_handler)

    print("🤖 Bot işə düşdü...")
    app.run_polling()

if __name__ == "__main__":
    main()
