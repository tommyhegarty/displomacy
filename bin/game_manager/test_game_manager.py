import move_adjudicator
import process_turn
import game_master
import sys
import os

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

def start_game_test():
    players=["tommy","no","no1","no3","no67","sajd","siahdoia"]
    game_master.new_game(players, "first game ever", "12 hours")
    #print(game_master.get_game("first game ever"))
    #game_master.end_game("first game ever")

if __name__ == '__main__':
    command = sys.argv[1]
    if (command == "startgame"):
        start_game_test()
    elif (command == "runturn"):
        run_turn_test()