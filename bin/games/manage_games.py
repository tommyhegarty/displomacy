import json
import os
import glob
import random
import datetime
from dbs import games_db as gdb
from logic import game_vars as gv

def get_all_waiting_games(channel):
    gamedocs = gdb.search_games({'channel': channel, 'started': True})
    return [g['name'] for g in gamedocs if not gamedocs['started']]

def get_all_started_games(channel):
    gamedocs = gdb.search_games({'channel': channel, 'started': True})
    return [g['name'] for g in gamedocs if gamedocs['started']]

def get_ongoing_game(name, channel):
    try:
        gamedoc = gdb.get_game(name, channel)
    except Exception as e:
        raise e
    else:
        if gamedoc['started']:
            return gamedoc
        else:
            raise Exception('The game of that name is not yet started!')

def get_waiting_game(name, channel):
    try:
        gamedoc = gdb.get_game(name, channel)
    except Exception as e:
        raise e
    else:
        if not gamedoc['started']:
            return gamedoc
        else:
            raise Exception('The game of that name is already started!')

def get_game(name, channel):
    return gdb.get_game(name, channel)

def new_game(name, player, duration, channel):

    if not name.isalnum():
        raise Exception("Invalid characters used in game name. Only alphanumeric characters allowed, with no spaces!")
    
    if get_game(name, channel) != None:
        raise Exception("A game of this name already exists in this channel.")

    gamedoc = gv.template.copy()
    gamedoc['_id'] = {
        'name': name,
        'channel': channel
    }
    gamedoc['turn_duration'] = duration
    gamedoc['name'] = name
    gamedoc['channel'] = channel
    gamedoc['players'] = [player]

    result = gdb.add_game(gamedoc)

    if result == gamedoc:
        return gamedoc
    else:
        raise Exception('Something other than the game state was added to the db! What a horrible tragedy.')

def start_game(name, channel):

    gamedoc = get_waiting_game(name, channel)
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
    gamedoc['next_turn'] = next_turn
    gamedoc['started'] = True
    
    result = gdb.update_game(gamedoc)
    if result == gamedoc:
        return gamedoc
    else:
        raise Exception(f'The modification does not match the updated state. Something is wrong!')

def join_game(name, channel, player):
    gamedoc = get_game(name, channel)

    if gamedoc['started']:
        raise Exception('That game has already started, you cannot join in-progress games.')
    elif player in gamedoc['players']:
        raise Exception('You\'ve already joined this game.')

    
    gamedoc['players'].append(player)
    result = gdb.update_game(gamedoc)
    if result == gamedoc:
        return gamedoc
    else:
        raise Exception(f'The modification does not match the updated state. Something is wrong!')

def leave_game(name, channel, player):
    gamedoc = get_game(name, channel)

    if gamedoc['started']:
        raise Exception('That game has already started. Perhaps you\'re trying to surrender instead?')
    elif player not in gamedoc['players']:
        raise Exception('You\'re not in this game. You cannot leave a game you have not joined.')

    if len(gamedoc['players']) == 1:
        result = gdb.delete_game(name, channel)
        if result == gamedoc:
            return None
        else:
            raise Exception(f'Something has been deleted that is NOT the game! Not ideal.')
    else:
        result = gdb.update_game(gamedoc)
        if result == gamedoc:
            return gamedoc
        else:
            raise Exception(f'The modification does not match the updated state. Something is wrong!')

def surrender(name, channel, player):
    gamedoc = get_game(name, channel)
    
    if not gamedoc['started']:
        raise Exception('That game hasn\'t started yet. You can only surrender in-progress games.')
    elif player not in gamedoc['players']:
        raise Exception('You cannot surrender a game you are not in.')

    
    country = gamedoc['currently_playing'][player]
    gamedoc['state'][country]['surrendered'] = True
    gamedoc['state'][country]['controls'] = []
    gamedoc['state'][country]['armies'] = []
    gamedoc['state'][country]['navies'] = []
    gamedoc['next_orders'][country] = []
    gamedoc['currently_playing'].remove(player)

    result = gdb.update_game(gamedoc)
    if result == gamedoc:
        return gamedoc
    else:
        raise Exception(f'The modification does not match the updated state. Something is wrong!')

def get_all_ready_games():
    now = datetime.datetime.now()
    time_up = gdb.search_games({'next_turn': {"$lte": now}})
    all_locked = gdb.search_games({'locked': {
        "AUS":True,
        "ENG":True,
        "FRA":True,
        "GER":True,
        "ITA":True,
        "RUS":True,
        "TUR":True
    }})
    done_retreating = gdb.search_games({'retreating': True, 'retreats': []})
    done_supplying = gdb.search_games({'supplying': True, 'supply': []})
    deduped = list(dict.fromkeys(time_up+all_locked+done_retreating+done_supplying))

    return deduped
