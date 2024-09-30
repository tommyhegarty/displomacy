from boto3 import dynamodb
import os

connection_string = os.environ['dbstring']

def get_game(name, channel):

    games = MongoClient(connection_string)['displomacy']['games']
    return games.find_one({'name': name, 'channel': channel})

def add_game(gamedoc):

    try:
        games = MongoClient(connection_string)['displomacy']['games']
        games.insert_one(gamedoc)
    except:
        raise Exception('A game of that name already exists in that channel')
    
    return get_game(gamedoc['name'],gamedoc['channel'])

def update_game(gamedoc):

    try:
        games = MongoClient(connection_string)['displomacy']['games']
        result = games.find_one_and_replace({'name': gamedoc['name'], 'channel': gamedoc['channel']}, gamedoc, return_document=collection.ReturnDocument.AFTER)
    except Exception as e:
        raise e
    else:
        return result

def search_games(search_filter):

    try:
        games = MongoClient(connection_string)['displomacy']['games']
        result = [game for game in games.find(search_filter)]
    except Exception as e:
        raise e
    else:
        return result

def delete_game(name, channel):
    try:
        games = MongoClient(connection_string)['displomacy']['games']
        result = games.find_one_and_delete({'_id': {'name': name, 'channel': channel}})
    except Exception as e:
        raise e
    else:
        return result
