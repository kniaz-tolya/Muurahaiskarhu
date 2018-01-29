#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json # manipulation of json
import socket # for server connection
import time
import datetime
import logging
import urllib.request
import urllib.parse
from urllib.request import Request
import subprocess
from subprocess import check_output
from pprint import pprint
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Logging config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Global variables

# Warren the socke reader settings
PORT = 4028 # Port that json-rpc server runs
HOST = 'localhost' # Host that the server runs
BUFF = 4096 # Number of bytes to receive from the server socket

# Telegram bot token
TELEGRAM_BOT_TOKEN = ""

# SlushPool settings
SP_API_TOKEN = "" # full access token
SP_API_TOKEN_RO = "" # read only token
SP_PROFILE_URL = ""
SP_STATS_URL = ""

# SiaMining API
SIA_API_MARKET = ""
SIA_API_NETWORK = ""
SIA_API_POOLINFO = ""
SIA_ADDRESS = ""
SIA_API_SUMMARY = ""
SIA_API_PAYOUTS = ""
SIA_API_WORKERS = ""
SIA_API_ADDRESS = ""

# CoinDesk API to get EUR/BTC/USD daily values () - no auth needed <3
COINDESK_API_URL = ""

# Ant miners as an array - might be a better way but this was the easiest :)
# TODO: key-value dict with name + ip
MINERS = ""

# default values overriden by config
TEMP_WARNING_C = "90"
TEMP_CAUTION_C = "115"

CD_EUR = ""
CD_USD = ""
SIA_USD = ""

def warren(sock):
    """ Warren Buffet... I mean Warren Socket reader """
    buffer = sock.recv(BUFF)
    done = False
    while not done:
        more = sock.recv(BUFF)
        if not more:
            done = True
        else:
            buffer = buffer+more
    if buffer:
        return buffer.decode('utf-8')
    return None


def start(bot, update):
    """ Start menu command handler """
    #pylint:disable=w0613
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def money(bot, update, status=True): # status is false if called from inline buttons
    #pylint:disable=w0613

    # Slushpool
    data = json.loads(json_url_reader(SP_PROFILE_URL))
    data = json.loads(data) # dunno why this needs to be done twice to work...
    unconfirmed_reward = data["unconfirmed_reward"]
    log_entry("BTC EUR price: " + CD_EUR.replace(",", "")) # debug: format currency
    unconfirmed_reward_eur = float(unconfirmed_reward)*float(CD_EUR.replace(",", ""))
    estimated_reward = data["estimated_reward"]
    #estimated_reward_eur = float(estimated_reward)*float(CD_EUR.replace(",", ""))
    confirmed_reward = data["confirmed_reward"]
    confirmed_reward_eur = float(confirmed_reward)*float(CD_EUR.replace(",", ""))
    total_reward = float(unconfirmed_reward) + float(confirmed_reward)
    total_reward_eur = float(total_reward)*float(CD_EUR.replace(",", ""))
    respi = "*Slushpool:*\n"
    respi = respi + "*Unconfirmed rewards*:\n" + str(unconfirmed_reward) + \
    " BTC " + "(" + str("{0:.2f}".format(unconfirmed_reward_eur)) + " \u20ac)\n"
    respi = respi + "*Confirmed rewards*:\n" + str(confirmed_reward) + \
    " BTC " + "(" + str("{0:.2f}".format(confirmed_reward_eur)) + " \u20ac)\n"
    #respi = respi + "*Estimated reward*:\n" + str(estimated_reward) + \
    #" BTC " + "(" + str("{0:.2f}".format(estimated_reward_eur)) + " \u20ac)\n"
    respi = respi + "*Total rewards*:\n" + str("{0:.5f}".format(total_reward)) + \
    " BTC " + "(*" + str("{0:.2f}".format(total_reward_eur)) + " \u20ac*)\n"

    # Siamining
    data = json.loads(json_url_reader(SIA_API_SUMMARY))
    data = json.loads(data)
    sia_balance = float(data['balance'])
    sia_paid = float(data['paid'])
    log_entry("SIA balance: " + str("{0:.5f}".format(sia_balance)) + " SIA")
    log_entry("SIA paid: " + str("{0:.5f}".format(sia_paid)) + " SIA")

    sia_balance_usd = sia_balance*SIA_USD
    sia_paid_usd = sia_paid*SIA_USD
    sia_total_rewards = sia_balance+sia_paid
    sia_total_rewards_usd = sia_total_rewards*SIA_USD

    log_entry("SIA unpaid balance: " + str("{0:.2f}".format(sia_balance_usd)) + " USD")
    log_entry("SIA paid balance: " + str("{0:.2f}".format(sia_paid_usd)) + " USD")
    log_entry("SIA total rewards: " + str("{0:.2f}".format(sia_total_rewards_usd)) + " USD")

    respi = respi + "\n*Siamining:*" + "\n*Unpaid balance:*\n" + \
    str("{0:.5f}".format(sia_balance)) + " SIA " + \
    "(*\u0024" + str("{0:.2f}".format(sia_balance_usd)) + "*)\n"
    respi = respi + "*Paid rewards:*\n" + str("{0:.5f}".format(sia_paid)) + " SIA " + \
    "(*\u0024" + str("{0:.2f}".format(sia_paid_usd)) + "*)\n"
    respi = respi + "*Total rewards:*\n" + str("{0:.5f}".format(sia_total_rewards)) + " SIA " + \
    "(*\u0024" + str("{0:.2f}".format(sia_total_rewards_usd)) + "*)\n"

    respi = respi + "\n🤑💰🤑"
    if status:
        update.message.reply_text(text=respi, parse_mode="Markdown")
    else:
        return respi

