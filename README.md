# Mu
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====== الإعدادات ======
TOKEN = "8390525446:AAEb3i5PYYJbKUMaHM1r6qrNKkwxswRlZm8"

ADMIN_ID = 8471320644# 

# ====== تحميل / حفظ المستخدمين ======
def load_allowed_users():
    try:
        with open("allowed.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_allowed_users(users):
    with open("allowed.json", "w") as f:
        json.dump(users, f)

ALLOWED_USERS = load_allowed_users()

# ====== الأوامر ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ALLOWED_USERS or user_id == ADMIN_ID:
        await update.message.reply_text("👋 أهلاً، عندك إذن دخول.")
    else:
        await update.message.reply_text("🚫 ما عندك إذن استخدام البوت.")

async def allow_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بس الأدمن يضيف
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 فقط الأدمن يقدر يضيف مستخدمين.")
        return
    
    if not context.args:
        await update.message.reply_text("📌 استعمل: /allow <user_id>")
        return

    new_id = int(context.args[0])
    if new_id not in ALLOWED_USERS:
        ALLOWED_USERS.append(new_id)
        save_allowed_users(ALLOWED_USERS)
        await update.message.reply_text(f"✅ تمت الموافقة على المستخدم: {new_id}")
    else:
        await update.message.reply_text("ℹ️ هذا المستخدم عنده إذن بالفعل.")

async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بس الأدمن يمنع
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 فقط الأدمن يقدر يمنع مستخدمين.")
        return
    
    if not context.args:
        await update.message.reply_text("📌 استعمل: /block <user_id>")
        return

    block_id = int(context.args[0])
    if block_id in ALLOWED_USERS:
        ALLOWED_USERS.remove(block_id)
        save_allowed_users(ALLOWED_USERS)
        await update.message.reply_text(f"🚫 تم منع المستخدم: {block_id}")
    else:
        await update.message.reply_text("ℹ️ هذا المستخدم أصلاً ما عنده إذن.")

# ====== الرسائل العامة ======
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ALLOWED_USERS or user_id == ADMIN_ID:
        await update.message.reply_text(f"📩 {update.message.text}")
    else:
        await update.message.reply_text("🚫 غير مسموح لك باستخدام البوت.")

# ====== التشغيل ======
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("allow", allow_user))
    app.add_handler(CommandHandler("block", block_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🚀 البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()

    
