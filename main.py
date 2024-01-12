from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, InlineQueryHandler,CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from threading import Lock

# Define states for the conversation
LANGUAGE, MENU, LEARN_WORDS = range(3)

# SQLite database setup
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()
lock= Lock()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        language TEXT,
        words_learned INTEGER
    )
''')
conn.commit()

# Start command to initiate the conversation
def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    reply_markup = ReplyKeyboardMarkup([['English', 'Russian']], one_time_keyboard=True)
    update.message.reply_text('Please choose your language:', reply_markup=reply_markup)

    return LANGUAGE

# Function to handle language selection
def language(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    language = update.message.text
    with lock:
      # Save language preference in the database
      cursor.execute('INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)', (user_id, language))
      conn.commit()

    # Display menu after language selection
    reply_markup = ReplyKeyboardMarkup([['Learn New Words', 'Books', 'Materials']], one_time_keyboard=True)
    update.message.reply_text(f'Language set to {language}. Choose an option:', reply_markup=reply_markup)

    return MENU

# Function to handle menu options
def menu(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    option = update.message.text

    if option == 'Learn New Words':
        # Display words to learn
        words_to_learn = get_words_to_learn(user_id)
        update.message.reply_text('Learn the following words:', reply_markup=InlineKeyboardMarkup(words_to_learn))
        return LEARN_WORDS
    else:
        update.message.reply_text('Feature under development. Choose another option.')
        return MENU

# Function to handle learned words
def learn_words(update: Update, context: CallbackContext) -> int:
    # Handle the user interacting with the words to learn
    
    return MENU

# Function to get words to learn based on user language
def get_words_to_learn(user_id):
    # Retrieve words from the database based on the user's language
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    language = cursor.fetchone()[0]
    if language == 'English':
        words = ['Word1', 'Word2', 'Word3', 'Word4', 'Word5', 'Word6', 'Word7', 'Word8', 'Word9', 'Word10']
    else:
        words = ['Слово1', 'Слово2', 'Слово3', 'Слово4', 'Слово5', 'Слово6', 'Слово7', 'Слово8', 'Слово9', 'Слово10']

    # Convert words to InlineKeyboardButtons
    words_buttons = [[InlineKeyboardButton(word, callback_data=word)] for word in words]

    return words_buttons

# Function to handle inline button presses
def button_pressed(update: Update, context: CallbackContext):
    query = update.callback_query
    word = query.data
    query.answer(f'You clicked on {word}')

# Define the conversation handler with states
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        LANGUAGE: [MessageHandler(Filters.regex('^(English|Russian)$'), language)],
        MENU: [MessageHandler(Filters.regex('^(Learn New Words|Books|Materials)$'), menu)],
        LEARN_WORDS: [CallbackQueryHandler(button_pressed)]
    },
    fallbacks=[],
)

# Set up the bot
updater = Updater("6494671478:AAGcUDJUHygtbOs_ooPb9Nt95mJiEREVY9E", use_context=True)
dispatcher = updater.dispatcher

# Add the conversation handler to the dispatcher
dispatcher.add_handler(conv_handler)

# Start polling
updater.start_polling()
updater.idle()
