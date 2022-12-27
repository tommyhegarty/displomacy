import psycopg2
import os
DATABASE_URL ="postgresql://discbot:discbotpass@localhost:5432/discplomacy"

# lobby object needs
# create lobby
# get lobby information
# start game from lobby

def add_message_id(name, message_id):
    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    UPDATE lobbies SET message_id = %s WHERE name = %s;
    """,
    [message_id, name])

    connection.commit()
    connection.close()

def get_message_id(name):
    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    SELECT message_id FROM lobbies WHERE name = %s;
    """,
    [name])
    result=db.fetchone()
    connection.close()
    if (result == None):
        raise NameError('No lobby of that name exists.')
    
    return result[0]

def create_lobby(name, turn_duration, creation_time):
    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    try:
        db.execute("""
        INSERT INTO lobbies (name, turn_duration, creation_time)
        VALUES (%s, %s, %s);
        """,
        [name, turn_duration, creation_time])
    except:
        raise NameError('Lobby of that name already exists.')

    connection.commit()
    connection.close()

def get_lobby_information(name):
    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    SELECT * FROM lobbies WHERE name = %s;
    """,
    [name])
    result=db.fetchone()
    connection.close()

    if (result == None):
        raise NameError('Lobby of that name does not exist.')
    
    return result[0]

def start_game_from_lobby(name):
    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    SELECT * FROM lobbies WHERE name = %s;
    """,
    [name])
    result = db.fetchone()

    if(result == None):
        connection.close()
        raise NameError('Lobby of that name does not exist.')
    
    db.execute("""
    DELETE FROM lobbies WHERE name = %s;
    """,
    [name])
    connection.close()
    return result