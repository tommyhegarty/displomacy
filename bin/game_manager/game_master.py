import move_adjudicator
import process_turn
import game_cfgs
import json
import random
import uuid
import os
import psycopg2
from psycopg2.extras import Json

DATABASE_URL = os.environ['DATABASE_URL']
connection = psycopg2.connect(DATABASE_URL, sslmode="require")

COUNTRIES=[
    "AUS","ENG","FRA","GER","ITA","RUS","TUR"
]

def get_game(game_name):
    db = connection.cursor()
    query='SELECT * FROM gamestates WHERE name = %s;'
    data=(game_name,)
    game_doc=db.execute(query,data)

    if (game_doc == None):
        raise NameError("Failed to find a game with that name")
    else:
        return game_doc

def end_game(game_name):
    db = connection.cursor()
    query='SELECT * FROM gamestates WHERE name = %s;'
    data=(game_name,)
    game_doc=db.execute(query,data)

    if (game_doc == None):
        raise NameError("Failed to find a game with that name")
    else:
        query='DELETE FROM gamestates WHERE name =  %s;'
        data=(game_name,)
        game_doc=db.execute(query,data)

def assign_players(players):
    shuffled=COUNTRIES.copy()
    random.shuffle(shuffled)
    to_return={
        shuffled[0]: players[0],
        shuffled[1]: players[1],
        shuffled[2]: players[2],
        shuffled[3]: players[3],
        shuffled[4]: players[4],
        shuffled[5]: players[5],
        shuffled[6]: players[6]
    }
    return to_return

def new_game(players, game_name, turn_duration):
    db = connection.cursor()
    game_template=game_cfgs.template
    game_template["currently_playing"]=assign_players(players)
    game_template["name"]=game_name
    game_template["turn_duration"]=turn_duration

    reject_duplicates=db.execute("""
    SELECT * FROM gamestates name WHERE name = (%s);
    """,
    [game_name])

    print(reject_duplicates)
    if (reject_duplicates != None):
        raise NameError("Name is already in use!")

    to_insert=json.dumps(game_template)
    db.execute("""
    INSERT INTO gamestates (name, games) VALUES (%s, %s);
    """,
    [game_name, to_insert])