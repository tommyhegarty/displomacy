# we're going to need:
#   parse orders
#   execute turn & post results
#   finish game state
import random
from games import manage_games as gm
from games import parse_orders as po
from games import game_vars as gv
from games import process_orders as process_orders
from players import manage_players as pm
import asyncio
from datetime import datetime, timedelta

def fail_retreats(name):
    doc = gm.get_game(name)
    retreats = doc['required_retreats']
    for country in retreats.keys():
        country_retreats = retreats[country]
        while country_retreats:
            (fromloc,available) = country_retreats.pop(0)
            toloc=available[0]
            try:
                doc['state'][country]['armies'].remove(fromloc)
                doc['state'][country]['armies'].append(toloc)
            except:
                doc['state'][country]['fleets'].remove(fromloc)
                doc['state'][country]['fleets'].append(toloc)
    doc['required_retreats']={}
    gm.update_game(doc)

def fail_supplies(name):
    doc=gm.get_game(name)
    supplies=doc['required_supply']
    for country in supplies.keys():
        supply = supplies[country]
        while (supply < 0):
            if (doc['state'][country]['armies'] != []):
                doc['state'][country]['armies'].pop(0)
            elif (doc['state'][country]['fleets'] != []):
                doc['state'][country]['fleets'].pop(0)
            supply = supply +1
    doc['required_supply']={}
    doc['year']=doc['year']+1
    doc['season']='spring'
    gm.update_game(doc)

def clear_last_orders(name):
    game_doc=gm.get_game(name)
    game_doc['last_orders']={}
    gm.update_game(game_doc)

# returns nothing
def surrender(player, game_name):
    game=gm.get_game(game_name)
    if (player not in game['currently_playing'].keys()):
        raise NameError('You are not playing in this game')
    country=game['currently_playing'][player]
    game['state'][country]['surrendered']=True
    game['state'][country]['armies']=[]
    game['state'][country]['fleets']=[]
    game['state'][country]['controls']=[]
    game['currently_playing'].pop(player)
    gm.update_game(game)

# returns nothing
def change_wincon(player, game_name, wincon):
    game=gm.get_game(game_name)
    if (player not in game['currently_playing'].keys()):
        raise NameError('You are not playing in this game')
    country=game['currently_playing'][player]
    game['state'][country]['wincon']=wincon
    gm.update_game(game)

# returns (dict) that is the game doc of the current game
def get_gamestate(player, game_name):
    game_doc=gm.get_game(game_name)
    keys=game_doc['currently_playing'].keys()
    if (player not in keys):
        raise NameError('You are not playing in this game')
    player_country=game_doc['currently_playing'][player]
    for country in gv.countries:
        if (player_country != country):
            game_doc['state'][country].pop('wincon')
            game_doc['next_orders'].pop(country)
    return game_doc

# returns (dict) that is the game template of the new game
def start_game(players, name, turn_duration):
    game_template=gv.template
    shuffled=gv.countries.copy()
    random.shuffle(shuffled)
    game_template["currently_playing"]={
        players[0]: shuffled[0],
        players[1]: shuffled[1],
        players[2]: shuffled[2],
        players[3]: shuffled[3],
        players[4]: shuffled[4],
        players[5]: shuffled[5],
        players[6]: shuffled[6]
    }
    for player in players:
        pm.add_game(player, name)

    game_template["name"]=name
    game_template["turn_duration"]=turn_duration

    now=datetime.now()
    if(turn_duration=='10 minutes'):
        turn=timedelta(minutes=10)
    elif(turn_duration=='1 hour'):
        turn=timedelta(hours=1)
    elif(turn_duration=='24 hours'):
        turn=timedelta(hours=24)
    next_turn=now+turn

    gm.new_game(game_template,next_turn)
    return game_template

