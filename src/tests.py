import os, cfg, datetime

os.environ['dbstring'] = cfg.dbstring

from dbs import games_db as gdb
from logic import game_vars as gv
from games import manage_games as mg

def test_dbs():
    template = gv.template
    result = gdb.add_game(template)
    print(result)

    current = datetime.datetime.now()
    next_turn = current - datetime.timedelta(seconds=3600)
    template['next_turn']=next_turn
    template['players']=['a','b','c','d','e']
    result = gdb.update_game(template)
    print(result)
    
    result = gdb.search_games({'players': 'd'})
    print(result)

    result = gdb.get_game('sample','')
    print(result)

    result = gdb.delete_game('sample','')
    print(result)

def test_game_manager():
    result = mg.new_game('funnyname','a','20 mins','channeltest')
    print(result)

    result = mg.get_game('funnyname','channeltest')
    print(result)

    result = mg.leave_game('funnyname', 'channeltest', 'a')
    print(result)

def test_ready_games():
    now = datetime.datetime.now()
    result = gdb.search_games({"next_turn": {"$lt": now}})
    print(result)

test_ready_games()
#test_dbs()
#test_game_manager()