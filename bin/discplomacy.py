# main file for the discplomacy bot

import os
import cfg
import disnake
from disnake.ext import commands

os.environ['DATA_DIR'] = os.getcwd()+"/data"

from games import manage_games
from games.public_cog import public_cog
from games.orders_cog import orders_cog

TOKEN=cfg.token
prefix="/"
intents = disnake.Intents.default()
intents.typing = False
intents.presences = False
bot=commands.InteractionBot(test_guilds=[644627772265857077],intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=disnake.Game(name='European Politics c. 1901'))

bot.add_cog(public_cog(bot))
bot.add_cog(orders_cog(bot))

bot.run(TOKEN)