# returns (array, array) that is (winners so far, currently active players)
def check_wincons(game_doc):
    winner_found=False
    non_surrendered_countries=[]
    players = game_doc['currently_playing']

    for country in gv.countries:
        num_winners=game_doc['state'][country]['wincon']
        total_control=len(game_doc['state'][country]['controls'])
        if (game_doc['state'][country]['surrendered'] == False):
            non_surrendered_countries.append((country, num_winners))
        if (num_winners == 1 and total_control > 17):
            player_position=list(players.values()).index(country)
            player=list(players.keys())[player_position]
            winner_found=True
            winners=[player]
    
    if(winner_found):
        print(f'Found a single winner, {winners[0]}')
        game_doc['next_orders']=[]
        game_doc['last_orders']=[]
        gm.update_game(game_doc)
        return (winners,players)
    # no single person has won the game, so check if a draw has been agreed upon

    agreed_draw=True
    for (country, wincon) in non_surrendered_countries:
        print(f'Wincon of {wincon} for country {country}, there are {len(non_surrendered_countries)} countries still playing.')
        if (wincon <= len(non_surrendered_countries)):
            agreed_draw = False
    winners=[]
    if (agreed_draw):
        for (country, wincon) in non_surrendered_countries:
            player_position=list(players.values()).index(country)
            player=list(players.keys())[player_position]
            winners.append(player)
    
    if(winner_found):
        game_doc['next_orders']=[]
        game_doc['last_orders']=[]
        gm.update_game(game_doc)
    return (winners, players)

# returns list of orders given game name and discord id
def get_orders(game_name, discord_id):
    game_doc=gm.get_game(game_name)
    country_code=game_doc['currently_playing'][discord_id]
    orders=game_doc['next_orders'][country_code]
    return orders

# returns value of execute turn return
def parse_orders(order_string, discord_id):

    '''
    order string looks like:
    ?orders command
    game name
    SUP A BUD RUM GAL // this order is for the army in Budapest, supporting the army in Galicia moving into Rumania
    CON F ION TUN GRE // this order is for the fleet in Ionian sea, convoying the army in Greece to move to Tunisia
    MOV A ROM APU // move orders only take 3 arguments, this moves the army in Rome to Apulia
    HOL A ROM // hold orders take two arguments, this orders the Roman army to hold
    '''
    arr=order_string.splitlines()
    # remove one line to remove command
    arr.pop(0)
    # remove line one and grab game name
    gamename_line=arr.pop(0)
    game_doc=gm.get_game(gamename_line)

    # who is this player
    season=game_doc['season']
    retreats=game_doc['required_retreats']
    if(season == 'winter'):
        raise ValueError('Supply is still ongoing')
    elif(retreats != {}):
        raise ValueError('Retreats are still being submitted')

    players=game_doc['currently_playing']
    try:
        owner=players[discord_id]
    except:
        raise KeyError('You are not playing in this game.')

    # break out the array
    formatted_orders=po.parse_orders(arr,game_doc,owner)
    game_doc['next_orders'][owner]=formatted_orders
    gm.update_game(game_doc)

    # now check if every player has orders
    game_doc=gm.get_game(gamename_line)
    if(po.all_orders_submitted(game_doc)):
        return (True, gamename_line)
    return (False, gamename_line)

# returns (dict, dict) that is (positive supply (player -> tuple of supp number and game name), negative supply (player -> tuple of supp number and game name))
def start_supply(game_doc):
    players=game_doc['currently_playing']
    name=game_doc['name']

    reinforcements_doc={}
    disbandments_doc={}

    for country in gv.countries:
        supply=game_doc['state'][country]['controls']
        units=game_doc['state'][country]['armies']+game_doc['state'][country]['fleets']
        supp_required=len(supply)-len(units)

        player_position=list(players.values()).index(country)
        player=list(players.keys())[player_position]
        if (supp_required > 0):
            game_doc['required_supply'][country]=supp_required
            reinforcements_doc[player]=(supp_required,name)
        elif (supp_required < 0):
            game_doc['required_supply'][country]=supp_required
            disbandments_doc[player]=(supp_required,name)
    
    gm.update_game(game_doc)
    return (reinforcements_doc, disbandments_doc)

