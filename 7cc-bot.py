import logging 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
import os
from dotenv import load_dotenv

# 🔥 Set up logging immediately after imports
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment
TOKEN = os.getenv('TOKEN')

if not TOKEN:
    raise ValueError("Token not found! Please make sure the 'TOKEN' environment variable is set.")

# Custom function to clear any active webhook
async def post_init(application: Application) -> None:
    """Delete any existing webhook to avoid conflicts with polling."""
    await application.bot.delete_webhook()
    logging.info("Webhook deleted successfully.")

# Custom error handler function
async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a message to the user."""
    logging.error(f"An error occurred: {context.error}")
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="An error occurred. Please try again later."
        )

# Menu items
menu_items = {
    "0": "Молитва о себе и о участниках (7с), а также о новых молитвенниках если Господу это угодно",
    "0.1": "🔺Не упасть в грех прелюбодеяния",
    "1": "1. Исполняться Духом Святым",
    "1.1": "1.1. Всегда за все каяться",
    "1.2": "1.2. Постоянно быть послушным Иисусу",
    "1.3": "1.3. Всегда и полностью верить Иисусу",
    "4": "4. Пребывать в молитве",
    "5": "5. Изучать Слово",
    "6": "6. Иметь общение со святыми",
    "7": "7. Свидетельствовать об Иисусе"
}

# Questions for each menu item
questions = {
    "0": ["Вы молились о себе и об участниках группы?", "Вы просили Бога послать еще молитвенников?"],
    "0.1": ["Вы молились о том, чтобы Бог вселил в вас и в участников этой группы великий страх перед грехом прелюбодеяния?", "Вы постились по этой теме?"],
    "1": ["Вы стремились исполниться Духом Святым сегодня?", "Исполняли ли вы 3 закона духовной жизни?"],
    "1.1": ["Вы каялись сегодня за свои грехи?", "Какие грехи исповедовали пред Богом и людьми?"],
    "1.2": ["Были ли вы послушны Иисусу сегодня?", "Что вы сделали, чтобы подчиниться воле Иисуса сегодня?"],
    "1.3": ["Вы верите Иисусу во всем?", "Вы доверяли Богу сегодня в своих делах и мыслях?"],
    "4": ["Вы молились сегодня?", "Как долго вы пребывали в молитве?"],
    "5": ["Вы изучали Слово сегодня?", "Какую часть Писания вы прочитали сегодня?"],
    "6": ["Вы имели общение со святыми сегодня?", "С кем из братьев и сестер вы сегодня общались?"],
    "7": ["Вы свидетельствовали об Иисусе сегодня?", "Кому вы рассказали об Иисусе сегодня?"],
}

# User's last message storage
user_last_message = {}

# /start command
async def start(update: Update, context: CallbackContext) -> None:
    """Send the main menu to the user after the /start command and clear previous messages."""
    chat_id = update.message.chat_id

    # Delete the current message from the user
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    except Exception as e:
        logging.error(f"Error deleting message for /start: {e}")
    
    # Delete the last message with questions
    if chat_id in user_last_message:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_last_message[chat_id])
        except Exception as e:
            logging.error(f"Error deleting message: {e}")
    
    # Send the menu
    reply_markup = build_menu()
    message = await context.bot.send_message(chat_id=chat_id, text="Начните проверку, выберите пункт из меню ниже:", reply_markup=reply_markup)
    user_last_message[chat_id] = message.message_id  # Save message ID

# Function to create the menu keyboard
def build_menu():
    """Creates and returns the keyboard with menu items."""
    keyboard = []
    for key, value in menu_items.items():
        keyboard.append([InlineKeyboardButton(value, callback_data=key)])
    return InlineKeyboardMarkup(keyboard)

# Handle button presses
async def button_handler(update: Update, context: CallbackContext) -> None:
    """Handles user menu selection."""
    query = update.callback_query
    await query.answer()
    
    # Get the selected menu item
    selected_item = query.data
    item_title = menu_items.get(selected_item, "Неизвестный пункт")
    
    # Create a message with questions for the selected menu item
    if selected_item in questions:
        question_list = questions[selected_item]
        message_text = f"<b>{item_title}</b>\n\nЗадайте себе эти вопросы, и перейдите к следующим пунктам.:"
        for i, question in enumerate(question_list, start=1):
            message_text += f"\n{i}. <i>{question}</i>"
    else:
        message_text = "Не удалось найти вопросы по этому пункту."

    # Add the menu to the message with questions
    message_text += "\n\n<b>Выберите другой пункт из меню ниже:</b>"
    reply_markup = build_menu()
    
    # Edit the message only if it's different
    if query.message.text != message_text or query.message.reply_markup != reply_markup:
        await query.edit_message_text(text=message_text, reply_markup=reply_markup, parse_mode='HTML')

# Main entry point
if __name__ == "__main__":
    logging.info("Bot started. Configuring handlers and starting polling.")
    
    # Create the bot application instance
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Add a command handler for /start command
    application.add_handler(CommandHandler("start", start))
    
    # Add a callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Add error handler to catch uncaught exceptions
    application.add_error_handler(error_handler)

    try:
        # Run polling to keep the bot running, clear pending updates to avoid conflict
        application.run_polling(drop_pending_updates=True)
    
