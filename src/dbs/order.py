import boto3, cfg
import boto3.dynamodb.conditions as con
from botocore.exceptions import ClientError

# no longer its own table
# now uses the game table to track all orders

#game={
#   'channel':'',
#   'all_players':[],
#   'active_players':[],
#   'started':'',
#   'locked':[],
#   'turn_length':'',
#   'next_turn':''
#   'orders':{
#       'player':{'location':{order contents}}
#   }
#}

def __submit_order(id, channel, order, location):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    ddb.update_item(
        Key={'channel':channel},
        ExpressionAttributeNames={
            '#o':'orders',
            '#p':id,
            '#l':location
        },
        ExpressionAttributeValues={
            ':o':order
        },
        UpdateExpression='SET #o.#p.#l TO :o'
    )

def __get_orders(id, channel):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    response=ddb.get_item(Key={'channel':channel})
    item=response.get('Item','')
    if item == '':
        raise KeyError(f'GAME')
    
    if not item.get('started'):
        raise TypeError('game not started yet')

    players=item.get('active_players','')
    if players == '' or id not in players:
        raise KeyError(f'PLAYER')

    orders=item.get('orders','').get(id)    
    return orders

def __set_lock(id,channel,bool):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    ddb.update_item(
        Key={'channel':channel},
        ExpressionAttributeNames={
            '#l':'locked',
            '#o':'orders',
            '#p':id
        },
        ExpressionAttributeValues={':l':bool},
        UpdateExpression='SET #o.#p.#l = :l',
        ConditionExpression=con.Attr('started').eq(True)
    )

def __get_all_orders(channel):
    ddb=boto3.resource('dynamodb').Table(cfg.game_table)
    response = ddb.get_item(
        Key={'channel':channel}
    )
    item=response.get('Items','')
    if item == '':
        raise KeyError(f'no game {channel}')
    
    if not item.get('started'):
        raise TypeError(f'Game {channel} not started.')
    
    return item.get('orders')
    
def submit_order(id, channel, order):
    try:
        orders=__get_orders(id, channel)
        if orders.get('locked',''):
            raise ValueError
        __submit_order(id, channel, order, order.get('location'))
    except KeyError as err:
        if err == 'GAME':
            raise KeyError(f'There is no game {channel}.')
        elif err == 'PLAYER':
            raise KeyError(f'Player {id} is not an active player in game {channel}.')
        else:
            raise err
    except TypeError:
        print(f'Game {channel} has not started yet.')
        raise TypeError(f'Game {channel} has not started yet.')
    except ValueError:
        # there was a lock on these orders
        print(f'could not submit order {order} for player {id} in game {channel} because the orders are locked.')
        raise ValueError(f'Player {id} has locked their orders for game {channel} and so cannot submit.')
    except Exception as err:
        # unknown and unexpected error has been thrown
        print(f'submitting order {order} for player {id} in game {channel} threw error {err}')
        raise err

def lock_orders(id, channel):
    try:
        __set_lock(id,channel,True)
    except ClientError as err:
        if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f'Game {channel} not yet started.')
            raise TypeError(f'Game {channel} not yet started.')
        else:
            raise err
    except Exception as err:
        print(f'locking orders for player {id} in game {channel} failed with {err}')

def unlock_orders(id, channel):
    try:
        __set_lock(id,channel,False)
    except ClientError as err:
        if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f'Game {channel} not yet started.')
            raise TypeError(f'Game {channel} not yet started.')
        else:
            raise err
    except Exception as err:
        print(f'unlocking orders for player {id} in game {channel} failed with {err}')

def get_player_orders(id,channel):
    try:
        orders=__get_orders(id,channel)
    except KeyError as err:
        if err == 'GAME':
            print(f'Game {channel} does not exist.')
            raise KeyError(f'Game {channel} does not exist.')
        elif err == 'PLAYER':
            print(f'Player {id} is not active in game {channel}.')
            raise KeyError(f'Player {id} is not active in game {channel}.')
    except Exception as err:
        print(f'getting all orders for player {id} in game {channel} failed with {err}')
        raise err
    else:
        result=[]
        for key in orders.keys():
            result.append(orders.get(key))
        return result

def get_all_game_orders(channel):
    try:
        orders=__get_all_orders(channel)
        return orders
    except KeyError:
        print(f'no game {channel} exists to get orders from')
        raise KeyError(f'Game {channel} does not exist.')
    except TypeError:
        print(f'Game {channel} has not started yet.')
        raise TypeError(f'Game {channel} has not started yet.')
    except Exception as err:
        print(f'getting all orders for game {channel} failed with {err}')
        raise err