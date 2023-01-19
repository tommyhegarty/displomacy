import os, cfg

os.environ['dbstring'] = cfg.dbstring

from dbs import games_db as gdb
from logic import game_vars as gv

def test_dbs():
    template = gv.template
    try:
        result = gdb.add_game(template)
    except Exception as e:
        print(e)
    else:
        print(result)

test_dbs()