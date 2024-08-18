from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from django.conf import settings
from asgiref.sync import sync_to_async
from fetchdata.models import Datacenter, VpsInfo

# Initialize the bot with the token from the settings
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

def is_superadmin(telegram_id):
    return str(telegram_id) in settings.SUPERADMIN_TELEGRAM_IDS

async def start(update: Update, context):
    telegram_id = update.message.from_user.id
    keyboard = [[InlineKeyboardButton("Register Server", callback_data='register_server')]]

    if is_superadmin(telegram_id):
        keyboard.append([InlineKeyboardButton("Admin Features", callback_data='admin_features')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

async def register_server(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Fetch data centers asynchronously
    datacenters = await sync_to_async(list)(Datacenter.objects.all())
    keyboard = [[InlineKeyboardButton(dc.name, callback_data=f'dc_{dc.id}') for dc in datacenters]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="Please assign your data center:", reply_markup=reply_markup)

async def handle_datacenter_selection(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Extract datacenter ID
    datacenter_id = int(query.data.split('_')[1])
    context.user_data['datacenter_id'] = datacenter_id

    await query.edit_message_text(text="Please send the IP address of the server:")

    # Move to the next stage where we expect an IP address as a message
    context.user_data['awaiting_ip'] = True

async def handle_ip_address(update: Update, context):
    if context.user_data.get('awaiting_ip'):
        ip_address = update.message.text
        datacenter_id = context.user_data.get('datacenter_id')
        telegram_id = update.message.from_user.id

        try:
            # Fetch the VPS information asynchronously
            vps_info = await sync_to_async(VpsInfo.objects.get)(datacenter_id=datacenter_id, ip=ip_address)

            # Assign the user's Telegram ID to the VPS
            vps_info.telegram_id = telegram_id
            await sync_to_async(vps_info.save)()

            await update.message.reply_text("Server registered successfully!")
        except VpsInfo.DoesNotExist:
            await update.message.reply_text("No matching server found with that IP address in the selected data center.")
        finally:
            # Reset the state
            context.user_data['awaiting_ip'] = False
    else:
        await update.message.reply_text("Please start the registration process by selecting a data center.")

async def admin_features(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Check if the user is a superadmin
    telegram_id = query.from_user.id
    if is_superadmin(telegram_id):
        await query.edit_message_text(text="Superadmin: Here are your features...")
        # Add more admin features here
    else:
        await query.edit_message_text(text="Unauthorized access.")

# Set up the command and handler routes
def setup_handlers():
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(register_server, pattern='register_server'))
    application.add_handler(CallbackQueryHandler(handle_datacenter_selection, pattern='^dc_'))
    application.add_handler(CallbackQueryHandler(admin_features, pattern='admin_features'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ip_address))

# Start the bot
def run_bot():
    setup_handlers()
    application.run_polling()