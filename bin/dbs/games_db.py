from pymongo import MongoClient
import os

connection_string = os.environ['dbstring']

def get_game(name, channel):
    games = MongoClient(connection_string)['discplomacy']['games']
    return games.find_one({'name': name, 'channel': channel})

def add_game(gamedoc):

    try:
        games = MongoClient(connection_string)['discplomacy']['games']
        result = games.insert_one(gamedoc)
    except:
        raise Exception('A game of that name already exists in that channel')
    else:
        return result