# returns (boolean, dict) that is (supply completed true/false, game doc state)            
def execute_supply(player,name, addremove, unit, location):
    # string is formatted as ?supply add/remove type location

    game_doc=gm.get_game(name)
    try:
        country=game_doc['currently_playing'][player]
    except:
        raise KeyError('You are not playing in this game.')

    try:
        total_supp=game_doc['required_supply'][country]
    except:
        raise KeyError('You have no supply to fulfill.')

    if(unit != 'A' and unit != 'F'):
        raise ValueError('Not a valid unit type.')

    if (addremove == 'add'):
        if (total_supp < 0):
            raise ValueError('You cannot add reinforcements -- you are at negative supply and have to disband.')
        if (location not in game_doc['state'][country]['original']):
            raise ValueError('You cannot deploy there -- it was not a starting territory of yours.')
        if (location not in game_doc['state'][country]['controls']):
            raise ValueError('You cannot deploy there -- you no longer control that territory.')
        if (location in game_doc['state'][country]['armies'] or location in game_doc['state'][country]['fleets']):
            raise ValueError('You cannot deploy there -- a unit is already stationed.')
        if (location in gv.game_map['SEA'] and unit == 'A'):
            raise ValueError('You cannot deploy an army in the sea.')
        if (location in gv.game_map['LANDLOCKED'] and unit == 'F'):
            raise ValueError('You cannot deploy a fleet in a landlocked territory.')

        if(unit == 'F'):
            game_doc['state'][country]['fleets'].append(location)
        else:
            game_doc['state'][country]['armies'].append(location)
        
        if(total_supp-1 == 0):
            game_doc['required_supply'].pop(country)
        else:
            game_doc['required_supply'][country]=total_supp-1

    elif (addremove == 'remove'):
        if (total_supp > 0):
            raise ValueError('Why are you disbanding? You must reinforce.')
        if (location in game_doc['state'][country]['armies']):
            game_doc['state'][country]['armies'].remove(location)
        elif (location in game_doc['state'][country]['fleets']):
            game_doc['state'][country]['fleets'].remove(location)
        else:
            raise ValueError('You cannot disband in that location as you do not have a unit stationed there.')
        
        if(total_supp+1 == 0):
            game_doc['required_supply'].pop(country)
        else:
            game_doc['required_supply'][country]=total_supp+1
    else:
        raise ValueError('Invalid command.')

    if (game_doc['required_supply'] == {}):
        game_doc['year']=game_doc['year']+1
        game_doc['season']='spring'
        gm.update_game(game_doc)
        return (True, game_doc)
    
    gm.update_game(game_doc)
    return (False, game_doc)

# returns (dict) that is (game_doc after being updated)
def update_map(orders, season, game_doc):
    for order in orders:
        command = order['command']
        if (command == "MOV"):
            move_to=order['new']
            move_from=order['conflict']
            unit=order['unit_type']
            to_update=order['owner']

            if (unit == 'A'):
                unit='armies'
            else:
                unit='fleets'

            game_doc['state'][to_update][unit].remove(move_from)
            game_doc['state'][to_update][unit].append(move_to)
            if (season == 'fall' and move_to in gv.game_map['SUPPLY']):
                for country in gv.countries:
                    if(move_to in game_doc['state'][country]['controls']):
                        game_doc['state'][country]['controls'].remove(move_to)
                game_doc['state'][to_update]['controls'].append(move_to)
    game_doc['season']=season
    return game_doc

