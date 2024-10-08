# main file for the displomacy bot

import cfg, disnake, asyncio
from disnake.ext import commands, tasks

import runner
from cogs import message_util as mu
from games import manage_games as mg
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

@tasks.loop(minutes=1.0)
async def check_games():
    await bot.wait_until_ready()
    print('Checking if there are any games ready to go.')
    game_list = mg.get_all_ready_games()
    print(f'Currently ready games are : {game_list}')
    done=[]
    for g in game_list:
        print(f'Executing turn for {g["name"]} in {g["channel"]}')
        if g['name'] not in done:
            done.append(g['name'])
            if g['retreating']:
                new_state=runner.retreat_timeout(g)
                if new_state['supplying']:
                    asyncio.create_task(notify_supply(new_state))
                else:
                    asyncio.create_task(notify_next_turn(new_state))
            elif g['supplying']:
                new_state=runner.supply_timeout(g)
                asyncio.create_task(notify_next_turn(new_state))
            else:
                new_state = runner.game_step(g)
                print(new_state)
                if new_state['retreating']:
                    asyncio.create_task(notify_retreat(new_state))
                elif new_state['supplying']:
                    asyncio.create_task(notify_supply(new_state))
                else:
                    asyncio.create_task(notify_next_turn(new_state))

bot.add_cog(public_cog(bot))
bot.add_cog(orders_cog(bot))

check_games.start()
bot.run(TOKEN)