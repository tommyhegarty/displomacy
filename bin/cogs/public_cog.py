import disnake
from disnake.ext import commands
from games import manage_games as mg
from . import message_util as mu
from logic import autocompleters as auto

class public_cog(commands.Cog):

    @commands.slash_command(dm_permission=False)
    async def new(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(max_length=25),
        duration: str = commands.Param(choices=['20 minutes','1 hour','1 day'])
    ):
        '''
        Start a new game in a channel! It will be open to all channel users.

        Parameters
        ----------
        name: The name of the game you're starting. Unique, alphanumeric, no spaces, 25 chars or less.
        duration: The duration of the game's turns. Options are 20 minutes, 1 hour, and 1 day.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)
        try:
            gamedoc = mg.new_game(name, user, duration, channel)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc)
            await inter.send(embed = embed, file=file)

    @commands.slash_command(dm_permission=False)
    async def view(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_all_games)
    ):
        channel = inter.channel_id
        user = str(inter.author.id)

        try:
            gamedoc = mg.get_game(name, channel)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc, user)
            await inter.send(embed=embed,file=file)
    
    @commands.slash_command(dm_permission=False)
    async def gamelist(
        inter: disnake.ApplicationCommandInteraction
    ):
        '''
        See all the existing (started and waiting) games in this channel.
        '''
        await inter.send(await auto.autocomp_all_games(inter,""))

    @commands.slash_command(dm_permission=False)
    async def join(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_waiting_games)
    ):
        '''
        Join a lobby in this channel to play Diplomacy!

        Parameters
        ----------
        name: The name of the game you're joining.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)
        try:
            gamedoc = mg.join_game(name, channel, user)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc)
            await inter.send(content=f'<@{user}> has joined the game.', embed=embed, file=file)
    
    @commands.slash_command(dm_permission=False)
    async def leave(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_waiting_games)
    ):
        '''
        Leave a game you're currently in before the game starts.

        Parameters
        ----------
        name: The name of the unstarted game you're leaving
        '''
        channel = inter.channel_id
        user = str(inter.author.id)
        try:
            gamedoc = mg.leave_game(name, channel, user)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed= embed, ephemeral=True, delete_after=120)
        else:
            if gamedoc == None:
                await inter.send(f'<@{user}> has left the game ***{name}***, leaving no players in the lobby. The game has been deleted.')
            else:
                (embed, file) = mu.build_game_message(gamedoc)
                await inter.send(f'<@{user}> has left the game.', embed=embed, file=file)

    @commands.slash_command(dm_permission=False)
    async def start(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_waiting_games),
    ):
        '''
        Start a game when all players have joined!

        Parameters
        ----------
        name: The name of the game you're starting. Unique, alphanumeric, no spaces, 25 chars or less.
        duration: The duration of the game's turns. Options are 20 minutes, 1 hour, and 1 day.
        '''
        channel = inter.channel_id
        user = str(inter.author.id)
        try:
            gamedoc = mg.start_game(name, channel, user)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed, ephemeral=True, delete_after=120)
        else:
            (embed, file) = mu.build_game_message(gamedoc)
            await inter.send(embed = embed, file=file)
    
    @commands.slash_command(dm_permission=False)
    async def surrender(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(autocomplete=auto.autocomp_ongoing_games)
    ):
        '''
        Admit defeat in an ongoing game. This must be done publicly!

        Parameters
        ----------
        name: The name of the in-progress game you're surrendering
        '''
        channel = inter.channel_id
        user = str(inter.author.id)

        try:
            mg.surrender(name, channel, user)
        except Exception as e:
            embed = mu.build_error_message(e)
            await inter.send(embed=embed,ephemeral=True,delete_after=120)