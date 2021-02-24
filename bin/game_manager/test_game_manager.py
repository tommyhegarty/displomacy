import move_adjudicator
import process_turn

def new_order(command,new,conflict,target,unit_type,owner):
    to_return={
        "command":command,
        "new":new,
        "conflict":conflict,
        "target":target,
        "unit_type":unit_type,
        "owner":owner
    }
    return to_return

def run_turn_test():
    orders=[
        new_order("MOVE","BUD","RUM","","A","TUR"),
        new_order("SUPPORT","SER","BUD","RUM","A","TUR"),
        new_order("MOVE","VIE","BUD","","A","RUS"),
        new_order("MOVE","GAL","WAR","","A","RUS"),
        new_order("MOVE","GAL","VIE","","A","AUS")
    ]
    results=process_turn.execute_orders(orders)
    print(f"Successful orders : {results[0]}")
    print(f"Retreat required : {results[1]}")

if __name__ == '__main__':
    run_turn_test()