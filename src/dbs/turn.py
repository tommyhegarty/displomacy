import boto3, cfg
import boto3.dynamodb.conditions as con
from botocore.exceptions import ClientError

# turn = {
#   'channel'='',
#   'turn'='',
#   'players':[],
#   'history'={
#       'player'={
#           'country'='',
#           'submitted_orders'=[],
#           'successful_orders'=[]
#       }
#   }
#}

def __submit_turn(channel, turn, history, players):
    ddb=boto3.resource('dynamodb').Table(cfg.turn_table)
    ddb.put_item(
        Item={
            'channel': channel,
            'turn':turn,
            'players':players,
            'history':history
        }
    )

def __get_turn_history(channel,turn):
    ddb=boto3.resource('dynamodb').Table(cfg.turn_table)
    response=ddb.get_item(
        Key={'channel':channel,'turn':turn}
    )
    result=response.get('Item','')
    if result == '':
        raise KeyError
    return result

def __get_game_history(channel):
    ddb=boto3.resource('dynamodb').Table(cfg.turn_table)
    response=ddb.query(
        ExpressionAttributeValues={':channel':channel},
        KeyConditionExpression='channel = :channel'
    )
    result=response.get('Items','')
    if result == '':
        raise KeyError
    return result

def get_player_full_history(channel,player):
    try:
        items=__get_game_history(channel)
        total_players=[x['players'] for x in items]
        if player not in total_players:
            raise ValueError
        
    except KeyError:
        print(f'the game {channel} does not have a turn history')
    except ValueError:
        print(f'the player {player} is not in game {channel}')
    except Exception as err:
        print(f'could not get all history from game {channel} with {err}')
    else:
        result={}
        for turn in items:
            result[turn['turn']]=turn['history'][player]
        if result == {}:
            print(f'player {player} does not have a history in game {channel}')
        else:
            return result

def get_player_turn_history(channel,player,turn):
    try:
        items=__get_turn_history(channel,turn)
        if player not in items['players']:
            raise ValueError
    except KeyError:
        print(f'the game {channel} does not have a history for turn {turn}')
    except ValueError:
        print(f'the player {player} does not have a history in game {channel} for turn {turn}')
    except Exception as err:
        print(f'trying to get turn history for player {player} in game {channel} for turn {turn} failed with {err}')
    else:
        return items['history'][player]
    
def get_game_full_history(channel):
    try:
        items=__get_game_history(channel)     
    except KeyError:
        print(f'the game {channel} does not have a turn history')
    except Exception as err:
        print(f'could not get all history from game {channel} with {err}')
    else:
        result={}
        for turn in items:
            result[turn['turn']]=turn['history']
        return result

def get_game_turn_history(channel,turn):
    try:
        item=__get_turn_history(channel,turn)
    except KeyError:
        print(f'the game {channel} does not have a turn history for turn {turn}')
    except Exception as err:
        print(f'could not get all history from game {channel} with {err}')
    else:
        return item['history']

def complete_turn(channel, turn, history):
    players=history.keys()
    try:
        __submit_turn(channel, turn, history, players)
    except Exception as err:
        print(f'saving turn history {turn} for channel {channel} failed with error {err}')