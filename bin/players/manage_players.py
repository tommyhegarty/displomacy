import json
import os

data_dir = os.environ['DATA_DIR']+'/players'

def register_player(user):
    if os.path.exists(f'{data_dir}/{user}.json'):
        return False
    else:
        data = {
            "discord_id": user,
            "current_games": [],
            "current_lobbies": [],
            "completed_games": []
        }
        file = open(f'{data_dir}/{user}.json', 'w')
        file.write(json.dumps(data))
        file.close()
        return True

def join_lobby(user, name, channel):
    if not os.path.exists(f'{data_dir}/{user}.json'):
        return False
    else:
        file = open(f'{data_dir}/{user}.json', 'r')
        data = json.load(file)
        file.close()

        data['current_lobbies'].append({'name': name, 'channel': channel})

        file = open(f'{data_dir}/{user}.json', 'w')
        file.write(json.dumps(data))
        file.close()
        return True

def leave_lobby(user, name, channel):
    if not os.path.exists(f'{data_dir}/{user}.json'):
        return False
    else:
        file = open(f'{data_dir}/{user}.json', 'r')
        data = json.load(file)
        file.close()

        obj = {'name': name, 'channel': channel}
        if obj not in data['current_lobbies']:
            return False
        data['current_lobbies'].remove(obj)

        file = open(f'{data_dir}/{user}.json', 'w')
        file.write(json.dumps(data))
        file.close()
        return True