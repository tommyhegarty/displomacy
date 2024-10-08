import boto3, cfg
import boto3.dynamodb.conditions as con
from botocore.exceptions import ClientError
import boto3.dynamodb

def __player_setter(id,game):
    ddb=boto3.resource('dynamodb').Table(cfg.player_table)
    ddb.put_item(Item={'id':id,'active_games':[game]})

def __player_getter(id):
    ddb=boto3.resource('dynamodb').Table(cfg.player_table)
    response=ddb.get_item(Key={'id':id})
    result=response.get('Item','')
    if result == '':
        raise KeyError
    else:
        return result

def __add_game(id, game):
    ddb=boto3.resource('dynamodb').Table(cfg.player_table)
    ddb.update_item(
        TableName=cfg.player_table,
        Key={'id':id},
        ExpressionAttributeNames={'#ag':'active_games'},
        ExpressionAttributeValues={':a':[game]},
        UpdateExpression='SET #ag = list_append(#ag, :a)',
        ConditionExpression=con.Attr('id').exists()
    )

def __update_game_list(id, game_list):
    ddb=boto3.resource('dynamodb').Table(cfg.player_table)
    ddb.update_item(
        TableName=cfg.player_table,
        Key={'id':id},
        ExpressionAttributeNames={'#ag':'active_games'},
        ExpressionAttributeValues={':a':game_list},
        UpdateExpression=f'SET #ag = :a',
        ConditionExpression=con.Attr('id').exists()
    )

def player_join_game(id, channel):
    try:
        print(f'attempting to add game {channel} to player {id}')
        game_list=__player_getter(id).get('active_games')
        if channel in game_list:
            raise TypeError
        else:
            __add_game(id,channel)        
    except KeyError:
        print(f'the player {id} does not exist, starting a new player with active game {channel}')
        __player_setter(id, channel)
    except TypeError:
        print(f'player {id} is trying to join {channel}, which they are already in')
    except boto3.client('dynamodb').exceptions.ResourceNotFoundException as err:
        print(f'could not find the table {cfg.player_table}, this is catastrophic: {err}.')
    except Exception as err:
        print(f'unknown error {err}')

def get_player_games(id):
    try:
        item=__player_getter(id)
    except KeyError:
        print(f'player {id} does not exist in the database')
    except Exception as err:
        print(f'getting games for {id} threw uncaught error {err}')
    else:
        return item.get('active_games')

def player_finish_game(id, channel):
    try:
        print(f'attempting to remove game {channel} from player {id}')
        game_list=__player_getter(id).get('active_games')
        if channel not in game_list:
            raise TypeError
        else:
            game_list.remove(channel)
            __update_game_list(id, game_list)
    except KeyError:
        print(f'player with {id} does not exist, so cannot finish game')
    except TypeError:
        print(f'player {id} is trying to leave game {channel}, which they are not in')
    except Exception as err:
        print(f'player {id} failed to leave game {channel} for reason {err}')