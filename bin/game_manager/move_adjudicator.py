import json

with open("mapgraph.json","r") as file:
    mapgraph = json.load(file)

def valid_move(unit_type, unit_location, destination):
    # failure cases
        # army moving into water
        if (unit_type == "A" and destination in mapgraph["SEA"]):
            return "INVALID"
        # fleet moving onto landlocked
        elif (unit_type == "F" and destination in mapgraph["LANDLOCKED"]):
            return "INVALID"
        # lets evaluate some valid moves
        elif (destination in mapgraph["adjacency"][unit_location]):
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