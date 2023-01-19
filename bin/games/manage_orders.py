import json
import os
from logic import game_vars as gv, order_eval as oeval
from . import manage_games as mg
from filelock import FileLock as fl

data_dir = os.environ['DATA_DIR']+'/games'

def submit_order(name, channel, player, order, fromloc, toloc, targetloc, unit):

    gamedoc = mg.get_ongoing_game(name, channel)
    next_turn = gamedoc['next_turn']
    filename = f'{channel}-{name}-{next_turn}.json'

    lock = fl(filename)
    lock.acquire()

    try:
        if player not in gamedoc['currently_playing'].keys():
            raise Exception('You aren\'t currently playing in this game')

        reason = oeval.valid_order(gamedoc, player, order, fromloc, toloc, targetloc, unit)
        if reason != 'valid':
            raise Exception(f'That order is invalid: {reason}')

        country = gamedoc['currently_playing'][player]
        order = {
            'order': order,
            'from': fromloc,
            'to': toloc,
            'sup': targetloc,
            'country': country,
            'unit': unit
        }

        gamedoc['next_orders'] = [c for c in gamedoc['next_orders'] if (c['from'] is not fromloc) and (c['country'] is not country)]
        gamedoc['next_orders'].add(order)

        file = open(f'{data_dir}/{filename}', 'w')
        file.write(json.dumps(gamedoc))
        file.close()

    finally:
        lock.release()
        return gamedoc
    
def lock(name, channel, player):
    gamedoc = mg.get_ongoing_game(name, channel)
    next_turn = gamedoc['next_turn']
    filename = f'{channel}-{name}-{next_turn}.json'

    lock = fl(filename)
    lock.acquire()

    try:
        if player not in gamedoc['currently_playing'].keys():
            raise Exception('You aren\'t currently playing in this game')

        country = gamedoc['currently_playing'][player]
        if gamedoc['locked'][country]:
            raise Exception(f'You\'ve already locked your orders in this game.')

        gamedoc['locked'][country] = True

        file = open(f'{data_dir}/{filename}', 'w')
        file.write(json.dumps(gamedoc))
        file.close()

    finally:
        lock.release()
        return gamedoc

def unlock(name, channel,player):
    gamedoc = mg.get_ongoing_game(name, channel)
    next_turn = gamedoc['next_turn']
    filename = f'{channel}-{name}-{next_turn}.json'

    lock = fl(filename)
    lock.acquire()

    try:
        if player not in gamedoc['currently_playing'].keys():
            raise Exception('You aren\'t currently playing in this game')

        country = gamedoc['currently_playing'][player]
        if not gamedoc['locked'][country]:
            raise Exception(f'Your orders are not currently locked in this game.')

        gamedoc['locked'][country] = False

        file = open(f'{data_dir}/{filename}', 'w')
        file.write(json.dumps(gamedoc))
        file.close()

    finally:
        lock.release()
        return gamedoc