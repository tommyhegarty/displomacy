# main file for the discplomacy bot

import os
import discord
import cfg
import asyncio
from datetime import datetime
from discord.ext import commands
import run_game
import shlex

TOKEN=cfg.token
prefix="?"
bot=commands.Bot(command_prefix=prefix)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(pass_context=True)
async def test(ctx):
    '''
    Command to test embed looks
    '''
    print(ctx.message.author)
    print(ctx.message.author.id)
    await send_private_message(ctx.message.author, 'TEST','This is a test message')

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
    ?game view "game name".
    You can only view games you are a player in.
    '''
    split=shlex.split(ctx.message.content)
    if (len(split) != 3):
        await ctx.message.author.send("Incorrect number of arguments for ?game view, format is '?game view \"game name\"' (the double quotes around game name are required).")
    else:
        print(f'Looking at {split[2]} with author {ctx.message.author.id}')
        game_doc=run_game.get_gamestate(str(ctx.message.author.id), split[2])
        await return_gamedoc(ctx.message.author, split[2], game_doc)

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
    (all_orders, name)=run_game.parse_orders(ctx.message.content, str(ctx.message.author.id))
    if (all_orders):
        (result, result_tuple)=run_game.execute_turn(name)
    else:
        await return_orders_submitted_successfully(ctx.message.author,name)

@orders.command()
async def see(ctx):
    '''
    Command to see the orders you've submitted for a game. 
    Format is:
    ?orders see "gamename"
    '''
    split=shlex.split(ctx.message.content)
    if (len(split) != 3):
        await ctx.message.author.send("Incorrect number of arguments for ?orders view, format is '?orders view \"game name\"' (the double quotes around game name are required).")
    else:
        orders=run_game.get_orders(split[2],str(ctx.message.author.id))
        await return_orders(ctx.message.author, orders, split[2])

@bot.command()
async def retreat(ctx):
    '''
    Command to fulfill retreat requirements. 
    Retreat orders are given one at a time. Format is:
    ?retreat "game name" currentlocation retreatlocation

    example
    ?retreat "game name" RUM BUD

    If the retreat command is not valid, you will be notified immediately.
    '''
    split=shlex.split(ctx.message.content)
    if (len(split) != 4):
        await ctx.message.author.send("Incorrect number of arguments for ?supply, format is '?retreat \"game name\" currentlocation retreatlocation' (the double quotes around game name are required).")
    else:
        (retreat_over,game_doc)=run_game.execute_retreat(str(ctx.message.author.id), split[1], split[2], split[3])
        if (retreat_over):
            await notify_retreat_complete(game_doc)

@bot.command()
async def supply(ctx):
    '''
    Command to execute supply, either adding or removing armies.
    Supply orders are given one at a time. Format is:
    ?supply "game name" add/remove type location

    example
    ?supply "game name" add A BUD

    If your supply command is not valid, you will be notified immediately
    '''
    split=shlex.split(ctx.message.content)
    if (len(split) != 5):
        await ctx.message.author.send("Incorrect number of arguments for ?supply, format is '?supply \"game name\" add/remove type location' (the double quotes around game name are required).")
    else:
        (supply_over,game_doc)=run_game.execute_supply(str(ctx.message.author.id), split[1], split[2], split[3], split[4])
        if (supply_over):
            await notify_supply_complete(game_doc)


@bot.command()
async def wincon(ctx):
    '''
    Command to change wincon for a game.
    1 means winning alone (the default setting), 2 means two way draw, etc up to 6. Format is:
    ?wincon "gamename" wincon

    example
    ?wincon "gamename" 3
    Will set your saved state to indicate that you are willing to draw when only 3 players remain.
    '''
    split=shlex.split(ctx.message.content)
    if (len(split) != 3):
        await ctx.message.author.send("Incorrect number of arguments for ?wincon, format is '?wincon \"game name\" wincon' (the double quotes around game name are required).")
    else:
        run_game.change_wincon(str(ctx.message.author.id), split[1], split[2])

@bot.command()
async def surrender(ctx):
    '''
    Command to surrender a game with the name you provide.
    Format is:
    ?surrender "gamename"

    Careful! This action cannot be undone. You will continue to receive messages about this game until it ends, but you will no longer be required to submit orders.
    '''
    split=shlex.split(ctx.message.content)
    if (len(split) != 2):
        await ctx.message.author.send("Incorrect number of arguments for ?surrender, format is '?surrender \"gamename\"' (the double quotes around game name are required)")
    else:
        run_game.surrender(str(ctx.message.author.id), split[1])



@commands.Cog.listener()
async def on_command_error(self, ctx, error):
    print(f'Handling... {error}')

async def send_private_message(user,game_name,message):
    embed=discord.Embed(
        title=game_name,
        description=message,
        color=discord.Color.dark_green()
    )
    embed.set_author(name='Discplomacy')
    await user.send(embed=embed)
    print(f'Sending {message} to {user}')

async def notify_new_phase(game_doc):
    print('here is where we notify a new phase')

async def notify_supply_complete(game_doc):
    players=game_doc['currently_playing']
    year=game_doc['year']
    season=game_doc['season']
    game=game_doc['name']
    for player in players.keys():
        await send_private_message(player,game, f'Winter completed, it is now {season} {year}')

async def notify_retreat_complete(game_doc):
    players=game_doc['currently_playing']
    year=game_doc['year']
    season=game_doc['season']
    game=game_doc['name']
    for player in players.keys():
        await send_private_message(player,game, f'Retreats completed, it is now {season} {year}')

async def notify_reinforcements(player,supply,name):
    await send_private_message(player,name,f'You can resupply your forces up to {supply}. Use the ?supply add command, remembering that the only valid supply locations are unoccupied supply centers you began the game with.')

async def notify_disbandment(player,supply,name):
    await send_private_message(player,name,f'You must disband your forces up to {supply}. Use the ?supply remove command.')

async def notify_retreats_required(retreats,name):
    for player in retreats.keys():
        locations = retreats[player]
        send_private_message(player, name,f'The turn has executed and you are forced to retreat from the following locations: {locations}')

async def notify_unit_destroyed(location, player, name):
    await send_private_message(player,name,f'Your unit at {location} was defeated and had nowhere to retreat, so was destroyed.')

async def notify_game_start(game_doc):
    players=game_doc['currently_playing']
    game=game_doc['name']
    for player in players.keys():
        country = game_doc['currently_playing'][player]
        await send_private_message(player, game, f'Your game has started! You have been assigned {country}')

async def notify_game_over(winners,players):
    print('Game has ended')

async def return_orders(player, orders, game):
    await send_private_message(player, game, f'Your currently active orders are {orders}')

async def return_orders_submitted_successfully(player, game):
    await send_private_message(player, game, f'You have successfully submitted your orders.')

async def return_gamedoc(player, game, game_doc):
    await send_private_message(player, game, f'The current state of the game is {game_doc}')

bot.run(TOKEN)