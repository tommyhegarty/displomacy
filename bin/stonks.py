# stock capabilities for the bot

import os
import discord
import cfg
import requests
from datetime import date, time, timedelta, datetime

async def daily(content, channel):
    split = content.split()
    symbol=split[2].upper()
    search_date=""
    if (len(split) == 3):
        # today
        search_date=date.today()
        now=datetime.now().time()
        if (now < time(9,30,0,0)):
            await channel.send("The market has not opened yet! Sending yesterday's data.")
            search_date=date.today() - timedelta(days = 1) 
    elif (len(split) == 4):
        # provided date
        search_date=split[3]
        if (search_date=="yesterday"):
            search_date=date.today() - timedelta(days = 1) 
    else:
        #incorrect format
        channel.send('Incorrect format for !stonks daily command. Correct usage: !stonks daily [symbol] <date (optional)>')
    url=f'https://api.polygon.io/v1/open-close/{symbol}/{search_date}?apiKey={cfg.stonks_key}'
    response=requests.get(url).json()
    print(response)
    if (response['status'] == "ERROR"):
        errmess = response['error']
        await channel.send(f'Something was wrong with your search parameters... {errmess}')
    else:
        close=response['close']
        ope=response['open']
        high=response['high']
        low=response['low']
        date_from=response['from']
        message=f""" ```
SYMBOL  :   {symbol}
FROM    :   {date_from}
OPEN    :   {ope}
CLOSE   :   {close}
HIGH    :   {high}
LOW     :   {low}``` """
        await channel.send(message)

async def process_message(message):
    content = message.content
    channel = message.channel

    # sample message : !stonks daily pltr
    if ("daily" in content): 
        await daily(content, channel)