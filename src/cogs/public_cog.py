import disnake
from disnake.ext import commands
from games import manage_games as mg
from . import message_util as mu
from logic import autocompleters as auto

class public_cog(commands.Cog):

    @commands.slash_command(dm_permission=False)
    async def new(
        inter: disnake.ApplicationCommandInteraction,
        duration: str = commands.Param(choices=['20 minutes','1 hour','1 day'])
    ):
        '''
        Start a new game in a channel! It will be open to all channel users.

        Parameters
        ----------
        duration: The duration of the game's turns. Options are 20 minutes, 1 hour, and 1 day.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)
        
        print(f'new game submitted by {user} in {channel}')

    @commands.slash_command(dm_permission=False)
    async def view(
        inter: disnake.ApplicationCommandInteraction,
    ):
        channel = inter.channel_id
        user = str(inter.author.id)

        print(f'view submitted for {user} in {channel}')

    @commands.slash_command(dm_permission=False)
    async def join(
        inter: disnake.ApplicationCommandInteraction,
    ):
        '''
        Join a game in this channel to play Diplomacy!
        '''
        channel = inter.channel_id
        user = str(inter.author.id)
        
        print(f'join submitted for {user} in {channel}')
    
    @commands.slash_command(dm_permission=False)
    async def leave(
        inter: disnake.ApplicationCommandInteraction,
    ):
        '''
        Leave a game you're currently in before the game starts.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)
        
        print(f'leave submitted for {user} in {channel}')
    
    @commands.slash_command(dm_permission=False)
    async def surrender(
        inter: disnake.ApplicationCommandInteraction,
    ):
        '''
        Admit defeat in an ongoing game. This must be done publicly!

        Parameters
        ----------
        name: The name of the in-progress game you're surrendering
        '''
        channel = inter.channel_id
        user = str(inter.author.id)

        print(f'surrender submitted for {user} in {channel}')