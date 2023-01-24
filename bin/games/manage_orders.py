import json
import os
from logic import game_vars as gv, order_eval as oeval
from . import manage_games as mg
from filelock import FileLock as fl
from dbs import games_db as gdb

def submit_order(name, channel, player, order, fromloc, toloc, targetloc, unit):

    gamedoc = gdb.get_game(name, channel)

    if player not in gamedoc['currently_playing'].keys():
        raise Exception('You aren\'t currently playing in this game')

    if gamedoc['season'] == 'winter' or gamedoc['retreating']:
        raise Exception('Not currently in Spring or Fall, cannot submit orders in seasons that aren\'t Spring or Fall!')

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

    result = gdb.update_game(gamedoc)
    if result == gamedoc:
        return result
    else:
        raise Exception('There was an error attempting to save the gamestate.')
    
def lock(name, channel, player):
    gamedoc = gdb.get_game(name, channel)


    if player not in gamedoc['currently_playing'].keys():
        raise Exception('You aren\'t currently playing in this game')

    country = gamedoc['currently_playing'][player]
    if gamedoc['locked'][country]:
            raise Exception(f'You\'ve already locked your orders in this game.')

    gamedoc['locked'][country] = True

    result = gdb.update_game(gamedoc)
    if result == gamedoc:
        return result
    else:
        raise Exception('There was an error attempting to save the gamestate.')

def unlock(name, channel,player):
    gamedoc = gdb.get_game(name, channel)

    if player not in gamedoc['currently_playing'].keys():
        raise Exception('You aren\'t currently playing in this game')

    country = gamedoc['currently_playing'][player]
    if not gamedoc['locked'][country]:
        raise Exception(f'Your orders are not currently locked in this game.')

    gamedoc['locked'][country] = False

    result = gdb.update_game(gamedoc)
    if result == gamedoc:
        return result
    else:
        raise Exception('Something went wrong trying to update the gamestate.')

def retreat(name, channel, player, fromloc, toloc):
    gamedoc = gdb.get_game(name, channel)
    
    if player not in gamedoc['currently_playing'].keys():
        raise Exception('You aren\'t currently playing in this game')
    
    country = gamedoc['currently_playing'][player]

    for r in gamedoc['retreats']:
        found=False
        if r['country'] == country and r['from'] == fromloc:
            if toloc not in r['possible']:
                raise Exception(f'Cannot retreat to that location. Must retreat to: {r["possible"]}.')
            else:
                gamedoc['retreats'].remove(r)
                if r['unit'] == 'A':
                    gamedoc['state'][country]['armies'].append(toloc)
                else:
                    gamedoc['state'][country]['fleets'].append(toloc)
                found=True
    
    if not found:
        raise Exception(f'There is no required retreat for the unit at {fromloc}.')
    
    result = gdb.update_game(gamedoc)
    if result == gamedoc:
        return result
    else:
        raise Exception('There was an error attempting to save the gamestate.')
    
def supply(name, channel, player, location, remove, utype):
    gamedoc = gdb.get_game(name, channel)
    
    if player not in gamedoc['currently_playing'].keys():
        raise Exception('You aren\'t currently playing in this game')
    
    country = gamedoc['currently_playing'][player]

    if remove:
        supply = {country: -1}
    else:
        supply = {country: 1}
    
    if supply not in gamedoc['supply']:
        raise Exception('You do not have an available supply of that type.')
    
    if location in gv.game_map['SEA'] and utype == 'A':
        raise Exception('Cannot add or remove an army from a sea province.')
    
    if location in gv.game_map['LANDLOCKED'] and utype == 'F':
        raise Exception('Cannot add or remove a fleet from a landlocked province.')
    
    if utype == 'A':
        u = 'armies'
    else:
        u = 'fleets'

    if remove:
        if location not in gamedoc['state'][country][u]:
            raise Exception('Your specified unit type is incorrect at that location.')
        gamedoc['state'][country][u].remove(location)
        gamedoc['supply'].remove(supply)
    else:
        if location in gamedoc['state'][country][u]:
            raise Exception('There is already a unit stationed there. Cannot add supply.')
        if location not in gamedoc['state'][country]['controls']:
            raise Exception('Supply can only be added at supply centers you control.')
        gamedoc['state'][country][u].append(location)
        gamedoc['supply'].remove(supply)
    
    result = gdb.update_game(gamedoc)
    if result == gamedoc:
        return result
    else:
        raise Exception('There was an error attempting to save the gamestate.')
