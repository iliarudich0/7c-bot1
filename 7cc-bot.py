
import logging 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext
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

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    """Respond to the /start command."""
    await update.message.reply_text('Hello! The bot is running! 🚀')

# Main entry point
if __name__ == "__main__":
    logging.info("Bot started. Configuring handlers and starting polling.")
    
    # Create the bot application instance
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Add a command handler for /start command
    application.add_handler(CommandHandler("start", start))
    
    # Add error handler to catch uncaught exceptions
    application.add_error_handler(error_handler)

    try:
        # Run polling to keep the bot running, clear pending updates to avoid conflict
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logging.error(f"Error while running the bot: {e}")
