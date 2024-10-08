import boto3, cfg, datetime
import boto3.dynamodb.conditions as con
from botocore.exceptions import ClientError

#game={
#   'channel':'',
#   'all_players':[],
#   'active_players':[],
#   'started':'',
#   'locked':[],
#   'turn_length':'',
#   'next_turn':''
#   'orders':{
#       'player':{'location':'order'}
#   }
#}

time_map={
    '1h': datetime.timedelta(hours=1),
    '20m': datetime.timedelta(minutes=20),
    '1d': datetime.timedelta(days=1)
}

def __get_game(channel):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    item=ddb.get_item(
        Key={'channel':channel}
    ).get('Item','')
    if item == '':
        raise KeyError
    return item

def __new_game(channel, player, turn_length):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    ddb.put_item(
        Item={
            'channel':channel,
            'all_players':[player],
            'active_players':[],
            'started':False,
            'locked':[],
            'turn_length':turn_length,
            'next_turn':'',
            'current_turn':'Spring 1900'
        },
        ConditionExpression=con.Not(con.Attr('channel').exists())
    )

def __join_game(channel, player):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    ddb.update_item(
        Key={'channel':channel},
        ExpressionAttributeNames={'#ap':'all_players'},
        ExpressionAttributeValues={':p':[player]},
        UpdateExpression='SET #ap = list_append(#ap,:p)'
    )

def __set_player_list(channel, player_list):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    ddb.update_item(
        Key={'channel':channel},
        ExpressionAttributeNames={'#ap':'all_players'},
        ExpressionAttributeValues={':p':player_list},
        UpdateExpression='SET #ap = :p'
    )

def __close_game(channel):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    ddb.delete_item(
        Key={'channel':channel}
    )

def create_new_game(channel, player, turn_length):
    now=datetime.datetime.now()
    delta=time_map[turn_length]
    next_turn=now+delta
    try:
        __new_game(channel,player,turn_length,next_turn)
    except ClientError as err:
        print(f'failed to create new game in game {channel} with player {player} because one already exists: {err}')
        raise KeyError
    except Exception as err:
        print(f'failed to create new game in game {channel} with player {player} with unknown {err}')
        raise err

def join_existing_game(channel, player):
    try:
        game_info=__get_game(channel)
        all_players=game_info.get('all_players')
        if game_info.get('started'):
            raise ValueError(f'Game {channel} cannot be joined by player {player} because it has already started.')
        if len(all_players) == 7:
            raise ValueError(f'Game {channel} cannot be joined by player {player} because it is full.')
        if player in all_players:
            raise ValueError(f'Player {player} is already in game {channel}')
        __join_game(channel,player)
        return all_players.append(player)
    except KeyError:
        print(f'There is no game in {channel}')
        raise KeyError(f'There is no game in {channel}')
    except ValueError as err:
        print(err)
        raise err
    except Exception as err:
        print(f'unknown error joining game {channel} with player {player}, threw {err}')
        raise err

def leave_unstarted_game(channel, player):
    try:
        game_info=__get_game(channel)
        all_players=game_info.get('all_players')
        if game_info.get('started'):
            raise ValueError(f'Game {channel} cannot be left by player {player} because it has already started; try /surrender.')
        if player not in all_players:
            raise ValueError(f'Player {player} is not in game {channel}.')
        if all_players == [player]:
            print(f'Player {player} is the last player left in the lobby; closing the game {channel}.')
            __close_game(channel)
        else:
            print(f'Removing player {player} from waiting list of players for game {channel}.')
            __set_player_list(channel, all_players.remove(player))
    except KeyError:
        print(f'Game {channel} does not exist.')
        raise KeyError(f'Game {channel} does not exist.')
    except ValueError as err:
        print(err)
        raise err
    except Exception as err:
        print(f'Player {player} leaving game {channel} failed with error {err}')
        raise err