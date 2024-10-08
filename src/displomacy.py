# main file for the displomacy bot

import cfg, disnake, asyncio
from disnake.ext import commands, tasks

import runner
from cogs import message_util as mu
from cogs.game_cog import public_cog
from cogs.orders_cog import orders_cog

TOKEN=cfg.token
intents = disnake.Intents.default()
intents.typing = False
intents.presences = False

bot=commands.InteractionBot(test_guilds=[644627772265857077],intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=disnake.Game(name='European Politics c. 1901'))

async def notify_retreat(gamedoc):
    print(f'Entering retreat phase for {gamedoc["name"]} in {gamedoc["channel"]}')
    retreats = list(dict.fromkeys([r['country'] for r in gamedoc['retreats']]))
    for player, country in gamedoc['currently_playing'].items():
        if country in retreats:
            (embed, image) = mu.retreat_message(gamedoc=gamedoc, player=player, country=country)
            user=await bot.fetch_user(player)
            await user.send(embed=embed, file=image)
    
    embed, image = mu.retreat_message(gamedoc=gamedoc)
    channel=await bot.fetch_channel(gamedoc['channel'])
    await channel.send(embed=embed, file=image)

async def notify_supply(gamedoc):
    print(f'Entering supply phase for {gamedoc["name"]} in {gamedoc["channel"]}')
    supply = list(dict.fromkeys([c for c,num in gamedoc['supply']]))
    for player, country in gamedoc['currently_playing'].items():
        if country in supply:
            (embed, image) = mu.supply_message(gamedoc=gamedoc, player=player, country=country)
            user=await bot.fetch_user(player)
            await user.send(embed=embed, file=image)
    
    embed, image = mu.supply_message(gamedoc=gamedoc)
    channel=await bot.fetch_channel(gamedoc['channel'])
    await channel.send(embed=embed, file=image)

async def notify_next_turn(gamedoc):
    print(f'Entering next turn for {gamedoc["name"]} in {gamedoc["channel"]}')
    embed, image = mu.build_game_message(gamedoc=gamedoc)
    channel=await bot.fetch_channel(gamedoc['channel'])
    await channel.send(embed=embed, file=image)


bot.add_cog(public_cog(bot))
bot.add_cog(orders_cog(bot))
bot.run(TOKEN)