def antstats(bot, update):
    #pylint:disable=w0613
    """ Ant Miner Stats """
    data = json.loads(json_url_reader(SP_STATS_URL))
    data = json.loads(data) # dunno why this needs to be done twice to work...
    respi = 'Recent blocks:\n'
    blocks = data["blocks"]
    for keys in data:
        log_entry(keys)
    update.message.reply_text(text=respi, parse_mode="Markdown")

def recentrounds(bot, update):
    """ Recent rounds menu command handler """
    #pylint:disable=w0613
    data = json.loads(json_url_reader(SP_STATS_URL))
    data = json.loads(data) # dunno why this needs to be done twice to work...
    respi = 'Recent blocks:\n'
    blocks = data["blocks"]
    for block in data["blocks"]:
        log_entry(block[0])
    update.message.reply_text(text=respi, parse_mode="Markdown")


def valuations(bot, update, status=True):
    """ Show coin valuations """
    respi = coindesk(bot, update, False)
    respi = respi + init_sia_price(bot, update, False)
    if status:
        update.message.reply_text(text=respi, parse_mode="Markdown")
    return respi


def coindesk(bot=True, update=True, status=True):
    """ Coindesk api handler """
    #pylint:disable=w0613
    data = json.loads(json_url_reader(COINDESK_API_URL))
    data = json.loads(data)
    cd_updated = data["time"]["updated"]
    #pylint:disable=w0603
    global CD_EUR
    CD_EUR = data["bpi"]["EUR"]["rate"]
    global CD_USD
    CD_USD = data["bpi"]["USD"]["rate"]
    respi = "(Last update: " + cd_updated + ")\n\n"
    respi = respi + "1 BTC = " + CD_EUR + " EUR\n"
    respi = respi + "1 BTC = " + CD_USD + " USD\n"
    log_entry("Coindesk values updated!")
    log_entry("1 BTC = " + CD_EUR + " EUR")
    log_entry("1 BTC = " + CD_USD + " USD")
    if status:
        update.message.reply_text(text=respi, parse_mode="Markdown")
    else:
        return respi

def init_sia_price(bot=True, update=True, status=True):
    """ Get SIA coin price """
    data = json.loads(json_url_reader(SIA_API_MARKET))
    data = json.loads(data)
    #pylint:disable=w0603
    global SIA_USD
    SIA_USD = data["usd_price"]
    respi = "1 SIA = " + str(SIA_USD) + " USD"
    log_entry("Siamining values updated!")
    log_entry(respi)
    if status:
        update.message.reply_text(text=respi, parse_mode="Markdown")
    else:
        return respi


