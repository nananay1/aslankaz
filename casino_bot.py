import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

CHOOSING, VOUCHER_CHAT, WITHDRAW_CHAT = range(3)
# Admin üçün vəziyyət: kimə cavab verir
ADMIN_REPLYING = "admin_replying"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [["🎟 Kod almaq istəyirəm", "💸 Pulumu çıxartmaq istəyirəm"]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"Salam, {user.first_name}! 👋\n\n"
        "Aşağıdakı seçimlərdən birini edin:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING

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

    # Admina düymə ilə bildirim
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💬 Bu istifadəçiyə cavab ver", callback_data=f"reply_{user.id}")
    ]])
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 *Yeni müraciət: Voucher alışı*\n\n"
            f"👤 Ad: {user.full_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📱 Username: @{user.username if user.username else 'yoxdur'}"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return VOUCHER_CHAT

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

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💬 Bu istifadəçiyə cavab ver", callback_data=f"reply_{user.id}")
    ]])
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 *Yeni müraciət: Pul çıxarma*\n\n"
            f"👤 Ad: {user.full_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📱 Username: @{user.username if user.username else 'yoxdur'}"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return WITHDRAW_CHAT

async def voucher_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = update.message.text

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💬 Bu istifadəçiyə cavab ver", callback_data=f"reply_{user.id}")
    ]])
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💬 *Voucher — İstifadəçi mesajı*\n"
            f"👤 {user.full_name} (`{user.id}`):\n\n"
            f"{text}"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await update.message.reply_text(
        "✅ Mesajınız operatora göndərildi. Tezliklə cavab alacaqsınız."
    )
    return VOUCHER_CHAT

async def withdraw_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = update.message.text

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💬 Bu istifadəçiyə cavab ver", callback_data=f"reply_{user.id}")
    ]])
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💬 *Pul çıxarma — İstifadəçi mesajı*\n"
            f"👤 {user.full_name} (`{user.id}`):\n\n"
            f"{text}"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await update.message.reply_text(
        "✅ Mesajınız operatora göndərildi. Tezliklə cavab alacaqsınız."
    )
    return WITHDRAW_CHAT

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Ana menyuya qayıtdınız. Seçiminizi edin:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING

async def unknown_in_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Zəhmət olmasa aşağıdakı düymələrdən birini seçin:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING

# Admin "Bu istifadəçiyə cavab ver" düyməsinə basır
async def admin_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.split("_")[1])
    context.user_data[ADMIN_REPLYING] = user_id

    await query.message.reply_text(
        f"✏️ İndi yazacağınız mesaj `{user_id}` ID-li istifadəçiyə göndəriləcək.\n\n"
        f"Ləğv etmək üçün /ləğv yazın.",
        parse_mode="Markdown"
    )

# Admin mesaj yazır → istifadəçiyə göndər
async def admin_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    target_id = context.user_data.get(ADMIN_REPLYING)
    if not target_id:
        await update.message.reply_text(
            "⚠️ Cavab vermək üçün əvvəlcə istifadəçinin mesajının altındakı "
            "«💬 Bu istifadəçiyə cavab ver» düyməsinə basın."
        )
        return

    text = update.message.text
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"💬 Operator: {text}"
        )
        await update.message.reply_text(f"✅ Mesaj göndərildi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xəta: {e}")

# Admin /ləğv yazır → cavab rejimindən çıx
async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    context.user_data.pop(ADMIN_REPLYING, None)
    await update.message.reply_text("❌ Cavab rejimi ləğv edildi.")

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
    app.add_handler(CallbackQueryHandler(admin_reply_button, pattern=r"^reply_\d+$"))
    app.add_handler(CommandHandler("ləğv", admin_cancel))

    # Admin mesajlarını tut (ConversationHandler-dən kənar)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
        admin_message_handler
    ))

    print("🤖 Bot işə düşdü...")
    app.run_polling()

if __name__ == "__main__":
    main()
