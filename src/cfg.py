import os

token=os.environ['TOKEN']

player_table='displomacy-players'
game_table='displomacy-games'
orders_table='displomacy-orders'
turn_table='displomacy-turn-history'

home=os.path.expanduser('~')
orders_location=f'{home}/orders'
event_queue=''