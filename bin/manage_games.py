import game_vars as gv
import json
import random
import uuid
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def update_game(game_doc):
    connection = psycopg2.connect(DATABASE_URL)
    db = connection.cursor()
    name = game_doc['name']

    get_game(name)

    db.execute("""
    UPDATE gamestates SET games = %s WHERE name = %s;
    """,
    [json.dumps(game_doc),name])

    connection.commit()
    connection.close()

def get_game(game_name):
    connection = psycopg2.connect(DATABASE_URL)
    db = connection.cursor()
    db.execute("""
    SELECT * FROM gamestates name WHERE name = (%s);
    """,
    [game_name])
    game_doc=db.fetchone()

    if (game_doc == None):
        raise NameError("Game of that name does not exist")
    else:
        return game_doc[1]
    
    connection.close()

def end_game(game_name):
    connection = psycopg2.connect(DATABASE_URL)
    db = connection.cursor()
    db.execute("""
    SELECT games FROM gamestates name WHERE name = (%s);
    """,
    [game_name])
    game_doc=db.fetchone()

    if (game_doc == None):
        raise NameError("Game of that name does not exist")
    else:
        db.execute("""
        DELETE FROM gamestates WHERE name = %s;
        """,
        [game_name])
    connection.commit()
    connection.close()

def new_game(game_doc):
    connection = psycopg2.connect(DATABASE_URL)
    db = connection.cursor()
    to_insert=json.dumps(game_doc)    
    db.execute("""
    INSERT INTO gamestates (name, games) VALUES (%s, %s);
    """,
    [game_doc['name'], to_insert])
    connection.commit()
    connection.close()