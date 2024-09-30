import datetime, random
from dbs import games_db as gdb
from logic import adjudicator as adj, game_vars as gv

def game_step(gamedoc):
    gamedoc = gamedoc.copy()

    order_list = gamedoc['next_orders']
    completed = adj.Adjudicator().execute_orders(order_list)

    # need to evaluate what to do with completed orders
    gamedoc['last_orders'] = completed
    dislodged = []

    for order, success in completed:
        if not success and order['order'] == 'MOVE':
            staying_in = order['from']
            if order['unit'] == 'A':
                utype = 'armies'
            else:
                utype = 'fleets'    
            if staying_in not in gamedoc['state'][order['country']][utype]:
                gamedoc['state'][order['country']][utype].append(staying_in)

    for order, success in completed:
        dislodged_country = None
        if success and order['order'] == 'MOVE':
            dislodge_possible = order['to']
        
            for c in gv.countries:
                if dislodge_possible in gamedoc['state'][c]['armies']:
                    dislodged.append({'country': c, 'unit': 'A', 'unit_location': dislodge_possible})
                    gamedoc['state'][c]['armies'].remove(dislodge_possible)
                    dislodged_country = c
                elif dislodge_possible in gamedoc['state'][c]['fleets']:
                    dislodged.append({'country': c, 'unit': 'F', 'unit_location': dislodge_possible})
                    gamedoc['state'][c]['fleets'].remove(dislodge_possible)
                    dislodged_country = c
            
            country = order['country']
            if order['unit'] == 'A':
                utype = 'armies'
            else:
                utype = 'fleets'
            
            gamedoc['state'][country][utype].remove(order['from'])
            gamedoc['state'][country][utype].append(order['to'])

            if gamedoc['season'] == 'fall' and dislodge_possible in gv.game_map['SUPPLY']:
                gamedoc['state'][country]['controls'].append(dislodge_possible)
                gamedoc['state'][country]['supply'] = gamedoc['state'][country]['supply']+1
                if dislodged_country != None:
                    gamedoc['state'][dislodged_country]['controls'].remove(dislodge_possible)
                    gamedoc['state'][dislodged_country]['supply'] = gamedoc['state'][dislodged_country]['supply']-1
                    
    
    occupied = []
    for c, state in gamedoc['state'].items():
        occupied.append(state['armies'])
        occupied.append(state['fleets'])
    for d in dislodged:
        country = d['country']
        unit = d['unit']
        loc = d['unit_location']

        if unit == 'A':
            retreats = [r for r in gv.game_map['adjacency'][loc] if r not in gv.game_map['SEA'] and r not in occupied]
        else:
            retreats = [r for r in gv.game_map['adjacency'][loc] if r not in gv.game_map['LANDLOCKED'] and r not in occupied]
        
        if len(retreats) != 0:
            gamedoc['retreats'].append({'country': country, 'unit': unit, 'from': loc, 'possible': retreats})
    
    if gamedoc['season'] == 'fall':
        for c in gv.countries:
            curr_controlled = gamedoc['state'][c]['controls']
            while gamedoc['state'][c]['supply'] < len(curr_controlled):
                gamedoc['state'][c]['supply'] = gamedoc['state'][c]['supply']+1
                gamedoc['supply'].append({c:1})
            while gamedoc['state'][c]['supply'] > len(curr_controlled):
                gamedoc['state'][c]['supply'] = gamedoc['state'][c]['supply']-1
                gamedoc['supply'].append({c:-1})
    
    if gamedoc['supply'] != []:
        gamedoc['supplying'] = True
    if gamedoc['retreats'] != []:
        gamedoc['retreating'] = True
    
    # checking for loss
    for player, country in gamedoc['currently_playing'].items():
        if gamedoc['season'] == 'fall' and gamedoc['state'][country]['supply'] == 0:
            gamedoc['defeated'][player] = country
            gamedoc['state'][country]['surrendered']=True

    if not gamedoc['retreating'] and not gamedoc['supplying']:
        if gamedoc['season'] == 'fall':
            gamedoc['season'] = 'spring'
            gamedoc['year'] = gamedoc['year']+1
        else:
            gamedoc['season'] = 'fall'

    gamedoc['next_orders'] = []


    current = datetime.datetime.now()
    duration = gamedoc['turn_duration']
    if duration == '1 hour':
        next_turn = current + datetime.timedelta(seconds=3600)
    elif duration == '1 day':
        next_turn = current + datetime.timedelta(seconds=86400)
    else:
        next_turn = current + datetime.timedelta(seconds=720)
    gamedoc['next_turn'] = next_turn

    gamedoc['locked']={
        "AUS":False,
        "ENG":False,
        "FRA":False,
        "GER":False,
        "ITA":False,
        "RUS":False,
        "TUR":False
    }

    gdb.update_game(gamedoc)

    return gamedoc

def retreat_timeout(gamedoc):
    while gamedoc['retreats']:
        r = gamedoc['retreats'].pop()
        country = r['country']
        going = r['possible'][0]

        if r['unit'] == 'A':
            unit = 'armies'
        else:
            unit = 'fleet'

        gamedoc['state'][country][unit].append(going)
    
    gamedoc['retreating']=False
    if gamedoc['supplying']:
        gdb.update_game(gamedoc)
        return gamedoc
    else:
        if gamedoc['season'] == 'fall':
            gamedoc['season'] = 'spring'
            gamedoc['year'] = gamedoc['year']+1
        else:
            gamedoc['season'] = 'fall'

        current = datetime.datetime.now()
        duration = gamedoc['turn_duration']
        if duration == '1 hour':
            next_turn = current + datetime.timedelta(seconds=3600)
        elif duration == '1 day':
            next_turn = current + datetime.timedelta(seconds=86400)
        else:
            next_turn = current + datetime.timedelta(seconds=720)
        gamedoc['next_turn'] = next_turn

        gdb.update_game(gamedoc)

        return gamedoc

def supply_timeout(gamedoc):
    while gamedoc['supply']:
        (c, num) = gamedoc['supply'].pop()
        if num == -1:
            total = gamedoc['state'][c]['armies']+gamedoc['state'][c]['fleets']
            if len(total) == 1:
                gamedoc['state'][c]['armies'] = []
                gamedoc['state'][c]['fleets'] = []
            else:
                selected = total[random.randint(0,len(total)-1)]
                if selected in gamedoc['state'][c]['armies']:
                    gamedoc['state'][c]['armies'].remove(selected)
                else:
                    gamedoc['state'][c]['fleets'].remove(selected)
    
    gamedoc['supplying'] = False
    if gamedoc['season'] == 'fall':
        gamedoc['season'] = 'spring'
        gamedoc['year'] = gamedoc['year']+1
    else:
        gamedoc['season'] = 'fall'

    current = datetime.datetime.now()
    duration = gamedoc['turn_duration']
    if duration == '1 hour':
        next_turn = current + datetime.timedelta(seconds=3600)
    elif duration == '1 day':
        next_turn = current + datetime.timedelta(seconds=86400)
    else:
        next_turn = current + datetime.timedelta(seconds=720)
    gamedoc['next_turn'] = next_turn

    gdb.update_game(gamedoc)

    return gamedoc    