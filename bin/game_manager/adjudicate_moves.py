import json
import game_cfgs

mapgraph=game_cfgs.game_map
adjacency=mapgraph["adjacency"]

def is_adjacent(ter1, ter2):
    return (ter1 in adjacency)
# turns look like this:
# {
#   command
#   new
#   conflict
#   target
#   unit_type
# }
def valid_hold(order):
    return "VALID"

def valid_move(order):
    destination=order["new"]
    unit_type=order["unit_type"]
    unit_location=order["conflict"]
    # failure cases
    # army moving into water
    if (unit_type == "A" and destination in mapgraph["SEA"]):
        return "INVALID"
    # fleet moving onto landlocked
    elif (unit_type == "F" and destination in mapgraph["LANDLOCKED"]):
        return "INVALID"
    # lets evaluate some valid moves
    elif (destination in adjacency[unit_location]):
        return "VALID"
    # no longer adjacent, so landlocked provinces cannot be reached
    elif (destination in mapgraph["LANDLOCKED"]):
        return "INVALID"
    # no longer adjacent, so fleets cannot move further
    elif (unit_type == "F"):
        return "INVALID"
    # eliminated all other possibilities, so have to check convoy validity
    else:
        return "CONVOY"

def valid_support(order):
    destination=order["conflict"]
    unit_location=order["new"]
    target=order["target"]
    unit_type = order["unit_type"]

    # to be a valid support order, the destination and target location must share a border and the unit and target location must share a border
    # fleets cannot support into landlocked territories
    # armies cannot support into sea territories
    if (unit_type == "F" and destination in mapgraph["LANDLOCKED"]):
        return "INVALID"
    elif (unit_type == "A" and destination in mapgraph["SEA"]):
        return "INVALID"
    elif (destination in adjacency[target] and destination in adjacency[unit_location]):
        return "VALID"
    else:
        return "INVALID"

def valid_convoy(order):
    destination=order["conflict"]
    target=order["new"]
    unit_type = order["unit_type"]

    #to be a valid convoy order, the unit must be F, the target must not be in a landlocked location, and the destination must not be landlocked
    if (unit_type != "F"):
        return "INVALID"
    if (target in mapgraph["LANDLOCKED"] or destination in mapgraph["LANDLOCKED"]):
        return "INVALID"
    else:
        return "VALID"

def valid_order(order):
    command = order["command"]
    switcher = {
        "HOLD":valid_hold,
        "MOVE":valid_move,
        "SUPPORT":valid_support,
        "CONVOY":valid_convoy
    }
    func=switcher.get(command)
    return func(order)