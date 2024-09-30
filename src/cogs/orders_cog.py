import disnake
from disnake.ext import commands
from games import manage_orders as mo
from logic import autocompleters as auto
from . import message_util as mu

class orders_cog(commands.Cog):
    
    @commands.slash_command(dm_permission=False)
    async def move(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_ongoing_games),
        unit: str = commands.Param(choices=['F','A']),
        unit_location: str = commands.Param(autocomplete=auto.autocomp_unit_locations),
        move_to: str = commands.Param(autocomplete=auto.autocomp_unit_adjacent),
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

        channel = inter.channel_id
        user = str(inter.author.id)

        try:
            gamedoc = mo.submit_order(name, channel, user, 'MOVE', unit_location, move_to, 'NAN', unit)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)

    @commands.slash_command(dm_permission=False)
    async def support(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_ongoing_games),
        unit: str = commands.Param(choices=['F','A']),
        unit_location: str = commands.Param(autocomplete=auto.autocomp_unit_locations),
        supporting_to: str = commands.Param(autocomplete=auto.autocomp_unit_adjacent),
        supporting_from: str = commands.Param(autocomplete=auto.autocomp_unit_supports)
    ):
        '''
        Submit a support order for a single unit.

        Parameters
        ----------
        name: The name of the game you're submitting to.
        unit: The type of unit. Options are 'F' for Fleet and 'A' for Army
        unit_location: Where (3 letter location) the unit is located.
        supporting_to: Where (3 letter location) the unit being supported is going.
        supporting_from: Where (3 letter location) the supported unit is currently located.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)

        try:
            gamedoc = mo.submit_order(name, channel, user, 'SUPPORT', unit_location, supporting_to, supporting_from, unit)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)

    @commands.slash_command(dm_permission=False)
    async def hold(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_ongoing_games),
        unit: str = commands.Param(choices=['F','A']),
        unit_location: str = commands.Param(autocomplete=auto.autocomp_unit_locations)
    ):
        '''
        Submit a hold older for a single unit.

        Parameters
        ----------
        name: The name of the game you're submitting to.
        unit: The type of unit. Options are 'F' for Fleet and 'A' for Army
        unit_location: Where (3 letter location) the unit is located.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)

        try:
            gamedoc = mo.submit_order(name, channel, user, 'HOLD', unit_location, unit_location, 'NAN', unit)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)

    @commands.slash_command(dm_permission=False)
    async def convoy(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_ongoing_games),
        fleet_location: str = commands.Param(autocomplete=auto.autocomp_unit_locations),
        convoy_to: str = commands.Param(autocomplete=auto.autocomp_unit_adjacent),
        convoy_from: str = commands.Param(autocomplete=auto.autocomp_unit_supports)
    ):
        '''
        Submit a convoy order for a fleet.

        Parameters
        ----------
        name: The name of the game you're submitting to.
        fleet_location: Where (3 letter location) the fleet is located.
        convoy_to: Where (3 letter location) the army being convoyed is going.
        convoy_from: Where (3 letter location) the convoyed army is coming from.
        '''

        channel = inter.channel_id
        user = str(inter.author.id)

        try:
            gamedoc = mo.submit_order(name, channel, user, 'CONVOY', fleet_location, convoy_to, convoy_from, 'F')
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)

    @commands.slash_command(dm_permission=False)
    async def lock(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_ongoing_games)
    ):
        channel = inter.channel_id
        user = str(inter.author.id)

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
        name: str = commands.Param(autocomplete=auto.autocomp_ongoing_games)
    ):
        channel = inter.channel_id
        user = str(inter.author.id)

        try:
            gamedoc = mo.unlock(name, channel, user)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)
    
    @commands.slash_command(dm_permission=False)
    async def retreat(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_user_games),
        from_location: str = commands.Param(autocomplete=auto.autocomp_retreat_locations),
        to_retreat: str = commands.Param(autocomplete=auto.autocomp_retreat_possibilities)
    ):
        user = str(inter.author.id)
        channel = inter.channel_id

        try:
            gamedoc = mo.retreat(name, channel, user, from_location, to_retreat)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)
    
    @commands.slash_command(dm_permission=False)
    async def supply(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_user_games),
        add_or_remove: str = commands.Param(choices=['ADD','REMOVE']),
        location: str = commands.Param(autocomplete=auto.autocomp_control_locations),
        unit: str = commands.Param(choices=['A','F'])
    ):
        if add_or_remove == 'ADD':
            remove = False
        else:
            remove = True

        user = str(inter.author.id)
        channel = inter.channel_id

        try:
            gamedoc = mo.supply(name, channel, user, location, remove, unit)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed, file=file, ephemeral=True)
