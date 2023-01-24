import disnake
import io
from datetime import datetime
from maps import draw_map

def retreat_message(gamedoc, player=None, country=None):
    name = gamedoc['name'].upper()
    season = gamedoc['season'].upper()
    year = gamedoc['year']
    nextturn = str(datetime.fromisoformat(gamedoc['next_turn']))

    embed = disnake.Embed(
            title=f'{name}, currently {season} {year} -- RETREAT PHASE',
            description=f'Next Turn: `{nextturn}`',
            color=0x00FFBB
        )
    if player == None:
        print('Building a public retreat message')
        embed.add_field(
            name=f'The orders of {season} - {year} have been resolved. Some players must retreat before the next turn opens.',
            value='DO NOT attempt to submit any orders. Orders will not be accepted until the next season begins.'
        )
    else:
        retreats = [r for r in gamedoc['retreats'] if r['country'] == country]
        embed.add_field(
            name='***USE THE /RETREAT COMMAND TO RESOLVE ALL REQUIRED RETREATS***',
            value=f'All retreats must be submitted by {nextturn} or a random retreat location will be selected.'
        )
        for r in retreats:
            embed.add_field(
                name=f'Required retreat AT {r["from"]}',
                value=f'Can retreat TO: {r["possible"]}',
                inline=True
            )
    
    if player is None:
        image = draw_map.draw_public_map_from_state(gamedoc)
    else:
        image = draw_map.draw_private_map_from_state(gamedoc, player)
    with io.BytesIO() as image_binary:
        image.save(image_binary,'PNG')
        image_binary.seek(0)
        em_file=disnake.File(fp=image_binary, filename='current_map_state.png')
        embed.set_image(url='attachment://current_map_state.png')

    return embed, em_file

def supply_message(gamedoc, player=None, country=None):
    name = gamedoc['name'].upper()
    season = gamedoc['season'].upper()
    year = gamedoc['year']
    nextturn = str(datetime.fromisoformat(gamedoc['next_turn']))

    embed = disnake.Embed(
            title=f'{name}, currently {season} {year} -- RETREAT PHASE',
            description=f'Next Turn: `{nextturn}`',
            color=0x00FFBB
        )
    if player == None:
        print('Building a public retreat message')
        embed.add_field(
            name=f'The orders of {season} - {year} have been resolved, and all possible retreats handled. Some players must supply before the next turn opens.',
            value='DO NOT attempt to submit any orders. Orders will not be accepted until the next season begins.'
        )
    else:
        supply = [n for s,n in gamedoc['supply'] if s == country]
        embed.add_field(
            name='***USE THE /REMOVE or /ADD COMMAND TO RESOLVE ALL REQUIRED SUPPLY***',
            value=f'All supply must be submitted by {nextturn}. In the case of positive supply, nothing will be added. In the case of negative supply, random units will be removed.'
        )
        total = sum(supply)
        embed.add_field(
            name='Supply Requirements',
            value=f'***{total}***'
        )
    
    if player is None:
        image = draw_map.draw_public_map_from_state(gamedoc)
    else:
        image = draw_map.draw_private_map_from_state(gamedoc, player)
    with io.BytesIO() as image_binary:
        image.save(image_binary,'PNG')
        image_binary.seek(0)
        em_file=disnake.File(fp=image_binary, filename='current_map_state.png')
        embed.set_image(url='attachment://current_map_state.png')

    return embed, em_file

def not_started_game(gamedoc):
    embed = disnake.Embed(
            title=gamedoc['name'],
            description=f'`{gamedoc["turn_duration"]} / turn`',
            color=0x00FFBB
        )
    player_string = ""
    for p in gamedoc['players']:
        player_string=f'{player_string}<@{p}> '
    embed.add_field(
        name=f'Players (*{len(gamedoc["players"])}/7*)',
        value=player_string,
        inline=True
    )
    embed.add_field(
        name='Waiting...',
        value=f'**{gamedoc["name"]}** will start when 7 players join the lobby and a player issues the `/start` command.',
        inline=False
    )
    image = draw_map.draw_public_map_from_state(gamedoc)
    with io.BytesIO() as image_binary:
        image.save(image_binary,'PNG')
        image_binary.seek(0)
        em_file=disnake.File(fp=image_binary, filename='current_map_state.png')
        embed.set_image(url='attachment://current_map_state.png')

    return (embed, em_file)

def started_game(gamedoc, player=None):
    name = gamedoc['name'].upper()
    season = gamedoc['season'].upper()
    year = gamedoc['year']
    nextturn = str(datetime.fromisoformat(gamedoc['next_turn']))

    embed = disnake.Embed(
            title=f'{name}, currently {season} {year}',
            description=f'Next Turn: `{nextturn}`',
            color=0x00FFBB
    )
    for p in gamedoc['currently_playing'].keys():
        embed.add_field(
            name=f'<@{p}>',
            value=f'***{gamedoc["currently_playing"][p]}***',
            inline=True
        )
    if player is None:
        image = draw_map.draw_public_map_from_state(gamedoc)
    else:
        image = draw_map.draw_private_map_from_state(gamedoc, player)
    with io.BytesIO() as image_binary:
        image.save(image_binary,'PNG')
        image_binary.seek(0)
        em_file=disnake.File(fp=image_binary, filename='current_map_state.png')
        embed.set_image(url='attachment://current_map_state.png')

    return (embed, em_file)

def build_game_message(gamedoc, player=None):
    if not gamedoc['started']:
        return not_started_game(gamedoc)
    else:
        return started_game(gamedoc, player)

def build_error_message(e):
    embed = disnake.Embed()
    embed.color=0xFF0000
    embed.title='Error'
    embed.description=f'`{str(e)}`'

    return embed