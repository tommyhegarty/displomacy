import disnake
import io
from datetime import datetime
from maps import draw_map

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
    next = str(datetime.fromisoformat(gamedoc['next_turn']))

    embed = disnake.Embed(
            title=f'{name}, currently {season} {year}',
            description=f'Next Turn: `{next}`',
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