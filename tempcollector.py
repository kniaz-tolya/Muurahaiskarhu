#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json # manipulation of json
import socket # for server connection
import sys
import logging
import urllib.request
import urllib.parse
import subprocess
from subprocess import check_output
from pprint import pprint
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 4028 # Port that json-rpc server runs
HOST = 'localhost' # Host that the server runs
BUFF = 4096 # Number of bytes to receive from the server socket

# Ant miners as an array - might be a better way but this was the easiest :)
# TODO: key-value dict with name + ip
miners = ["192.168.2.11", "192.168.2.12", "192.168.2.13", "192.168.2.14", "192.168.2.15",
            "192.168.2.16", "192.168.2.17", "192.168.2.18", "192.168.2.19", "192.168.2.20",
            "192.168.2.21", "192.168.2.22"]

# global variables

# socketreader lol
def warren(socket):
	buffer = socket.recv(BUFF)
	done = False
	while not done:
		more = socket.recv(BUFF)
		if not more:
			done = True
		else:
			buffer = buffer+more
	if buffer:
		return buffer.decode('utf-8')

def money(bot, update, status=True): # status is false if called from inline buttons
    data = json.loads(json_url_reader(SP_PROFILE_URL))
    data = json.loads(data) # dunno why this needs to be done twice to work...
    hashrate = data["hashrate"]
    unconfirmed_reward = data["unconfirmed_reward"]
    print("cd_eur: " + cd_eur.replace(",","")) # debug: format currency to suitable float
    unconfirmed_reward_eur = float(unconfirmed_reward)*float(cd_eur.replace(",",""))
    estimated_reward = data["estimated_reward"]
    estimated_reward_eur = float(estimated_reward)*float(cd_eur.replace(",",""))
    confirmed_reward = data["confirmed_reward"]
    confirmed_reward_eur = float(confirmed_reward)*float(cd_eur.replace(",",""))
    total_reward = float(unconfirmed_reward) + float(confirmed_reward)
    total_reward_eur = float(total_reward)*float(cd_eur.replace(",",""))
    respi = "\n"
    respi = respi + "*Unconfirmed rewards*:\n" + str(unconfirmed_reward) + " BTC " + "(" + str("{0:.2f}".format(unconfirmed_reward_eur)) + " \u20ac)\n"
    respi = respi + "*Confirmed rewards*:\n" + str(confirmed_reward) + " BTC " + "(" + str("{0:.2f}".format(confirmed_reward_eur)) + " \u20ac)\n"
    respi = respi + "*Estimated reward*:\n" + str(estimated_reward) + " BTC " + "(" + str("{0:.2f}".format(estimated_reward_eur)) + " \u20ac)\n"
    respi = respi + "*Total rewards*:\n" + str("{0:.5f}".format(total_reward)) + " BTC " + "(" + str("{0:.2f}".format(total_reward_eur)) + " \u20ac)\n"
    respi = respi + "\n🤑💰🤑"
    print("Money\n" + respi)
    if(status):
        update.message.reply_text(text=respi, parse_mode="Markdown")
    else:
        return respi


def coindesk(bot=True, update=True, status=True):
    data = json.loads(json_url_reader(COINDESK_API_URL))
    data = json.loads(data)
    cd_updated = data["time"]["updated"]
    global cd_eur
    cd_eur = data["bpi"]["EUR"]["rate"]
    global cd_usd
    cd_usd = data["bpi"]["USD"]["rate"]
    respi = "(Last update: " + cd_updated + ")\n\n"
    respi = respi + "1 BTC = " + cd_eur + " EUR\n"
    respi = respi + "1 BTC = " + cd_usd + " USD\n"
    print("Coindesk values updated!\n" + respi)
    if(status):
        update.message.reply_text(text=respi, parse_mode="Markdown")
    else:
        return respi


def getstatus(miner, status=True):
    respi = ''
    hightemp = 0
    highminer = ''
    if miner == "AllMiners":
        response = ""
        for miner in miners:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialise our socket
            print('Connecting to socket on miner:',miner)
            sock.connect((miner, PORT))# connect to host <HOST> to port <PORT>
            dumped_data="stats|0".encode('utf-8')
            sock.send(dumped_data) # Send the dumped data to the server
            response = warren(sock)
            response = response.split(',')
            respi = respi + '\n' + miner + ': '
            for key in response:
                    key = key.split('=')
                    # print(key)
                    if key[0]=='temp2_6':
                        respi = respi + "Chips 1/2/3: *" + key[1]
                        if int(key[1]) > hightemp:
                            hightemp = int(key[1])
                            highminer = miner
                    elif key[0]=='temp2_7':
                        respi = respi + "/" + key[1]
                        if int(key[1]) > hightemp:
                            hightemp = int(key[1])
                            highminer = miner
                    elif key[0]=='temp2_8':
                        respi = respi + "/" + key[1] + "*℃"
                        if int(key[1]) > hightemp:
                            hightemp = int(key[1])
                            higminer = miner
            sock.close() # close the socket connection
    else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialise our socket
            print('Connecting to socket on miner:',miner)
            sock.connect((miner, PORT))# connect to host <HOST> to port <PORT>
            dumped_data="stats|0".encode('utf-8')
            sock.send(dumped_data) # Send the dumped data to the server
            response = warren(sock)
            response = response.split(',')
            respi = miner + ': '
            for key in response:
                    key = key.split('=')
                    print(key)
                    if key[0]=='temp2_6':
                        respi = respi + "Chip1: *" + key[1] + "*℃"
                        if int(key[1]) > hightemp:
                            hightemp = int(key[1])
                            highminer = miner
                    elif key[0]=='temp2_7':
                        respi = respi + ", Chip2: *" + key[1] + "*℃"
                        if int(key[1]) > hightemp:
                            hightemp = int(key[1])
                            highminer = miner
                    elif key[0]=='temp2_8':
                        respi = respi + ", Chip3: *" + key[1] + "*℃"
                        if int(key[1]) > hightemp:
                            hightemp = int(key[1])
                            highminer = miner
            sock.close() # close the socket connection
            print(respi)
    if hightemp > 105:
        respi = respi + "\n\n🌶️ *WARNING*: Reaching *high* temps! >105℃ 🌶️" # >105
    elif hightemp > 114:
        respi = respi + "\n\n🔥🔥🔥 *CAUTION*: *TOO HIGH TEMPS*!!! >115℃ 🔥🔥🔥" # >115
    else:
        respi = respi+ "\n\n👌 All temps within boundaries!" # <=105
    respi = respi + "\n🌡️ Highest temp: *" + str(hightemp) + "℃* (" + str(highminer) + ")"
    return respi

def json_url_reader(url):
    f = urllib.request.urlopen(url)
    r = f.read().decode('utf-8')
    return json.dumps(r)


def main():
    getstatus("192.168.2.11")

if __name__ == '__main__':
    main()