# returns (dict, dict) that is (retreats required (player -> array of retreats), units destroyed (player -> array of destroyed))
def retreat_needed(retreats, game_doc):
    retreats_req={}
    units_destroyed={}
    players = game_doc['currently_playing']
    name=game_doc['name']

    for retreat in retreats:
        unit=retreat['unit_type']
        fromloc=retreat['location']
        available=gv.game_map['adjacency'][fromloc]
        available.remove(retreat['attack_loc'])
        country=retreat['owner']

        player_position=list(players.values()).index(country)
        player=list(players.keys())[player_position]

        occupied=[]
        for country in gv.countries:
            occupied=occupied+game_doc['state'][country]['armies']+game_doc['state'][country]['fleets']
        available=[x for x in available if x not in occupied]

        if (unit == 'A'):
            available=[x for x in available if x not in gv.game_map['SEA']]
        else:
            available=[x for x in available if x not in gv.game_map['LANDLOCKED']]
        
        if (available == []):
            try:
                units_destroyed[player].append((fromloc, name))
            except:
                units_destroyed[player]=[(fromloc,name)]
        else:
            try:
                game_doc['required_retreats'][country].append((fromloc,available))
                retreats_req[player].append(fromloc)
            except:
                game_doc['required_retreats'][country]=[(fromloc,available)]
                retreats_req[player]=[fromloc]

    return (retreats_req, units_destroyed)

# no return
def end_game(game_doc):
    gm.end_game(game_doc['name'])
    for player in game_doc['currently_playing'].keys():
        pm.end_game(player, game_doc['name'])

# no return
def execute_retreat(player, name, loc_from, loc_to):

    game_doc=gm.get_game(name)
    country=game_doc['currently_playing'][player]
    try:
        available=game_doc['required_retreats'][country][loc_from]
    except:
        raise ValueError('You are not retreating from that location.')

    if(loc_to not in available):
        raise ValueError('You cannot retreat to that location.')
    
    try:
        game_doc['state'][country]['armies'].remove(loc_from)
        game_doc['state'][country]['armies'].append(loc_to)
    except:
        game_doc['state'][country]['fleets'].remove(loc_from)
        game_doc['state'][country]['fleets'].append(loc_to)

    game_doc['required_retreats'][country].pop(loc_from)
    if (game_doc['required_retreats'][country] == {}):
        game_doc['required_retreats'].pop(country)
            
    if (game_doc['required_retreats'] == 0):
        return (True, game_doc)
    
    gm.update_game(game_doc)
    return (False, game_doc)

# returns (string, tuple) where (string = result of turn ['RETREAT','SUPPLY','TURN END','GAME END'])
def execute_turn(game_name):
    game_doc=gm.get_game(game_name)

    season = game_doc['season']
    game_doc['last_orders']={}
    full_order_list=[]
    ordered_units_list=[]
    for country in gv.countries:
        country_orders = game_doc['next_orders'][country]
        for order in country_orders:
            full_order_list.append(order)
            if (order['command'] == 'MOV'):
                ordered_units_list.append(order['conflict'])
            else:
                ordered_units_list.append(order['new'])
    for country in gv.countries:
        for territory in game_doc['state'][country]['armies']+game_doc['state'][country]['fleets']:
            if (territory in game_doc['state'][country]['armies']):
                unit_type='A'
            else:
                unit_type='F'
            if territory not in ordered_units_list:
                new_order={
                    'command':'HOL',
                    'new':territory,
                    'conflict':territory,
                    'target':'',
                    'unit_type':unit_type,
                    'owner':country
                }
                full_order_list.append(new_order)
                game_doc['next_orders'][country].append(new_order)
    results=process_orders.execute_orders(full_order_list)
    successful_orders=results[0]
    retreat_required=results[1]

    if (season == 'spring'):
        new_season = 'fall'
    else:
        new_season ='winter'
    
    print(f'Successful orders are {successful_orders}')
    print(f'Retreats required are  {retreat_required}')
    game_doc=update_map(successful_orders,season,game_doc)
    game_doc['season']=new_season

    for country in gv.countries:
        game_doc['last_orders'][country]=game_doc['next_orders'][country].copy()
        game_doc['next_orders'][country]=[]
    gm.update_game(game_doc)
    
    if(retreat_required != []):
        return ('RETREAT',retreat_needed(retreat_required,game_doc))
    elif (new_season == 'winter'):
        print(f'It is winter, checking {game_doc}')
        (winners, players)=check_wincons(game_doc)
        if (winners == []):
            return ('SUPPLY', start_supply(game_doc))
        else:
            return ('GAME END',(winners,players))
    else:
        return ('TURN END',[])