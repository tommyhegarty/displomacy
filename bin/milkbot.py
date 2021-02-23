# main file for the milkbot

import os
import discord
import cfg
import stonks
from datetime import datetime

TOKEN=cfg.token
client = discord.Client()

milking={}

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    print("Received message: message")
    if (message.content == '!milk'):
        print('Time to start the milking!!!')
        if message.channel in milking:
            print('We already are milking here')
            await message.channel.send('Ay! I\'m milkin\' here!')
        else:
            milking[message.channel]=datetime.now()
            await message.channel.send(f'Okay {message.author.mention}, we\'ll start milking')
    elif (message.content == '!milk acquired'):
        print('We\'re stopping milking')
        if message.channel not in milking:
            print('We\'re not milking yet.')
            await message.channel.send('No one told me he was getting milk...')
        else:
            started_time=milking.get(message.channel)
            nowtime=datetime.now()
            finalcount=nowtime-started_time
            s=finalcount.total_seconds()
            hours, remainder = divmod(s, 3600)
            minutes, seconds = divmod(remainder, 60)
            finalcount=f'{hours} hours, {minutes} minutes, and {seconds} seconds'
            print(f'Time is {finalcount}')
            await message.channel.send(f'It took {finalcount} to get milk.')
            await message.channel.send('https://tenor.com/view/angle-milk-kurt-gif-8146001')
            finalcount=0
            del milking[message.channel]
    elif (message.content.startswith("!stonks")):
        await stonks.process_message(message)

client.run(TOKEN)