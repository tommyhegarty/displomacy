import os, cfg

os.environ['dbstring'] = cfg.dbstring

from dbs import games_db as gdb

def test_dbs():
    result=gdb.get_game('sample', '')
    print(result)

test_dbs()