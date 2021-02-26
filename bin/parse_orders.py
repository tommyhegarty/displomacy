import json
import game_vars
def parse_orders(order_arr, game_doc, owner):
    # break out the array
    formatted_orders=[]
    for order in order_arr:
        split_spaces=order.split()
        command=split_spaces[0]
        u_type=split_spaces[1]
        if (command == 'CON' or command == 'SUP'):
            new=split_spaces[2]
            conflict=split_spaces[3]
            target=split_spaces[4]
        elif (command == 'MOV'):
            new=split_spaces[3]
            conflict=split_spaces[2]
            target=''
        elif(command == 'SUP'):
            new=split_spaces[2]
            conflict=split_spaces[2]
            target=''
        else:
            raise ValueError("Not a valid command")
        new_order = {
            'command':command,
            'new': new,
            'conflict': conflict,
            'target': target,
            'unit_type': u_type,
            'owner': owner
        }
        formatted_orders.append(new_order)
    return formatted_orders

def all_orders_submitted(game_doc):
    to_return=True
    all_moves=game_doc['next_orders']
    for country in game_vars.countries:
        if (all_moves[country] == []):
            to_return = False
    return to_return