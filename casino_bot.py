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
ADMIN_REPLYING = "admin_replying"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Klaviaturalar ──────────────────────────────────────────

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [["🎟 Kod almaq istəyirəm", "💸 Pulumu çıxartmaq istəyirəm"]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def back_keyboard():
    """İstifadəçi üçün 'Geri qayıt' düyməsi"""
    return ReplyKeyboardMarkup(
        [["🔙 Əsas menyuya qayıt"]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def admin_reply_keyboard(user_id):
    """Admin üçün inline düymə"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💬 Bu istifadəçiyə cavab ver", callback_data=f"reply_{user_id}")
    ]])

def admin_cancel_keyboard():
    """Admin cavab rejimini dayandırmaq üçün inline düymə"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Cavabı dayandır", callback_data="cancel_reply")
    ]])

# ── İstifadəçi funksiyaları ────────────────────────────────

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
        "Almaq istədiyiniz kod məbləğini və ya sualınızı yazın.\n"
        "Operator tezliklə sizinlə əlaqə saxlayacaq.",
        parse_mode="Markdown",
        reply_markup=back_keyboard()
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 *Yeni müraciət: Voucher alışı*\n\n"
            f"👤 Ad: {user.full_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📱 Username: @{user.username if user.username else 'yoxdur'}"
        ),
        parse_mode="Markdown",
        reply_markup=admin_reply_keyboard(user.id)
    )
    return VOUCHER_CHAT

async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user

    await update.message.reply_text(
        "💸 *Pul çıxarma*\n\n"
        "Çıxarmaq istədiyiniz məbləği və ödəniş məlumatlarınızı yazın.\n"
        "Operator tezliklə sizinlə əlaqə saxlayacaq.",
        parse_mode="Markdown",
        reply_markup=back_keyboard()
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 *Yeni müraciət: Pul çıxarma*\n\n"
            f"👤 Ad: {user.full_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📱 Username: @{user.username if user.username else 'yoxdur'}"
        ),
        parse_mode="Markdown",
        reply_markup=admin_reply_keyboard(user.id)
    )
    return WITHDRAW_CHAT

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """İstifadəçi 'Geri qayıt' düyməsinə basır"""
    await update.message.reply_text(
        "Əsas menyuya qayıtdınız. Seçiminizi edin:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING

async def voucher_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = update.message.text or update.message.caption or "📎 [Fayl/Şəkil göndərdi]"

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💬 *Voucher — İstifadəçi mesajı*\n"
            f"👤 {user.full_name} (`{user.id}`):\n\n"
            f"{text}"
        ),
        parse_mode="Markdown",
        reply_markup=admin_reply_keyboard(user.id)
    )
    # Şəkil/fayl varsa forward et
    if not update.message.text:
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

    await update.message.reply_text(
        "✅ Mesajınız operatora göndərildi. Tezliklə cavab alacaqsınız."
    )
    return VOUCHER_CHAT

async def withdraw_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = update.message.text or update.message.caption or "📎 [Fayl/Şəkil göndərdi]"

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💬 *Pul çıxarma — İstifadəçi mesajı*\n"
            f"👤 {user.full_name} (`{user.id}`):\n\n"
            f"{text}"
        ),
        parse_mode="Markdown",
        reply_markup=admin_reply_keyboard(user.id)
    )
    # Şəkil/fayl varsa forward et
    if not update.message.text:
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

    await update.message.reply_text(
        "✅ Mesajınız operatora göndərildi. Tezliklə cavab alacaqsınız."
    )
    return WITHDRAW_CHAT

async def unknown_in_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Zəhmət olmasa aşağıdakı düymələrdən birini seçin:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSING

# ── Admin funksiyaları ─────────────────────────────────────

async def admin_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin 'Bu istifadəçiyə cavab ver' düyməsinə basır"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    if query.data == "cancel_reply":
        context.user_data.pop(ADMIN_REPLYING, None)
        await query.message.reply_text("❌ Cavab rejimi dayandırıldı.")
        return

    user_id = int(query.data.split("_")[1])
    context.user_data[ADMIN_REPLYING] = user_id

    await query.message.reply_text(
        f"✏️ İndi yazacağınız mesaj `{user_id}` ID-li istifadəçiyə göndəriləcək.",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard()
    )

async def admin_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin mesaj yazır → istifadəçiyə göndər"""
    if update.effective_user.id != ADMIN_ID:
        return

    target_id = context.user_data.get(ADMIN_REPLYING)
    if not target_id:
        await update.message.reply_text(
            "⚠️ Cavab vermək üçün əvvəlcə istifadəçinin mesajının altındakı "
            "«💬 Bu istifadəçiyə cavab ver» düyməsinə basın."
        )
        return

    try:
        if update.message.text:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"💬 Operator: {update.message.text}"
            )
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=target_id,
                photo=update.message.photo[-1].file_id,
                caption=f"💬 Operator: {update.message.caption or ''}"
            )
        elif update.message.document:
            await context.bot.send_document(
                chat_id=target_id,
                document=update.message.document.file_id,
                caption=f"💬 Operator: {update.message.caption or ''}"
            )
        elif update.message.video:
            await context.bot.send_video(
                chat_id=target_id,
                video=update.message.video.file_id,
                caption=f"💬 Operator: {update.message.caption or ''}"
            )

        await update.message.reply_text(
            "✅ Mesaj göndərildi.",
            reply_markup=admin_cancel_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Xəta: {e}")

# ── Əsas ──────────────────────────────────────────────────

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
                MessageHandler(filters.Regex("^🔙 Əsas menyuya qayıt$"), back_to_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, voucher_message),
                MessageHandler(filters.PHOTO | filters.Document.ALL | filters.VIDEO | filters.AUDIO, voucher_message),
            ],
            WITHDRAW_CHAT: [
                MessageHandler(filters.Regex("^🔙 Əsas menyuya qayıt$"), back_to_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_message),
                MessageHandler(filters.PHOTO | filters.Document.ALL | filters.VIDEO | filters.AUDIO, withdraw_message),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
        ],
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_reply_button, pattern=r"^(reply_\d+|cancel_reply)$"))
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.Document.ALL | filters.VIDEO) & filters.User(ADMIN_ID),
        admin_message_handler
    ))

    print("🤖 Bot işə düşdü...")
    app.run_polling()

if __name__ == "__main__":
    main()
