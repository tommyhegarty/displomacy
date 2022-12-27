import psycopg2
import os
DATABASE_URL = "postgresql://discbot:discbotpass@localhost:5432/discplomacy"

def setup():
    ## create lobby db
    connection=psycopg2.connect(DATABASE_URL)
    db=connection.cursor()

    db.execute("""
    CREATE TABLE IF NOT EXISTS lobbies(
        name    text    not null,
        turn_duration   text    not null,
        creation_time   text    not null
    )
    """)

    ## create games db

    db.execute("""
    CREATE TABLE IF NOT EXISTS gamestates(
        name    text    not null,
        games   text    not null,
        next_turn   text    not null
    )
    """)

    ## create players db
    db.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id  text    not null,
        current_games   text    not null,
        completed_games text    not null
    )
    """)

    connection.commit()
    connection.close()