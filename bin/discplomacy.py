# main file for the discplomacy bot

import os
import cfg
import disnake
from disnake.ext import commands, tasks

from games import manage_games as mg
from cogs.public_cog import public_cog
from cogs.orders_cog import orders_cog

os.environ['dbstring'] = cfg.dbstring
TOKEN=cfg.token

intents = disnake.Intents.default()
intents.typing = False
intents.presences = False
bot=commands.InteractionBot(test_guilds=[644627772265857077],intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=disnake.Game(name='European Politics c. 1901'))

@tasks.loop(minutes=1.0)
async def check_games():
    print('Checking if there are any games ready to go.')
    game_list = mg.get_all_ready_games()

bot.add_cog(public_cog(bot))
bot.add_cog(orders_cog(bot))

bot.run(TOKEN)