import move_adjudicator
import process_turn
import game_cfgs
import json
import random
import uuid
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
db = psycopg2.connect(DATABASE_URL, sslmode="require")

COUNTRIES=[
    "AUS","ENG","FRA","GER","ITA","RUS","TUR"
]

def get_game(game_name):
    game_doc= db.execute(f'SELECT * FROM gamestates WHERE name == {game_name}')
    if (game_doc == ''):
        raise NameError("Failed to find a game with that name")
    else:
        return game_doc

def end_game(game_name):
    game_doc=db.execute_command(f'SELECT * FROM gamestates WHERE name == {game_name}')
    if (game_doc == ''):
        raise NameError("Failed to find a game with that name")
    else:
        db.execute_orders(f'DELETE FROM gamestates WHERE name == {game_name}')

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

def new_game(players, turn_duration, game_name):
    game_template=game_cfgs.template
    game_template["currently_playing"]=assign_players(players)
    game_template["name"]=game_name
    game_template["turn_duration"]=turn_duration

    reject_duplicates=f'SELECT * FROM gamestates WHERE name == {game_name}'
    if (reject_duplicates != ''):
        raise NameError("Name is already in use!")

    db.insert(game_template)