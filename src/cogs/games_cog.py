import disnake
from disnake.ext import commands
from dbs import game as g, player as p
from . import responses as r

class games_cog(commands.Cog):

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
        channel = str(inter.channel_id)
        user = str(inter.author.id)
        
        try:
            g.create_new_game(channel, user, duration)
        except KeyError:
            await r.respond_privately(inter,f'Could not create a new game -- one already exists in this channel! Try to /join it instead.')
            return
        except Exception as err:
            await r.respond_privately(inter,f'Failed to create a new game with unrecognized exception: {type(err)}.')
            return
        else:
            try:
                p.player_join_game(user, channel)
            except Exception as err:
                g.leave_unstarted_game(channel,user)
                await r.respond_privately(inter,f'There was a problem registering the new game to your player profile: {type(err)}')
                return
        
        await r.respond(inter,f'@{user} created a new game in the channel: [#{channel}]. Join this game by typing /join; once 6 more players join, the game will begin!')

    @commands.slash_command(dm_permission=False)
    async def join(
        inter: disnake.ApplicationCommandInteraction,
    ):
        '''
        Join a game in this channel to play Diplomacy!
        '''
        channel = str(inter.channel_id)
        user = str(inter.author.id)

        try:
            total_players=g.join_existing_game(channel, user)
        except KeyError:
            await r.respond_privately(inter,f'There is no game in this channel. Try /new instead!')
            return
        except ValueError as err:
            await r.respond_privately(err)
            return
        except Exception as err:
            await r.respond_privately(inter,f'Failed to join the game with unknown error: {type(err)}')
            return
        else:
            try:
                p.player_join_game(user, channel)
            except Exception as err:
                g.leave_unstarted_game(channel,user)
                await r.respond_privately(inter,f'')

        if len(total_players) < 7:
            stringified=[]
            for i in total_players:
                stringified.append(f'@{i}')
            await r.respond(inter, f'@{user} has joined the game in: [#{channel}]. The players now are: {stringified}')
        else:
            # start the game here
            await r.respond(inter, f'@{user} has joined the game -- there are enough players to begin the game!')
    
    @commands.slash_command(dm_permission=False)
    async def leave(
        inter: disnake.ApplicationCommandInteraction,
    ):
        '''
        Leave a game you're currently in before the game starts.
        '''
        channel = str(inter.channel_id)
        user = str(inter.author.id)
        
        try:
            players_left=g.leave_unstarted_game(channel, user)
        except ValueError as err:
            await r.respond_privately(inter, err)
        except KeyError as err:
            await r.respond_privately(inter, f'There is no game in this channel! Use /new to create one.')
        except Exception as err:
            await r.respond_privately(inter, f'There has been an unknown error trying to leave the game: {type(err)}')
        else:
            if players_left == []:
                await r.respond(f'The last player, @{user}, has left the lobby. The game has now closed. Use /new to create a new game in this channel.')
            else:
                await r.respond(f'Player @{user} has left the game. There are now {len(players_left)} players waiting to start.')
        
    
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
        channel = str(inter.channel_id)
        user = str(inter.author.id)

        print(f'surrender submitted for {user} in {channel}')