import disnake
from disnake.ext import commands
from logic import autocompleters as auto

class orders_cog(commands.Cog):
    
    @commands.slash_command(dm_permission=False)
    async def move(
        inter: disnake.ApplicationCommandInteraction,
        unit: str = commands.Param(choices=['F','A']),
        unit_location: str = commands.Param(autocomplete=auto.autocomp_unit_locations),
        move_to: str = commands.Param(autocomplete=auto.autocomp_unit_adjacent),
    ):
        '''
        Submit a move order for a single unit.

        Parameters
        ----------
        unit: The type of unit. Options are 'F' for Fleet and 'A' for Army
        unit_location: Where (3 letter location) the unit is located.
        move_to: Where (3 letter location) the unit is moving.
        '''

        channel = inter.channel_id
        user = str(inter.author.id)

        print(f'move order submitted for {user} in {channel}')

    @commands.slash_command(dm_permission=False)
    async def support(
        inter: disnake.ApplicationCommandInteraction,
        unit: str = commands.Param(choices=['F','A']),
        unit_location: str = commands.Param(),
        supporting_to: str = commands.Param(autocomplete=auto.autocomp_unit_adjacent),
        supporting_from: str = commands.Param(autocomplete=auto.autocomp_unit_supports)
    ):
        '''
        Submit a support order for a single unit.

        Parameters
        ----------
        unit: The type of unit. Options are 'F' for Fleet and 'A' for Army
        unit_location: Where (3 letter location) the unit is located.
        supporting_to: Where (3 letter location) the unit being supported is going.
        supporting_from: Where (3 letter location) the supported unit is currently located.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)

        print(f'support order submitted for {user} in {channel}')

    @commands.slash_command(dm_permission=False)
    async def hold(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(),
        unit: str = commands.Param(choices=['F','A']),
        unit_location: str = commands.Param(autocomplete=auto.autocomp_unit_locations)
    ):
        '''
        Submit a hold older for a single unit.

        Parameters
        ----------
        unit: The type of unit. Options are 'F' for Fleet and 'A' for Army
        unit_location: Where (3 letter location) the unit is located.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)

        print(f'hold order submitted for {user} in {channel}')

    @commands.slash_command(dm_permission=False)
    async def convoy(
        inter: disnake.ApplicationCommandInteraction,
        fleet_location: str = commands.Param(),
        convoy_to: str = commands.Param(autocomplete=auto.autocomp_unit_adjacent),
        convoy_from: str = commands.Param(autocomplete=auto.autocomp_unit_supports)
    ):
        '''
        Submit a convoy order for a fleet.

        Parameters
        ----------
        fleet_location: Where (3 letter location) the fleet is located.
        convoy_to: Where (3 letter location) the army being convoyed is going.
        convoy_from: Where (3 letter location) the convoyed army is coming from.
        '''

        channel = inter.channel_id
        user = str(inter.author.id)

        print(f'convoy order submitted for {user} in {channel}')

    @commands.slash_command(dm_permission=False)
    async def lock(
        inter: disnake.ApplicationCommandInteraction,
    ):
        channel = inter.channel_id
        user = str(inter.author.id)

        print(f'lock submitted for {user} in {channel}')

    @commands.slash_command(dm_permission=False)
    async def unlock(
        inter: disnake.ApplicationCommandInteraction,
    ):
        channel = inter.channel_id
        user = str(inter.author.id)

        print(f'unlock submitted for {user} in {channel}')
    
    @commands.slash_command(dm_permission=False)
    async def retreat(
        inter: disnake.ApplicationCommandInteraction,
        from_location: str = commands.Param(autocomplete=auto.autocomp_retreat_locations),
        to_retreat: str = commands.Param(autocomplete=auto.autocomp_retreat_possibilities)
    ):
        user = str(inter.author.id)
        channel = inter.channel_id

        print(f'retreat submitted for {user} in {channel}')
    
    @commands.slash_command(dm_permission=False)
    async def supply(
        inter: disnake.ApplicationCommandInteraction,
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

        print(f'supply submitted for {user} in {channel}')
