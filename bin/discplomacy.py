# main file for the discplomacy bot

import os
import discord
import cfg
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

client.run(TOKEN)