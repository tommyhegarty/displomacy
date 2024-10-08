import boto3, cfg, json, asyncio, watchdog, time
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent,FileSystemEventHandler
import dbs.order as o, dbs.game as g

# queue message format:
#{
#   'command':one of [order, lock, unlock, new, join, leave, surrender],
#   'player': 'playerid',
#   'channel': 'channel',
#   'content':{command-specific object?}
#}

class OrderEventHandler(FileSystemEventHandler):

    def lock(player, channel, content):
        o.lock_game(player, channel)
    def unlock(player, channel, content):
        o.unlock_game(player, channel)
    def order(player, channel, content):
        o.submit_order(player, channel, content)
    def new(player, channel, content):
        g.create_new_game(channel, player, content)

    command_map={
        'lock': lock,
        'unlock': unlock,
        'order': order
    }

    def on_created(self, event: FileCreatedEvent) -> None:
        file_path=event.src_path

        with open(file_path,'r') as file:
            message=json.load(file)
        
        command=message.get('command')
        player=message.get('player')
        channel=message.get('channel')
        content=message.get('content')

event_handler=OrderEventHandler()
observer=Observer()
observer.schedule(event_handler,cfg.orders_location,recursive=True)
print(f'observing at {cfg.orders_location}')
observer.start()

try:
    while True:
        time.sleep(1)
finally:
    observer.stop()
    observer.join()