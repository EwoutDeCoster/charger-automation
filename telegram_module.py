import asyncio
from telegram import ForceReply, Update, Bot, BotCommand,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters,CallbackQueryHandler
import json
import hw
import sys
CONFIG_FILE = 'credentials.json'
with open(CONFIG_FILE, 'r') as file:
    config = json.load(file)
    TOKEN = config["telegram"]["token"]

def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

# Load the token from the config file
config = load_config()
TOKEN = config["telegram"]["token"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    # append the chat_id to the config file ["telegram"]["chat_id"] list
    config = load_config()
    # check if the chat_id is already in the list
    chat_id = update.effective_chat.id
    if chat_id not in config["telegram"]["chat_ids"]:
        config["telegram"]["chat_ids"].append(chat_id)
        save_config(config)
        await update.message.reply_html(
            rf"Hey {user.mention_html()}! Je krijgt nu notificaties het systeem.",
            reply_markup=ForceReply(selective=True),
        )
    else:
        await update.message.reply_html(
            rf"Je krijgt al notificaties van het systeem.",
            reply_markup=ForceReply(selective=True),
        )
    
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /stop is issued."""
    user = update.effective_user
    # append the chat_id to the config file ["telegram"]["chat_id"] list
    config = load_config()
    # check if the chat_id is already in the list
    chat_id = update.effective_chat.id
    if chat_id in config["telegram"]["chat_ids"]:
        config["telegram"]["chat_ids"].remove(chat_id)
        save_config(config)
        await update.message.reply_html(
            rf"Hey {user.mention_html()}! Je krijgt nu geen notificaties meer van het systeem.",
            reply_markup=ForceReply(selective=True),
        )
    else:
        await update.message.reply_html(
            rf"Je bent niet geabonneerd op notificaties van het systeem.",
            reply_markup=ForceReply(selective=True),
        )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /ping is issued and show the latency."""
    await update.message.reply_text(f"Pong! 🏓")

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /dashboard is issued
    This command will send a message with a link to the dashboard."""
    url = "https://ewoutdecoster.tech/"
    text = (
        f"⚡️ <b>Dashboard</b>\n"
        f"——————————————————\n"
        f"\n"
        f"Klik <a href='{url}'>hier</a> om naar het dashboard te gaan."
        f"\n"
        f"——————————————————\n"
        f"<i>Let op: Dit werkt enkel op het thuisnetwerk.</i>"
    )
    await update.message.reply_text(text, parse_mode='HTML')

#async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#    """Echo the user message."""
#    await update.message.reply_text(update.message.text)


# command that can be called from another module to send a message to the user
async def send_message(chat_id: int, subject: str, message: str, footer: str):
    bot = Bot(TOKEN)
    formatted_message = (
        f"<b>{subject}</b>\n"
        f"——————————————————\n"
        f"\n"
        f"<code>{message}</code>\n"
        f"\n"
        f"——————————————————\n"
        f"<i>{footer}</i>"
    )
    await bot.send_message(chat_id=chat_id, text=formatted_message, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    text = (
        "<b> De volgende commando's zijn beschikbaar:</b>\n"
        "\n"
        "/start - Abonneer je op notificaties\n"
        "/stop - Stop notificaties\n"
        "/verbruik - Laat het huidige verbruik zien\n"
        "/dashboard - Ga naar het dashboard\n"
        "/help - Laat dit bericht zien"
    )
    await update.message.reply_text(text, parse_mode='HTML')

async def huidig_verbruik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /huidig_verbruik is issued."""
    huidig_verbruik = hw.get_energy_usage().get('active_power_w')
    text = (
        "<b>⚡ Het huidige verbruik is:</b>\n"
        f"{huidig_verbruik} W"
    )
    await update.message.reply_text(text, parse_mode='HTML')

async def set_commands(application):
    commands = [
        BotCommand("start", "Krijg notificaties van het systeem"),
        BotCommand("stop", "Stop notificaties van het systeem"),
        BotCommand("verbruik", "Bekijk het huidige verbruik"),
        BotCommand("dashboard", "Ga naar het dashboard (Werkt enkel op Home Wi-Fi)"),
        BotCommand("help", "Toon een lijst met commando's")
    ]
    await application.bot.set_my_commands(commands)



def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("verbruik", huidig_verbruik))
    application.add_handler(CommandHandler("dashboard", dashboard))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_commands(application))

    # on non command i.e message - echo the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()