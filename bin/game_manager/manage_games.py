import adjudicate_moves
import process_turn
import vars
import json
import random
import uuid
import os
import psycopg2
from psycopg2.extras import Json

DATABASE_URL = os.environ['DATABASE_URL']

COUNTRIES=[
    "AUS","ENG","FRA","GER","ITA","RUS","TUR"
]

def get_game(game_name):
    connection = psycopg2.connect(DATABASE_URL)
    db = connection.cursor()
    db.execute("""
    SELECT * FROM gamestates name WHERE name = (%s);
    """,
    [game_name])
    game_doc=db.fetchall()

    if (game_doc == []):
        raise NameError("Failed to find a game with that name")
    else:
        return game_doc
    
    connection.close()

def end_game(game_name):
    connection = psycopg2.connect(DATABASE_URL)
    db = connection.cursor()
    db.execute("""
    SELECT * FROM gamestates name WHERE name = (%s);
    """,
    [game_name])
    game_doc=db.fetchall()

    if (game_doc == []):
        raise NameError("Failed to find a game with that name")
    else:
        db.execute("""
        DELETE FROM gamestates WHERE name = %s;
        """,
        [game_name])
    connection.commit()
    connection.close()

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
    connection = psycopg2.connect(DATABASE_URL)
    db = connection.cursor()
    game_template=vars.template
    game_template["currently_playing"]=assign_players(players)
    game_template["name"]=game_name
    game_template["turn_duration"]=turn_duration

    db.execute("""
    SELECT * FROM gamestates name WHERE name = (%s);
    """,
    [game_name])
    reject_duplicates=db.fetchall()

    if (reject_duplicates != []):
        raise NameError("Name is already in use!")

    to_insert=json.dumps(game_template)    
    db.execute("""
    INSERT INTO gamestates (name, games) VALUES (%s, %s);
    """,
    [game_name, to_insert])
    connection.commit()
    connection.close()