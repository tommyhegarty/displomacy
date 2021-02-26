# we're going to need:
#   parse orders
#   execute turn & post results
#   finish game state
import random
import manage_games as gm
import parse_orders as po
import send_notifications as sn
import game_vars as gv
import process_orders as process_orders
import manage_players as pm
import asyncio

def get_gamestate(player, game_name):
    game_doc=gm.get_game(game_name)
    if (player not in game_doc['currently_playing'].keys()):
        raise NameError('You are not playing in this game')
    player_country=game_doc['currently_playing'][player]
    for country in gv.countries:
        if (player_country != country):
            game_doc['state'][country].pop('wincon')
            game_doc['next_orders'].pop(country)
    return game_doc

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

    asyncio.run(sn.notify_game_start(game_template))
    gm.new_game(game_template)

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
            print(f'Country {country} has won the game.')
            player_position=list(players.values()).index(country)
            player=list(players.keys())[player_position]
            asyncio.run(sn.notify_game_over([player], players))
            winner_found=True
    
    if(winner_found):
        return winner_found
    # no single person has won the game, so check if a draw has been agreed upon
    agreed_draw=True
    for (country, winners) in non_surrendered_countries:
        if (winners >= len(non_surrendered_countries)):
            agreed_draw == False
    winners=[]
    if (agreed_draw):
        for (country, winners) in non_surrendered_countries:
            player_position=list(players.values()).index(country)
            player=list(players.keys())[player_position]
            winners.append(player)
        asyncio.run(sn.notify_game_over(winners, players))
        winner_found=True
    
    return winner_found

def get_orders(game_name, discord_id):
    game_doc=gm.get_game(game_name)
    country_code=game_doc['currently_playing'][discord_id]
    orders=game_doc['next_orders'][country_code]
    return orders

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
    retreats=game_doc['retreats_required']
    if(season == 'winter'):
        raise ValueError('Supply is still ongoing')
    elif(retreats != []):
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
        execute_turn(gamename_line)

def start_supply(game_doc):
    players=game_doc['currently_playing']
    name=game_doc['name']
    for country in gv.countries:
        supply=game_doc['state'][country]['controls']
        units=game_doc['state'][country]['armies']+game_doc['state'][country]['fleets']
        supp_required=len(supply)-len(units)

        player_position=list(players.values()).index(country)
        player=list(players.keys())[player_position]
        if (supp_required > 0):
            game_doc['required_supply'][country]=supp_required
            asyncio.run(sn.notify_reinforcements(player, supp_required, name))
        elif (supp_required < 0):
            game_doc['required_supply'][country]=supp_required
            asyncio.run(sn.notify_disbandment(player, supp_required, name))
            
def execute_supply(string,player):
    # string is formatted as ?supply add/remove type location
    split=string.split()
    addremove=split[2]
    unit=split[3]
    location=split[4]
    name=split[1]

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

    if (game_doc['required_supply'] == 0):
        game_doc['year']=game_doc['year']+1
        game_doc['season']='spring'
        asyncio.run(sn.notify_supply_complete(game_doc))
    
    gm.update_game(game_doc)

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
            if (season == 'fall'):
                for country in gv.countries:
                    if(move_to in game_doc['state'][country]['controls']):
                        game_doc['state'][country]['controls'].remove(move_to)
                game_doc['state'][to_update]['controls'].append(move_to)
    game_doc['season']=season
    return game_doc

def retreat_needed(retreats, game_doc):
    to_send={}
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
            asyncio.run(sn.notify_unit_destroyed(fromloc,player,name))
        else:
            try:
                game_doc['required_retreats'][country].append((fromloc,available))
                to_send[player].append(fromloc)
            except:
                game_doc['required_retreats'][country]=(fromloc,available)
                to_send[player]=fromloc

    asyncio.run(sn.notify_retreats_required(to_send,name))

def end_game(game_doc):
    gm.end_game(game_doc['name'])
    for player in game_doc['currently_playing'].keys():
        pm.end_game(player, game_doc['name'])

def execute_retreat(string, player):
    split=string.split()
    name=split[1]
    loc_from=split[2]
    loc_to=split[3]

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
            
    gm.update_game(game_doc)

def execute_turn(game_name):
    game_doc=gm.get_game(game_name)

    season = game_doc['season']
    full_order_list=[]
    for country in gv.countries:
        country_orders = game_doc['next_orders'][country]
        for order in country_orders:
            full_order_list.append(order)
    results=process_orders.execute_orders(full_order_list)
    successful_orders=results[0]
    retreat_required=results[1]

    game_doc=update_map(successful_orders, season,game_doc)

    if (season == 'spring'):
        new_season = 'fall'
    else:
        new_season ='winter'
    
    game_doc=update_map(successful_orders,season,game_doc)
    game_doc['season']=new_season
    gm.update_game(game_doc)
    
    if(retreat_required != []):
        retreat_needed(retreat_required,game_doc)
    elif (new_season == 'winter'):
        if (not check_wincons(game_doc)):
            start_supply(game_doc)
        else:
            end_game(game_doc)