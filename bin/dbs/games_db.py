from pymongo import MongoClient
import os

connection_string = os.environ['dbstring']

def get_game(name, channel):
    games = MongoClient(connection_string)['discplomacy']['games']
    return games.find_one({'name': name, 'channel': channel})