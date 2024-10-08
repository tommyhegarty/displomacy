from games import manage_games as mg
from dbs import games_db as gdb
from . import game_vars as gv
import disnake

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
