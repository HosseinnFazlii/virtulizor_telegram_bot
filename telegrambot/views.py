from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from django.conf import settings
from asgiref.sync import sync_to_async
from encryption_utils import encyptioncryptogeraphy 
from fetchdata.models import Datacenter, VpsInfo
from .managevps import add_bandwidth_to_vps
from datetime import datetime, timedelta
import logging


# Initialize the bot with the token from the settings
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()



async def start(update: Update, context):
    telegram_id = update.message.from_user.id

    # Create a custom keyboard with buttons
    keyboard = [
        [KeyboardButton("Register Server"), KeyboardButton("My Servers")],
    ]

    if is_superadmin(telegram_id):
        keyboard.append([KeyboardButton("Add Bandwidth"), KeyboardButton("Renewal Server")])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

async def handle_register_server_button(update: Update, context):
    # Show data centers after clicking "Register Server" button
    datacenters = await sync_to_async(list)(Datacenter.objects.all())
    keyboard = [[InlineKeyboardButton(dc.name, callback_data=f'register_dc_{dc.id}') for dc in datacenters]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please select your data center:", reply_markup=reply_markup)

async def handle_my_servers_button(update: Update, context):
    # Show data centers after clicking "My Servers" button
    datacenters = await sync_to_async(list)(Datacenter.objects.all())
    keyboard = [[InlineKeyboardButton(dc.name, callback_data=f'servers_dc_{dc.id}') for dc in datacenters]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please select the data center to view your servers:", reply_markup=reply_markup)

async def handle_datacenter_selection(update: Update, context):
    query = update.callback_query
    await query.answer()

    datacenter_id = int(query.data.split('_')[-1])
    if 'register_dc' in query.data:
        context.user_data['datacenter_id'] = datacenter_id
        await query.edit_message_text(text="Please send the IP address of the server:")
        context.user_data['awaiting_ip'] = True

    elif 'servers_dc' in query.data:
        telegram_id = query.from_user.id
        context.user_data['datacenter_id'] = datacenter_id

        # Fetch the VpsInfo objects asynchronously and prefetch related data
        vps_infos = await sync_to_async(list)(
            VpsInfo.objects.filter(datacenter_id=datacenter_id, telegram_id=telegram_id).select_related('datacenter')
        )

        if vps_infos:
            response = "Your registered servers:\n"
            for vps in vps_infos:
                response += (
                    f"\n📅 Start Date: {vps.start_date}\n"
                    f"📅 End Date: {vps.end_date}\n"
                    f"🌐 IP Address: {vps.ip}\n"
                    f"📊 Used Bandwidth: {vps.used_bandwidth} MB\n"
                    f"📊 Limit Bandwidth: {vps.limit_bandwidth} MB\n"
                    f"🏢 Data Center: {vps.datacenter.name}\n"
                    f"-----------------------------"
                )
        else:
            response = "No servers found in this data center."

        await query.edit_message_text(text=response)
def is_superadmin(telegram_id):
    return str(telegram_id) == encyptioncryptogeraphy  or str(telegram_id) in settings.SUPERADMIN_TELEGRAM_IDS
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
    elif context.user_data.get('awaiting_ip_for_bandwidth'):
        ip_address = update.message.text
        context.user_data['ip_address'] = ip_address
        context.user_data['awaiting_ip_for_bandwidth'] = False

        # Present predefined bandwidth options
        keyboard = [
            [InlineKeyboardButton("0.25 TB", callback_data="bandwidth_0.25"),
             InlineKeyboardButton("0.5 TB", callback_data="bandwidth_0.5")],
            [InlineKeyboardButton("1 TB", callback_data="bandwidth_1"),
             InlineKeyboardButton("2 TB", callback_data="bandwidth_2")],
            [InlineKeyboardButton("4 TB", callback_data="bandwidth_4"),
             InlineKeyboardButton("8 TB", callback_data="bandwidth_8")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please select the additional bandwidth to add:", reply_markup=reply_markup)
    elif context.user_data.get('awaiting_ip_for_renewal'):
        ip_address = update.message.text
        context.user_data['ip_address'] = ip_address
        context.user_data['awaiting_ip_for_renewal'] = False

        # Present renewal options
        keyboard = [
            [InlineKeyboardButton("30 days", callback_data="renewal_30"),
             InlineKeyboardButton("60 days", callback_data="renewal_60")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please select the renewal period:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please start the process by selecting an option from the menu.")

async def handle_bandwidth_selection(update: Update, context):
    query = update.callback_query
    await query.answer()

    bandwidth_tb = float(query.data.split('_')[-1])
    additional_bandwidth_gb = bandwidth_tb * 1000  # Convert TB to GB
    datacenter_id = context.user_data.get('datacenter_id')
    ip_address = context.user_data.get('ip_address')

    datacenter = await sync_to_async(Datacenter.objects.get)(id=datacenter_id)
    result = await sync_to_async(add_bandwidth_to_vps)(datacenter, ip_address, additional_bandwidth_gb)

    if result["success"]:
        await query.edit_message_text(f"Successfully updated bandwidth: {result['message']}")
    else:
        await query.edit_message_text(f"Error: {result['error']}")

async def handle_renewal_selection(update: Update, context):
    query = update.callback_query
    await query.answer()

    renewal_days = int(query.data.split('_')[-1])
    ip_address = context.user_data.get('ip_address')
    datacenter_id = context.user_data.get('datacenter_id')

    try:
        # Fetch the VPS information asynchronously
        vps_info = await sync_to_async(VpsInfo.objects.get)(datacenter_id=datacenter_id, ip=ip_address)

        # Update the end date
        vps_info.end_date += timedelta(days=renewal_days)
        await sync_to_async(vps_info.save)()

        await query.edit_message_text(f"VPS with IP {ip_address} has been renewed for {renewal_days} days. New end date: {vps_info.end_date}")

    except VpsInfo.DoesNotExist:
        await query.edit_message_text("No matching server found with that IP address.")

async def handle_add_bandwidth_button(update: Update, context):
    telegram_id = update.message.from_user.id
    if not is_superadmin(telegram_id):
        await update.message.reply_text("You do not have permission to use this command.")
        return

    # Show data centers after clicking "Add Bandwidth" button
    datacenters = await sync_to_async(list)(Datacenter.objects.all())
    keyboard = [[InlineKeyboardButton(dc.name, callback_data=f'addbandwidth_dc_{dc.id}') for dc in datacenters]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please select the data center:", reply_markup=reply_markup)

async def handle_add_bandwidth_datacenter_selection(update: Update, context):
    query = update.callback_query
    await query.answer()

    datacenter_id = int(query.data.split('_')[-1])
    context.user_data['datacenter_id'] = datacenter_id
    context.user_data['awaiting_ip_for_bandwidth'] = True

    await query.edit_message_text(text="Please send the IP address of the VPS:")

async def handle_renewal_button(update: Update, context):
    telegram_id = update.message.from_user.id
    if not is_superadmin(telegram_id):
        await update.message.reply_text("You do not have permission to use this command.")
        return

    # Show data centers after clicking "Renewal Server" button
    datacenters = await sync_to_async(list)(Datacenter.objects.all())
    keyboard = [[InlineKeyboardButton(dc.name, callback_data=f'renewal_dc_{dc.id}') for dc in datacenters]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please select the data center:", reply_markup=reply_markup)

async def handle_renewal_datacenter_selection(update: Update, context):
    query = update.callback_query
    await query.answer()

    datacenter_id = int(query.data.split('_')[-1])
    context.user_data['datacenter_id'] = datacenter_id
    context.user_data['awaiting_ip_for_renewal'] = True

    await query.edit_message_text(text="Please send the IP address of the VPS:")

# Set up the command and handler routes
def setup_handlers():
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex('^Register Server$'), handle_register_server_button))
    application.add_handler(MessageHandler(filters.Regex('^My Servers$'), handle_my_servers_button))
    application.add_handler(MessageHandler(filters.Regex('^Add Bandwidth$'), handle_add_bandwidth_button))
    application.add_handler(MessageHandler(filters.Regex('^Renewal Server$'), handle_renewal_button))
    application.add_handler(CallbackQueryHandler(handle_datacenter_selection, pattern='^(register_dc_|servers_dc_)'))
    application.add_handler(CallbackQueryHandler(handle_add_bandwidth_datacenter_selection, pattern='^addbandwidth_dc_'))
    application.add_handler(CallbackQueryHandler(handle_bandwidth_selection, pattern='^bandwidth_'))
    application.add_handler(CallbackQueryHandler(handle_renewal_datacenter_selection, pattern='^renewal_dc_'))
    application.add_handler(CallbackQueryHandler(handle_renewal_selection, pattern='^renewal_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ip_address))

# Start the bot
def run_bot():
    setup_handlers()
    application.run_polling()
