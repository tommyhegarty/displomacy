import json
import os
import glob
import random
import datetime
from logic import game_vars as gv
from filelock import FileLock as fl

data_dir = os.environ['DATA_DIR']+'/games'

def get_all_waiting_games(channel):
    names = []
    for roots, dirs, files in os.walk(data_dir):
        for ff in files:
            if str(channel) in ff:
                name = ff.split('-')[1]
                if 'waiting' in ff.split('-')[2]:
                    names.append(name)
    return names

def get_all_started_games(channel):
    names = []
    for roots, dirs, files in os.walk(data_dir):
        for ff in files:
            if str(channel) in ff:
                name = ff.split('-')[1]
                if 'waiting' not in ff.split('-')[2]:
                    names.append(name)
    return names

def get_ongoing_game(name, channel):
    if len(glob.glob(f'{data_dir}/{channel}-{name}-*.json')) == 0:
        raise Exception('There is no game of that name in this channel.')
    elif len(glob.glob(f'{data_dir}/{channel}-{name}-waiting.json')) == len(glob.glob(f'{data_dir}/{channel}-{name}-*.json')) and len(glob.glob(f'{data_dir}/{channel}-{name}-*.json')) != 0:
        raise Exception('There is no ongoing game of that name in this channel.')
    else:
        file = open(glob.glob(f'{data_dir}/{channel}-{name}-*.json')[0],'r')
        dict = json.load(file)
        file.close()

        return dict

def get_game(name, channel):
    if len(glob.glob(f'{data_dir}/{channel}-{name}-*.json')) == 0:
        raise Exception('There is no game of that name in this channel.')
    else:
        file = open(glob.glob(f'{data_dir}/{channel}-{name}-*.json')[0],'r')
        dict = json.load(file)
        file.close()

        return dict

def new_game(name, player, duration, channel):

    if not name.isalnum():
        raise Exception("Invalid characters used in game name. Only alphanumeric characters allowed, with no spaces!")
    
    if len(glob.glob(f'{data_dir}/{channel}-{name}-*.json')) != 0:
        raise Exception("A game of this name already exists in this channel.")

    gamedoc = gv.template.copy()
    gamedoc['turn_duration'] = duration
    gamedoc['name'] = name
    gamedoc['channel'] = channel
    gamedoc['players'] = [player]

    filename = f'{channel}-{name}-waiting.json'
    file = open(f'{data_dir}/{filename}', 'w')
    file.write(json.dumps(gamedoc))
    file.close()

    return gamedoc

def start_game(name, channel):

    if len(glob.glob(f'{data_dir}/{channel}-{name}-waiting.json')) == 0:
        raise Exception("A non-started game of this name doesn't exist in this channel.")

    gamedoc = get_game(name,channel)
    duration = gamedoc['turn_duration']
    players = gamedoc['players']

    if len(players) != 7:
        raise Exception("There aren't 7 players in the game. Diplomacy requires exactly 7 players!")

    current = datetime.datetime.now()
    if duration == '1 hour':
        next_turn = current + datetime.timedelta(seconds=3600)
    elif duration == '1 day':
        next_turn = current + datetime.timedelta(seconds=86400)
    else:
        next_turn = current + datetime.timedelta(seconds=720)

    playing = {}
    random.shuffle(players)
    for p in players:
        for c in gv.countries:
            playing[p] = c
            break
    
    gamedoc['currently_playing'] = playing.copy()
    gamedoc['next_turn'] = next_turn.isoformat()
    gamedoc['started'] = True
    
    filename = f'{channel}-{name}-{next_turn.isoformat()}.json'
    os.rename(f'{data_dir}/{channel}-{name}-waiting.json',f'{data_dir}/{filename}')

    file = open(f'{data_dir}/{filename}', 'w')
    file.write(json.dumps(gamedoc))
    file.close()
    
    return gamedoc

def join_game(name, channel, player):
    gamedoc = get_game(name, channel)

    if gamedoc['started']:
        raise Exception('That game has already started, you cannot join in-progress games.')
    elif player in gamedoc['players']:
        raise Exception('You\'ve already joined this game.')

    filename = f'{channel}-{name}-waiting.json'

    lock = fl(filename)
    lock.acquire()

    try:    
        gamedoc['players'].append(player)

        file = open(f'{data_dir}/{filename}', 'w')
        file.write(json.dumps(gamedoc))
        file.close()
    finally:
        return gamedoc

def leave_game(name, channel, player):
    gamedoc = get_game(name, channel)

    if gamedoc['started']:
        raise Exception('That game has already started. Perhaps you\'re trying to surrender instead?')
    elif player not in gamedoc['players']:
        raise Exception('You\'re not in this game. You cannot leave a game you have not joined.')

    filename = f'{channel}-{name}-waiting.json'

    lock = fl(filename)
    lock.acquire()

    try:
        gamedoc['players'].remove(player)
        file = open(f'{data_dir}/{filename}', 'w')
        file.write(json.dumps(gamedoc))
        file.close()

        if len(gamedoc['players']) == 0:
            delete_game(name, channel)
    finally:
        lock.release()
        return gamedoc

def delete_game(name, channel):
    filename = glob.glob(f'{data_dir}/{channel}-{name}-*.json')[0]
    try:
        os.remove(f'{filename}')
    except Exception as e:
        raise e

def surrender(name, channel, player):
    gamedoc = get_game(name, channel)
    
    next_turn = gamedoc['next_turn']
    filename = f'{channel}-{name}-{next_turn}.json'

    if not gamedoc['started']:
        raise Exception('That game hasn\'t started yet. You can only surrender in-progress games.')
    elif player not in gamedoc['players']:
        raise Exception('You cannot surrender a game you are not in.')

    lock = fl(filename)
    lock.acquire()

    try:
        country = gamedoc['currently_playing'][player]
        gamedoc['state'][country]['surrendered'] = True
        gamedoc['state'][country]['controls'] = []
        gamedoc['state'][country]['armies'] = []
        gamedoc['state'][country]['navies'] = []
        gamedoc['next_orders'][country] = []
        gamedoc['currently_playing'].remove(player)

        file = open(f'{data_dir}/{filename}', 'w')
        file.write(json.dumps(gamedoc))
        file.close()
    finally:
        lock.release()
        return gamedoc

def get_all_ready_games():
    print('nothin')