def status(bot, update):
    """ Status menu command handler """
    #pylint:disable=w0613
    keyboard = [[InlineKeyboardButton("⭕ Recent Blocks", callback_data='recentrounds'),
                 InlineKeyboardButton("🤑 Show Me The Money!", callback_data='poolaccount')],

                [InlineKeyboardButton("🌡️ All Temperatures", callback_data='Temperature'),
                 InlineKeyboardButton("💰 Coin Valuations", callback_data='Valuations')],

                [InlineKeyboardButton("🐜 Ant 1", callback_data='Ant1'),
                 InlineKeyboardButton("🐜 Ant 2", callback_data='Ant2'),
                 InlineKeyboardButton("🐜 Ant 3", callback_data='Ant3'),
                 InlineKeyboardButton("🐜 Ant 4", callback_data='Ant4')],

                [InlineKeyboardButton("🐜 Ant 5", callback_data='Ant5'),
                 InlineKeyboardButton("🐜 Ant 6", callback_data='Ant6'),
                 InlineKeyboardButton("🐜 Ant 7", callback_data='Ant7'),
                 InlineKeyboardButton("🐜 Ant 8", callback_data='Ant8')],

                [InlineKeyboardButton("🐜 Ant 9", callback_data='Ant9'),
                 InlineKeyboardButton("🐜 Ant 10", callback_data='Ant10'),
                 InlineKeyboardButton("🐜 Ant 11", callback_data='Ant11'),
                 InlineKeyboardButton("🐜 Ant 12", callback_data='Ant12')],

                [InlineKeyboardButton("🐜 Ant 13", callback_data='Ant13'),
                 InlineKeyboardButton("🐜 Ant 14", callback_data='Ant14'),
                 InlineKeyboardButton("🐜 Ant 15", callback_data='Ant15'),
                 InlineKeyboardButton("🐜 Ant 16", callback_data='Ant16')],

                [InlineKeyboardButton("Mitäs tähän laitettais?", callback_data='RpiTemp')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('What status would you like to see?', reply_markup=reply_markup)


def button(bot, update):
    """ Telegram Menu button handler """
    query = update.callback_query

    choice = ''

    if query.data == 'Valuations':
        choice = 'Valuations'
        log_entry("--- Selected menu item: " + choice)
        respi = valuations(bot, update, False)
    elif query.data == 'Temperature':
        choice = 'Temperature'
        log_entry("--- Selected menu item: " + choice)
        respi = temps(bot, update, False)
    elif query.data == 'poolaccount':
        choice = 'Money'
        log_entry("--- Selected menu item: " + choice)
        respi = money(bot, update, False) # call with False status to allow response overdrive
    elif query.data == 'recentrounds':
        data = json.loads(json_url_reader(SP_STATS_URL))
        respi = data
        pprint(respi)
    elif query.data == 'RpiTemp':
        data = subprocess.Popen('/opt/vc/bin/vcgencmd measure_temp', shell=True,  \
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in data.stdout.readlines():
            respi = line
            log_entry(line)
        data = check_output(['/opt/vc/bin/vcgencmd', 'measure_temp'])
        respi = data
        log_entry(respi)
    elif query.data == 'Ant1':
        choice = MINERS[0]
        respi = getstatus(MINERS[0])
    elif query.data == 'Ant2':
        choice = MINERS[1]
        respi = getstatus(MINERS[1])
    elif query.data == 'Ant2':
        choice = MINERS[1]
        respi = getstatus(MINERS[1])
    elif query.data == 'Ant3':
        choice = MINERS[2]
        respi = getstatus(MINERS[2])
    elif query.data == 'Ant4':
        choice = MINERS[3]
        respi = getstatus(MINERS[3])
    elif query.data == 'Ant5':
        choice = MINERS[4]
        respi = getstatus(MINERS[4])
    elif query.data == 'Ant6':
        choice = MINERS[5]
        respi = getstatus(MINERS[5])
    elif query.data == 'Ant7':
        choice = MINERS[6]
        respi = getstatus(MINERS[6])
    elif query.data == 'Ant8':
        choice = MINERS[7]
        respi = getstatus(MINERS[7])
    elif query.data == 'Ant9':
        choice = MINERS[8]
        respi = getstatus(MINERS[8])
    elif query.data == 'Ant10':
        choice = MINERS[9]
        respi = getstatus(MINERS[9])
    elif query.data == 'Ant11':
        choice = MINERS[10]
        respi = getstatus(MINERS[10])
    elif query.data == 'Ant12':
        choice = MINERS[11]
        respi = getstatus(MINERS[11])
    elif query.data == 'Ant13':
        choice = MINERS[12]
        respi = getstatus(MINERS[12])
    elif query.data == 'AllMiners':
        respi = getstatus(query.data)
        log_entry(respi)
    else:
        choice = 'Invalid choice!'

    log_entry("--- Finished menu item: " + choice)

    bot.edit_message_text(text="{}".format(respi),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode="Markdown")

def help(bot, update):
    """ Help menu command handler """
    #pylint:disable=w0613
    update.message.reply_text("Use /status to test this bot.")

def error(bot, update, error):
    #pylint:disable=w0613
    """ Log Errors caused by Updates  """
    LOGGER.warning('Update "%s" caused error "%s"', update, error)

def temps(bot, update, status=True):
    """ Temps menu command handler """
    #pylint:disable=w0613
    respi = getstatus("AllMiners")
    if status:
        update.message.reply_text(text=respi, parse_mode="Markdown")
    else:
        return respi

def getstatus(miner, status=True):
    """ Read status from miners """
    respi = ''
    hightemp = 0
    highminer = ''
    if miner == "AllMiners":
        response = ""
        respi = respi + 'Chip temps of miners:\n'
        for miner in MINERS:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialise our socket
            #log_entry('Connecting to socket on miner:', miner)
            sock.connect((miner, PORT))# connect to host <HOST> to port <PORT>
            dumped_data = "stats|0".encode('utf-8')
            sock.send(dumped_data) # Send the dumped data to the server
            response = warren(sock)
            response = response.split(',')
            respi = respi + '\n' + miner + ': '
            for key in response:
                key = key.split('=')
                if key[0] == 'temp2_6':
                    respi = respi + "*" + key[1]
                    if int(key[1]) > hightemp:
                        hightemp = int(key[1])
                        highminer = miner
                elif key[0] == 'temp2_7':
                    respi = respi + "/" + key[1]
                    if int(key[1]) > hightemp:
                        hightemp = int(key[1])
                        highminer = miner
                elif key[0] == 'temp2_8':
                    respi = respi + "/" + key[1] + "*℃"
                    if int(key[1]) > hightemp:
                        hightemp = int(key[1])
                        highminer = miner
            sock.close() # close the socket connection
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialise our socket
        #log_entry('Connecting to socket on miner:', miner)
        sock.connect((miner, PORT))# connect to host <HOST> to port <PORT>
        dumped_data = "stats|0".encode('utf-8')
        sock.send(dumped_data) # Send the dumped data to the server
        response = warren(sock)
        response = response.split(',')
        respi = miner + ': '
        for key in response:
            key = key.split('=')
            log_entry(key)
            if key[0] == 'temp2_6':
                respi = respi + "Chip1: *" + key[1] + "*℃"
                if int(key[1]) > hightemp:
                    hightemp = int(key[1])
                    highminer = miner
            elif key[0] == 'temp2_7':
                respi = respi + ", Chip2: *" + key[1] + "*℃"
                if int(key[1]) > hightemp:
                    hightemp = int(key[1])
                    highminer = miner
            elif key[0] == 'temp2_8':
                respi = respi + ", Chip3: *" + key[1] + "*℃"
                if int(key[1]) > hightemp:
                    hightemp = int(key[1])
                    highminer = miner
        sock.close() # close the socket connection
            #print(respi)
    if hightemp > int(TEMP_WARNING_C):
        respi = respi + "\n\n🌶️ *WARNING*: Reaching *high* temps! >" \
        + TEMP_WARNING_C + "℃ 🌶️" # >105
    elif hightemp > int(TEMP_CAUTION_C):
        respi = respi + "\n\n🔥🔥🔥 *CAUTION*: *TOO HIGH TEMPS*!!! >" \
        + TEMP_CAUTION_C + "℃ 🔥🔥🔥" # >115
    else:
        respi = respi+ "\n\n👌 All temps within boundaries!" # <=105
    respi = respi + "\n🌡️ Highest temp: *" + str(hightemp) + "℃* (" + str(highminer) + ")"
    return respi


def json_url_reader(url):
    """ Read JSON output from URL """
    # added user agent so that coindesk is not blocking as rogue request
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    fin = urllib.request.urlopen(req)
    fin = fin.read().decode('utf-8')
    return json.dumps(fin)


def log_entry(choice):
    """ Log entry to screen with timestamp, todo: file """
    time_stamp = time.time()
    formatted_time_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
    print("[" + formatted_time_stamp + "] " + choice)


def maini():
    """ Debug function to override mine for development """
    #response = getstatus("192.168.2.11")
    getstatus("192.168.2.11")


def init_config():
    """ Initialize configruation (e.g. Telegram bot token) from config.json """
    with open('config.json') as json_cfg_file:
        config = json.load(json_cfg_file)
    return config


def init_global_vars(config):
    """ Init global variables - and yes, I know... """
    #pylint: disable=w0603
    global COINDESK_API_URL
    COINDESK_API_URL = config['coindesk']['api_url']
    global SP_API_TOKEN
    SP_API_TOKEN = config['slushpool']['api_token']
    global SP_API_TOKEN_RO
    SP_API_TOKEN_RO = config['slushpool']['ro_api_token']
    global SP_PROFILE_URL
    SP_PROFILE_URL = config['slushpool']['profile_url'] + SP_API_TOKEN
    global SP_STATS_URL
    SP_STATS_URL = config['slushpool']['stats_url'] + SP_API_TOKEN
    global SIA_API_MARKET
    SIA_API_MARKET = config['siamining']['api_market']
    global SIA_API_NETWORK
    SIA_API_NETWORK = config['siamining']['api_network']
    global SIA_API_POOLINFO
    SIA_API_POOLINFO = config['siamining']['api_poolinfo']
    global SIA_ADDRESS
    SIA_ADDRESS = config['siamining']['address']
    global SIA_API_ADDRESS
    SIA_API_ADDRESS = config['siamining']['api_address']
    global SIA_API_SUMMARY
    SIA_API_SUMMARY = SIA_API_ADDRESS + SIA_ADDRESS + "/summary"
    global SIA_API_PAYOUTS
    SIA_API_PAYOUTS = SIA_API_ADDRESS + SIA_ADDRESS + "/payouts"
    global SIA_API_WORKERS
    SIA_API_WORKERS = SIA_API_ADDRESS + SIA_ADDRESS + "/workers"
    global MINERS
    MINERS = config['mining']['miners']
    global TEMP_CAUTION_C
    TEMP_CAUTION_C = config['mining']['temp_caution_c']
    global TEMP_WARNING_C
    TEMP_WARNING_C = config['mining']['temp_warning_c']



def debug_print(telegram_token):
    """ Debug function to verify config file read and string etc """
    log_entry("Telegram token: " + telegram_token)
    log_entry("Coindesk api url: " + COINDESK_API_URL)
    log_entry("Slushpool api token: " + SP_API_TOKEN)
    log_entry("Slushpool read only api token: " + SP_API_TOKEN_RO)
    log_entry("Slushpool profile url: " + SP_PROFILE_URL)
    log_entry("Slushpool stats url: " + SP_STATS_URL)
    log_entry("SiaMining market url: " + SIA_API_MARKET)
    log_entry("SiaMining network url: " + SIA_API_NETWORK)
    log_entry("SiaMining pool url: " + SIA_API_POOLINFO)
    log_entry("SiaMining api summary url: " + SIA_API_SUMMARY)
    log_entry("SiaMining api payouts url: " + SIA_API_PAYOUTS)
    log_entry("SiaMining workers url: " + SIA_API_WORKERS)
    for miner in MINERS:
        log_entry("Adding miner to bot: " + miner)
    log_entry("Temperature limits: caution=" + TEMP_CAUTION_C + \
              ", warning=" + TEMP_WARNING_C)


def main():
    """ Main Function """
    # Create the Updater and pass it your bot's token.

    config = init_config()
    telegram_bot_token = config['telegram']['token']

    init_global_vars(config)

    #debug
    debug_print(telegram_bot_token)

    # init currency values to global variables before starting polling
    coindesk(False, False, False)
    init_sia_price(False, False, False)

    updater = Updater(telegram_bot_token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('status', status))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('money', money))
    updater.dispatcher.add_handler(CommandHandler('rounds', recentrounds))
    updater.dispatcher.add_handler(CommandHandler('cd', valuations))
    updater.dispatcher.add_handler(CommandHandler('stats', antstats))
    updater.dispatcher.add_handler(CommandHandler('temps', temps))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
