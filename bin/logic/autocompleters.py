from games import manage_games as mg
from . import game_vars as gv
import disnake

async def autocomp_waiting_games(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [lang for lang in mg.get_all_waiting_games(inter.channel_id) if user_input.lower() in lang or user_input.lower() == ""]

async def autocomp_ongoing_games(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [lang for lang in mg.get_all_started_games(inter.channel_id) if user_input.lower() in lang or user_input.lower() == ""]

async def autocomp_all_games(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [lang for lang in mg.get_all_waiting_games(inter.channel_id) + mg.get_all_started_games(inter.channel_id) if user_input.lower() in lang or user_input.lower() == ""]

async def autocomp_unit_locations(inter: disnake.ApplicationCommandInteraction, user_input: str):
    user = inter.user.id
    name = inter.options['name']
    if name == '':
        return []
    else:
        try:
            gamedoc = mg.get_ongoing_game(name, inter.channel_id)
            country = gamedoc['currently_playing'][user]
            combo = gamedoc['state'][country]['armies'] + gamedoc['state'][country]['fleets']
            return [loc for loc in combo if user_input.upper() in combo or user_input == ""]
        except:
            return []

async def autocomp_unit_moves(inter: disnake.ApplicationCommandInteraction, user_input: str):
    ufrom = inter.options['unit_location']
    if ufrom == '':
        return []
    else:
        try:
            moveto = gv.game_map['adjacency'][ufrom]
            return [loc for loc in moveto if user_input.upper() in moveto or user_input == ""]
        except:
            return []