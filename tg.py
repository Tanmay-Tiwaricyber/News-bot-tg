import logging
import requests
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import ConversationHandler, CallbackQueryHandler

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot's token and news API key
TELEGRAM_TOKEN = '7426280797:AAFxve1CAeRinm-XxzF4yfPW50BvhPPrlpw'
NEWS_API_KEY = 'e2f073f6547f40abb3ca9de526202ee6'

# Conversation states
LANGUAGE, NEWS = range(2)

# Dictionary to store user preferences
user_preferences = {}

# Function to fetch news articles in a specific language
def fetch_news(language='en'):
    url = f'https://newsapi.org/v2/top-headlines?language={language}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        return news_data['articles']
    else:
        logger.error(f"Error fetching news: {response.status_code}")
        return []

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    welcome_message = (
        "👋 Welcome to the News Bot!\n"
        "I'm here to keep you updated with the latest news in your preferred language.\n"
        "Use /news to get the latest articles and customize your experience!"
    )
    await update.message.reply_text(welcome_message)
    
    keyboard = [[InlineKeyboardButton("About", callback_data='about')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Please select your preferred language (e.g., 'en' for English, 'hi' for Hindi).", reply_markup=reply_markup)
    return LANGUAGE

# Language handler
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    language = update.message.text.strip()
    user_preferences[user_id] = language
    await update.message.reply_text(f"Your preferred language is set to '{language}'. Use /news to get the latest news.")
    return ConversationHandler.END

# About button handler
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about_message = (
        "📢 About this Bot:\n"
        "This bot provides you with the latest news articles based on your preferred language.\n"
        "Developed by: Silent Programmer\n"
        "Use /start to set your language preference and /news to get the latest news!"
    )
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(about_message)

# News command handler
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    language = user_preferences.get(user_id, 'en')  # Default to English if no preference is set
    articles = fetch_news(language)
    
    if articles:
        for article in articles[:5]:  # Limit to the top 5 news articles
            title = article['title']
            url = article['url']
            image_url = article['urlToImage']
            
            # Create message with the article title and image
            if image_url:
                await update.message.reply_photo(photo=image_url, caption=f"📰 {title}\nRead more: {url}\n")
            else:
                await update.message.reply_text(f"📰 {title}\nRead more: {url}\n")
    else:
        await update.message.reply_text("Sorry, I couldn't fetch the news at the moment.")

# Error handling
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

# Main function to run the bot
def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Set up conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
        },
        fallbacks=[],
    )

    # Register command handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CallbackQueryHandler(about, pattern='about'))

    # Log all errors
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
