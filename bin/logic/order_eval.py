from . import game_vars as gv

def valid_order(gamedoc, player, order, fromloc, toloc, targetloc, unit):
    country = gamedoc['state'][player]
    armies = country['armies']
    navies = country['navies']

    land = gv.game_map['LAND']
    sea = gv.game_map['SEA']
    locked = gv.game_map['LANDLOCKED']

    if fromloc not in land+sea:
        return f'{fromloc} is not a valid location code'
    if toloc not in land+sea :
        return f'{toloc} is not a valid location code'
    if ((order == 'SUPPORT' or order == 'CONVOY') and targetloc not in land+sea):
        return f'{targetloc} is not a valid location code'

    if fromloc not in armies + navies:
        return 'You do not have a unit stationed in that location.'
    
    adjacency = gv.game_map['adjacency'][fromloc]
    toloc_adjacency = gv.game_map['adjacency'][toloc]
    if toloc not in adjacency and order != 'HOLD':
        if order != 'MOVE':
            return f'{fromloc} and {toloc} are not adjacent.'
        if toloc in locked or fromloc in locked:
            return f'{fromloc} and {toloc} are not adjacent and cannot be connected via convoy.'
        
    if (order == 'SUPPORT'):
        if targetloc not in adjacency:
            return f'{fromloc} and {targetloc} are not adjacent.'
        if targetloc not in toloc_adjacency:
            return f'{toloc} and {targetloc} are not adjacent.'
    
    if order == 'MOVE':
        if fromloc in armies and toloc not in land:
            return f'The unit at {fromloc} is an army. It can only move to other land provinces.'
        if fromloc in navies and toloc not in sea:
            return f'The unit at {fromloc} is a navy. It can only move to other sea provinces.'
    
    if order == 'HOLD':
        if fromloc != toloc:
            return f'You cannot hold a unit from {fromloc} to {toloc}. Both submitted locations must be {fromloc}'

def evaluate_orders(gamedoc):

    # fucking hell
    order_queue = gamedoc['next_orders']