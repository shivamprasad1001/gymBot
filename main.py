import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from sheets import init_sheet, save_lead


# Load config
with open("config.json") as f:
    config = json.load(f)


print(config["sheet_name"])

SHEET = init_sheet(config["sheet_name"])
# States
ASK_GOAL, ASK_NAME, ASK_CONTACT = range(3)
user_data = {}

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Weight Loss", "Muscle Gain", "General Fitness"]]
    await update.message.reply_text(
        "Welcome to ZymBot 💪!\nWhat’s your fitness goal?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_GOAL

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"goal": update.message.text}
    await update.message.reply_text("Great! What’s your name?")
    return ASK_NAME

async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id]["name"] = update.message.text
    await update.message.reply_text("Please share your contact number 📱")
    return ASK_CONTACT

async def save_and_thank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]["contact"] = update.message.text

    # Save to Google Sheet
    save_lead(
        SHEET,
        user_data[uid]["name"],
        user_data[uid]["contact"],
        user_data[uid]["goal"]
    )

    await update.message.reply_text(
        "Thanks! You're all set for a free trial 🎉\n"
        "📍 Location: 123 Fit Street, Gymtown\n"
        "⏰ Timings: 6AM–10PM\n"
        "👨‍🏫 Ask me if you need a trainer or diet plan!"
    )
    return ConversationHandler.END

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled. Type /start to begin again.")
    return ConversationHandler.END

# Run bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(config["telegram_token"]).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact)],
            ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_and_thank)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv)
    print("Bot is running...")
    app.run_polling()
