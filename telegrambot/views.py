# telegrambot/telegram_bot.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from django.conf import settings
from fetchdata.models import Datacenter, VpsInfo

# Initialize the bot with the token from the settings
updater = Updater(token='YOUR_TELEGRAM_BOT_TOKEN', use_context=True)

def is_superadmin(telegram_id):
    return str(telegram_id) in settings.SUPERADMIN_TELEGRAM_IDS

def start(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    keyboard = [[InlineKeyboardButton("Register Server", callback_data='register_server')]]

    if is_superadmin(telegram_id):
        keyboard.append([InlineKeyboardButton("Admin Features", callback_data='admin_features')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

def register_server(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # Fetch data centers
    datacenters = Datacenter.objects.all()
    keyboard = [[InlineKeyboardButton(dc.name, callback_data=f'dc_{dc.id}') for dc in datacenters]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text="Please assign your data center:", reply_markup=reply_markup)

def handle_datacenter_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # Extract datacenter ID
    datacenter_id = int(query.data.split('_')[1])
    context.user_data['datacenter_id'] = datacenter_id

    query.edit_message_text(text="Please send the IP address of the server:")

    # Move to the next stage where we expect an IP address as a message
    context.user_data['awaiting_ip'] = True

def handle_ip_address(update: Update, context: CallbackContext):
    if context.user_data.get('awaiting_ip'):
        ip_address = update.message.text
        datacenter_id = context.user_data.get('datacenter_id')
        telegram_id = update.message.from_user.id

        try:
            # Filter VPS by datacenter and IP address
            vps_info = VpsInfo.objects.get(datacenter_id=datacenter_id, ip=ip_address)

            # Assign the user's Telegram ID to the VPS
            vps_info.telegram_id = telegram_id
            vps_info.save()

            update.message.reply_text("Server registered successfully!")
        except VpsInfo.DoesNotExist:
            update.message.reply_text("No matching server found with that IP address in the selected data center.")
        finally:
            # Reset the state
            context.user_data['awaiting_ip'] = False
    else:
        update.message.reply_text("Please start the registration process by selecting a data center.")

def admin_features(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # Check if the user is a superadmin
    telegram_id = query.from_user.id
    if is_superadmin(telegram_id):
        query.edit_message_text(text="Superadmin: Here are your features...")
        # Add more admin features here
    else:
        query.edit_message_text(text="Unauthorized access.")

# Set up the command and handler routes
def setup_handlers():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(register_server, pattern='register_server'))
    dp.add_handler(CallbackQueryHandler(handle_datacenter_selection, pattern='^dc_'))
    dp.add_handler(CallbackQueryHandler(admin_features, pattern='admin_features'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_ip_address))

# Start the bot
def run_bot():
    setup_handlers()
    updater.start_polling()
    updater.idle()
