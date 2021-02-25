# main file for the discplomacy bot

import os
import discord
import cfg
import asyncio
from datetime import datetime
from discord.ext import commands
from chat_tools.start_game import start_waiting

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
    
@bot.command()
async def orders(ctx):
    '''
    Command to submit orders. Format is: 
    game name
    command unit destination target

    Example:
    sample game
    SUP BUD RUM GAL // this order is for the army in Budapest, supporting the army in Galicia moving into Rumania
    CON ION TUN GRE // this order is for the fleet in Ionian sea, convoying the army in Greece to move to Tunisia
    MOV ROM APU // move orders only take 3 arguments, this moves the army in Rome to Apulia
    HOL ROM // hold orders take two arguments, this orders the Roman army to hold

    When submitting army orders, you must submit your whole slate of orders at once. Any order submission overwrites the previous order slate.
    Much like normal diplomacy, any deviation from proper order format will invalidate your order slate.
    '''
    print(ctx.message.content)

bot.run(TOKEN)