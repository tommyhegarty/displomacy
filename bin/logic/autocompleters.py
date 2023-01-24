from games import manage_games as mg
from dbs import games_db as gdb
from . import game_vars as gv
import disnake

async def autocomp_waiting_games(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [lang for lang in mg.get_all_waiting_games(inter.channel_id) if user_input.lower() in lang or user_input.lower() == ""]

async def autocomp_ongoing_games(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [lang for lang in mg.get_all_started_games(inter.channel_id) if user_input.lower() in lang or user_input.lower() == ""]

async def autocomp_all_games(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [lang for lang in mg.get_all_waiting_games(inter.channel_id) + mg.get_all_started_games(inter.channel_id) if user_input.lower() in lang or user_input.lower() == ""]

# autocomplete for where units are
async def autocomp_unit_locations(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        user = inter.user.id
        name = inter.options['name']
        gamedoc = mg.get_ongoing_game(name, inter.channel_id)
        country = gamedoc['currently_playing'][user]
        combo = gamedoc['state'][country]['armies'] + gamedoc['state'][country]['fleets']
        return [loc for loc in combo if user_input.upper() in combo or user_input == ""]
    except:
        return []

# autocomplete for movement
async def autocomp_unit_adjacent(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        ufrom = inter.options['unit_location']
        moveto = gv.game_map['adjacency'][ufrom]
        return [loc for loc in moveto if user_input.upper() in moveto or user_input == ""]
    except:
        return []

# autocompleter for support
async def autocomp_unit_supports(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        uto = inter.options['supporting_to']
        moveto = gv.game_map['adjacency'][uto].append(uto)
        return [loc for loc in moveto if user_input.upper() in moveto or user_input == ""]
    except:
        return []

# all games for a user
async def autocomp_user_games(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        userid = inter.user.id
        search_results = gdb.search_games({'players': userid})
        return [r['name'] for r in search_results if r['started'] and (user_input in r['name'] or user_input == '')]
    except:
        return []

# channel for the game
async def autocomp_channel_per_game(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        name = inter.options['name']
        return [g['name'] for g in gdb.search_games({'name': name}) if user_input in g['name'] or user_input == '']
    except:
        return []
    
# places that require retreat
async def autocomp_retreat_locations(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        name = inter.options['name']
        channel = inter.options['channel']
        gamedoc = gdb.get_game(name, channel)
        country = gamedoc['currently_playing'][inter.user.id]
        return [r['from'] for r in gamedoc['retreats'] if r['country'] == country and (user_input in r['from'] or user_input == '')]
    except:
        return []

# places that can be retreated to
async def autocomp_retreat_possibilities(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        name = inter.options['name']
        channel = inter.options['channel']
        gamedoc = gdb.get_game(name, channel)
        ret_loc = inter.options['from_location']
        possible = [r['possible'] for r in gamedoc['retreats'] if r['from'] == ret_loc][0]
        return [p for p in possible if user_input in p or user_input == '']
    except:
        return []

# supply locations
async def autocomp_control_locations(inter: disnake.ApplicationCommandInteraction, user_input: str):
    try:
        name = inter.options['name']
        channel = inter.options['channel']
        add_or_remove = inter.options['add_or_remove']
        gamedoc = gdb.get_game(name, channel)
        country = gamedoc['currently_playing'][inter.user.id]
        units = gamedoc['state'][country]['armies'] + gamedoc['state'][country]['fleets']
        if add_or_remove == 'ADD':
            control = gamedoc['state'][country]['controls']
            return [loc for loc in control if loc not in units and (user_input in loc or user_input == '')]
        elif add_or_remove == 'REMOVE':
            return [u for u in units if user_input in u or user_input == '']
        else:
            return []
    except:
        return []

