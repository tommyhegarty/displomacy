import adjudicate_moves
import vars

# could we make each order a dict?
# {
#   command
#   new : for move, where it's going. for support, hold and convoy, current location
#   conflict : for move, where it's coming from. for support and convoy, where target is headed. for hold, current location
#   target : for move and hold, blank. for support and convoy, location of unit it's targeting
#   unit_type
#   owner 
# }
end_locations=[]
possible_conflicts=[]
moves=[]
convoy_moves=[]
convoys=[]
supports=[]
holds=[]
failed_orders=[]
successful_orders=[]
retreat_required=[]

def execute_cascaded_combat(order, cascaded_loc):
    temp_success = successful_orders.copy()
    while temp_success:
        checking_order = temp_success.pop(0)
        checking_command = checking_order["command"]
        move_new = checking_order["new"]
        move_conflict = checking_order["conflict"]
        if (checking_command == "MOVE" and move_new == cascaded_loc):
            #print(f"The failed order : {order} has encountered a new conflict at {checking_order}")
            total = 0
            # now checking order has to deal with a contesting of 1
            for possible_support in supports:
                support_from=possible_support["target"]
                support_to=possible_support["conflict"]
                support_loc=possible_support["new"]
                #print(f"Checking possible support with order : {possible_support}")
                if (support_from == move_conflict and support_to == move_new):
                    if (support_loc not in possible_conflicts):
                        total = total + 1
            if (total > 0):
                retreat_required.append(order)
            else:
                successful_orders.remove(checking_order)
                failed_orders.append(checking_order)

def execute_combat(order):
    # need to get all moves & holds that conflict
    participant_orders=[order]
    new_location = order["new"]
    for checking_confl in moves+holds+supports+convoys:
        p_conflict=checking_confl["new"]
        if (p_conflict == new_location):
            participant_orders.append(checking_confl)

    # now need to tally up support for every order
    support_totals=[]
    for part in participant_orders:
        total = 0
        part_cur=part["conflict"]
        part_new=part["new"]
        for checking_supp in supports:
            support_from=checking_supp["target"]
            support_to=checking_supp["conflict"]
            support_loc=checking_supp["new"]
            if (support_from == part_cur and support_to == part_new):
                if (support_loc in possible_conflicts):
                    failed_orders.append(checking_supp)
                else:
                    total=total+1
        support_totals.append((part, total))
    
    max_str=0
    winning_order=[]
    for element in support_totals:
        supp=element[1]
        cur_order=element[0]
        if (supp > max_str):
            winning_order=cur_order

    #print(f"Participant orders are : {participant_orders}")
    #print(f"Winning order is : {winning_order}")
    return (participant_orders,winning_order)

def execute_convoy(convoy_orders, move_order):
    # convoy orders is a list of all convoys being used
    # move order is the unit being convoyed
    current_location = move_order["conflict"]
    next_step=move_order
    while convoy_orders:
        found_move=False
        for checking_adj in convoy_orders:
            fleet_location = checking_adj["new"]
            if (adjudicate_moves.is_adjacent(current_location,fleet_location)):
                next_step=checking_adj
                found_move=True
                break
        if (not found_move):
            return False
        next_step_loc=next_step["new"]
        if (next_step_loc in possible_conflicts):
            return False
    return True

def execute_orders(list_of_orders):

    # locating possible conflicts

    while list_of_orders:
        order = list_of_orders.pop(0)
        command = order["command"]
        current_el=order["new"]

        validity=adjudicate_moves.valid_order(order)
        array_switcher={
            "HOLD":holds,
            "MOVE":moves,
            "SUPPORT":supports,
            "CONVOY":convoys
        }
        if (validity == "INVALID"):
            break
        elif (validity == "CONVOY"):
            convoy_moves.append(order)
        else:
            array_switcher[command].append(order)

        if (current_el in end_locations):
            possible_conflicts.append(current_el)
        else:
            end_locations.append(current_el)

    # first runthrough of list of orders complete, all invalid orders removed

    # eval convoy moves
    while convoy_moves:
        order = convoy_moves.pop(0)
        new_location = order["new"]
        old_location = order["conflict"]

        convoys_for_move=[]
        for convoy_order in convoys:
            convoy_destination=convoy_order["new"]
            convoy_target=convoy_order["target"]
            if (new_location == convoy_destination and old_location == convoy_target):
                convoys_for_move.append(convoy_order)
        
        convoy_success=execute_convoy(convoys_for_move,order)
        
        if (convoy_success):
            successful_orders.append(convoy_success)
        else:
            failed_orders.append(order)
            for convoy in convoys_for_move:
                failed_orders.append(convoy)
    
    # eval valid move order non-convoy
    while moves:
        order = moves.pop(0)
        #print(f"Currently executing order : {order}")
        new_location = order["new"]
        if (new_location in possible_conflicts):
            tple=execute_combat(order)
            moves_used=tple[0]
            successful_move=tple[1]
            for to_remove in moves_used:
                if (to_remove != successful_move):
                    failed_orders.append(to_remove)
                if (to_remove != order):
                    try:
                        moves.remove(to_remove)
                    except Exception:
                        holds.remove(to_remove)
            if (successful_move != []):
                successful_orders.append(successful_move)
        else:
            successful_orders.append(order)
    
    #print(f"Successful orders have occurred at : {successful_orders}")
    # now we have a list of orders that failed -- determine if they require retreat or can play out on their own
    while failed_orders:
        #print(f"Current failed orders are : {failed_orders}")
        order = failed_orders.pop(0)
        command = order["command"]
        if (command == "HOLD"):
            retreat_required.append(order)
        else:
            cascaded_loc=""
            if (command == "MOVE"):
                cascaded_loc=order["conflict"]
            elif (command == "SUPPORT" or command == "CONVOY"):
                cascaded_loc=order["new"]
            execute_cascaded_combat(order, cascaded_loc)
    
    return (successful_orders, retreat_required)