import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# ========================
# ملفات التخزين
# ========================
ADMINS_FILE = "admins.json"
MEMBERS_FILE = "members.json"
SCORES_FILE = "scores.json"

OWNER_ID = "8471320644"   # ضع هنا ID المدير

# ========================
# تحميل / حفظ البيانات
# ========================
def load_data(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

ADMINS = load_data(ADMINS_FILE)
MEMBERS = load_data(MEMBERS_FILE)
SCORES = load_data(SCORES_FILE)

# ========================
# صلاحيات
# ========================
def is_owner(user_id):
    return str(user_id) == str(OWNER_ID)

def is_admin(user_id):
    return str(user_id) in ADMINS or is_owner(user_id)

def is_member(user_id):
    return str(user_id) in MEMBERS or is_admin(user_id)

# ========================
# أوامر عامة
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not is_member(user_id):
        await update.message.reply_text("❌ غير مصرح لك باستخدام هذا البوت. اطلب من المدير أو مشرف إضافتك.")
        return
    await update.message.reply_text("👋 أهلاً بك! يمكنك المشاركة في الأسئلة والإجابة بـ (صح) أو (خطأ).")

# ========================
# إضافة وحذف
# ========================
async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("❌ فقط المدير أو المشرف يمكنه إضافة أعضاء.")
        return
    try:
        new_id = str(int(context.args[0]))
        if new_id in MEMBERS:
            await update.message.reply_text("⚠️ هذا المستخدم موجود بالفعل.")
        else:
            MEMBERS[new_id] = True
            save_data(MEMBERS_FILE, MEMBERS)
            await update.message.reply_text(f"✅ تم إضافة العضو {new_id}.")
    except:
        await update.message.reply_text("❌ الاستخدام: /addmember <ID>")

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not is_owner(user_id):
        await update.message.reply_text("❌ فقط المدير يمكنه إضافة مشرفين.")
        return
    try:
        new_id = str(int(context.args[0]))
        if new_id in ADMINS:
            await update.message.reply_text("⚠️ هذا المستخدم مشرف بالفعل.")
        else:
            ADMINS[new_id] = True
            save_data(ADMINS_FILE, ADMINS)
            await update.message.reply_text(f"✅ تمت ترقية {new_id} إلى مشرف.")
    except:
        await update.message.reply_text("❌ الاستخدام: /addadmin <ID>")

# ========================
# عرض القوائم
# ========================
async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ غير مصرح لك.")
        return
    text = "👮‍♂️ قائمة المشرفين:\n"
    for a in ADMINS.keys():
        text += f"- {a}\n"
    text += f"\n👑 المدير: {OWNER_ID}"
    await update.message.reply_text(text)

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ غير مصرح لك.")
        return
    text = "👥 قائمة الأعضاء:\n"
    for m in MEMBERS.keys():
        text += f"- {m}\n"
    await update.message.reply_text(text)

# ========================
# النقاط
# ========================
async def show_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ غير مصرح لك.")
        return
    if not SCORES:
        await update.message.reply_text("📊 لا توجد نقاط بعد.")
        return
    text = "📊 نتائج الأعضاء:\n"
    for user, score in SCORES.items():
        text += f"- {user}: {score}\n"
    await update.message.reply_text(text)

async def reset_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ فقط المدير يمكنه تصفير النقاط.")
        return
    SCORES.clear()
    save_data(SCORES_FILE, SCORES)
    await update.message.reply_text("🔄 تم تصفير جميع النقاط.")

# ========================
# الأسئلة (صح / خطأ)
# ========================
ASKING, = range(1)

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ فقط المشرف أو المدير يمكنه إرسال الأسئلة.")
        return ConversationHandler.END
    await update.message.reply_text("✍️ أرسل سؤالك بهذا الشكل:\n\nالنص|صح أو خطأ")
    return ASKING

async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        question, answer = text.split("|")
        answer = answer.strip()
        context.user_data["question"] = question.strip()
        context.user_data["answer"] = answer
        await update.message.reply_text(f"✅ تم حفظ السؤال:\n\n{question}\n(الجواب: {answer})")
        return ConversationHandler.END
    except:
        await update.message.reply_text("❌ صيغة غير صحيحة. استخدم: السؤال|صح أو خطأ")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 تم إلغاء العملية.")
    return ConversationHandler.END

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not is_member(user_id):
        return
    text = update.message.text.strip()
    if "question" in context.user_data:
        correct = context.user_data["answer"]
        if text == correct:
            SCORES[user_id] = SCORES.get(user_id, 0) + 1
            save_data(SCORES_FILE, SCORES)
            await update.message.reply_text("✅ إجابة صحيحة! نقطة لك.")
        else:
            await update.message.reply_text("❌ إجابة خاطئة.")
    else:
        return

# ========================
# تشغيل البوت
# ========================
def main():
    app = Application.builder().token("8390525446:AAHEZZJ_bmxEFRWBWffU7L7D6-kPsQk_V4s").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addmember", add_member))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("listadmins", list_admins))
    app.add_handler(CommandHandler("listusers", list_users))
    app.add_handler(CommandHandler("scores", show_scores))
    app.add_handler(CommandHandler("resetscores", reset_scores))

    ask_handler = ConversationHandler(
        entry_points=[CommandHandler("ask", ask)],
        states={
            ASKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(ask_handler)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    app.run_polling()

if __name__ == "__main__":
    main()