import os
import json
import disnake
from disnake.ext import commands
from . import manage_games as mg
from players import manage_players as mp
from . import message_util as mu
from logic import game_vars as gv
from . import manage_orders as mo
from logic import autocompleters as auto

class orders_cog(commands.Cog):
    
    @commands.slash_command(dm_permission=False)
    async def move(
        inter: disnake.ApplicationCommandInteraction
    ):
        '''
        Submit a move order for a single unit.

        Parameters
        ----------
        name: The name of the game you're submitting to.
        unit: The type of unit. Options are 'F' for Fleet and 'A' for Army
        unit_location: Where (3 letter location) the unit is located.
        move_to: Where (3 letter location) the unit is moving.
        '''

    @commands.slash_command(dm_permission=False)
    async def support(
        inter: disnake.ApplicationCommandInteraction,
        name: str,
        unit: str,
        unit_location: str = commands.Param(autocomplete=autocomp_location),
        supporting_from: str = commands.Param(autocomplete=autocomp_location),
        supporting_to: str = commands.Param(autocomplete=autocomp_location)
    ):
        '''
        Submit an order for a single unit.

        Parameters
        ----------
        name: The name of the game you're submitting to.
        unit: The type of unit. Options are 'F' for Fleet and 'A' for Army
        unit_location: Where (3 letter location) the unit is located.
        supporting_from: Where (3 letter location) the unit being supported is.
        supporting_to: Where (3 letter location) the supported unit is going.
        '''
        channel = inter.channel_id
        user = inter.author.id

        try:
            gamedoc = mo.submit_order(name, channel, user, 'SUPPORT', unit_location, supporting_to, supporting_from, unit)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)

    @commands.slash_command(dm_permission=False)
    async def lock(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=autocomp_ongoing_games)
    ):
        channel = inter.channel_id
        user = inter.author.id

        try:
            gamedoc = mo.lock(name, channel, user)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)

    @commands.slash_command(dm_permission=False)
    async def unlock(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=autocomp_ongoing_games)
    ):
        channel = inter.channel_id
        user = inter.author.id

        try:
            gamedoc = mo.unlock(name, channel, user)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)