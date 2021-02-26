import psycopg2
import os
DATABASE_URL = os.environ['DATABASE_URL']

def add_player(discord_id):

    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    SELECT * FROM players WHERE id = %s;
    """,
    [discord_id])
    duplicates=db.fetchone()
    if (duplicates != ''):
        raise NameError("Duplicate id, this player already exists")

    db.execute("""
    INSERT INTO players (id, current_games, finished_games) VALUES (%s, %s, %s)
    """,
    [discord_id,[],[]])

    connection.commit()
    connection.close()

def add_game(discord_id, name):
    try:
        add_player(discord_id)
        print(f"Added {discord_id} to the database")
    except NameError:
        print("Player already exists, adding to existing.")

    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    UPDATE players SET current_games = array_append(current_games, %s) WHERE id = %s
    """,
    [name,discord_id])
    connection.commit()
    connection.close()

def get_games(discord_id):

    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    SELECT (current_games) FROM players WHERE id = %s;
    """,
    [discord_id])
    current_games=db.fetchone()

    connection.close()

    return current_games

def end_game(discord_id,name):
    try:
        add_player(discord_id)
        print(f"Added {discord_id} to the database")
    except NameError:
        print("Player already exists, adding to existing.")

    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    UPDATE players SET current_games = array_remove(current_games, %s) WHERE id = %s 
    """,
    [name, discord_id])
    connection.commit()
    connection.close()