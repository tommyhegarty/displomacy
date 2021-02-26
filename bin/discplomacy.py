# main file for the discplomacy bot

import os
import discord
import cfg
import asyncio
from datetime import datetime
from discord.ext import commands
import run_game

TOKEN=cfg.token
prefix="?"
bot=commands.Bot(command_prefix=prefix)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.group()
async def game(ctx):
    '''
    Command that deals with games. Subcommands are new, start and view
    '''
    
@game.command()
async def new(ctx):
    '''
    Command that opens a new game lobby. 
    Format is:
    ?game new 'game name' 'turn duration'
    A lobby message will be sent to this channel. Once 7 players have reacted :white_check_mark:, issue the start command in this channel and your game will begin.
    '''

@game.command()
async def start(ctx):
    '''
    Command that starts a game. Requires exactly 7 players. 
    Format is:
    ?game start 'game name'
    '''

@game.command()
async def view(ctx):
    '''
    Command that views the current state of a game lobby. 
    Format is:
    ?game view 'game name'.
    You can only view games you are a player in.
    '''

@bot.group()
async def orders(ctx):
    '''
    Command to see and submit orders, subcommands are see and submit
    '''
    print(ctx.message.content)

@orders.command()
async def submit(ctx):
    '''
    Command to submit orders. 
    Format is: 
    game name
    command type unit destination target

    Example:
    ?orders submit
    game name
    SUP A BUD RUM GAL // this order is for the army in Budapest, supporting the army in Galicia moving into Rumania
    CON F ION TUN GRE // this order is for the fleet in Ionian sea, convoying the army in Greece to move to Tunisia
    MOV A ROM APU // move orders only take 3 arguments, this moves the army in Rome to Apulia
    HOL A ROM // hold orders take two arguments, this orders the Roman army to hold

    When submitting army orders, you must submit your whole slate of orders at once. Any order submission overwrites the previous order slate.
    Much like normal diplomacy, any deviation from proper order format will invalidate your order slate.
    '''
    try:
        run_game.parse_orders(ctx.message.content, ctx.message.author)
        # send success message
    except Exception:
        print("Failed to parse orders.")

@orders.command()
async def see(ctx):
    '''
    Command to see the orders you've submitted for a game. 
    Format is:
    ?orders view gamename
    '''
    game_name=ctx.message.content.replace('?orders view ','')
    run_game.get_orders(game_name,ctx.message.author)

@orders.command()
async def retreat(ctx):
    '''
    Command to fulfill retreat requirements. 
    Retreat orders are given one at a time. Format is:
    ?retreat "game name" currentlocation retreatlocation

    example
    ?retreat "game name" RUM BUD

    If the retreat command is not valid, you will be notified immediately.
    '''

async def supply(ctx):
    '''
    Command to execute supply, either adding or removing armies.
    Supply orders are given one at a time. Format is:
    ?supply "game name" add/remove type location

    example
    ?supply "game name" add A BUD

    If your supply command is not valid, you will be notified immediately
    '''


async def send_private_message(discord_id,game_name,message):
    #user = bot.get_user(discord_id)
    #await user.send(message)
    print(f'Sending {message} to {discord_id}')

#bot.run(TOKEN)