# main file for the discplomacy bot

import os
import discord
import cfg
import asyncio
from datetime import datetime
from discord.ext import commands
from chat_interface.start_game import start_waiting

TOKEN=cfg.token
prefix="?"
bot=commands.Bot(command_prefix=prefix)

milking={}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def newgame(ctx):
    '''
    Command that starts initiating a game in your Discord server!
    '''
    print(ctx.message.content)
    # lets test concurrency with wait
    await start_waiting()
    

bot.run(TOKEN)