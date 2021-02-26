import discplomacy

async def notify_new_phase(game_doc):
    print('here is where we notify a new phase')

async def notify_supply_complete(game_doc):
    players=game_doc['currently_playing']
    year=game_doc['year']
    season=game_doc['season']
    game=game_doc['name']
    for player in players.keys():
        await discplomacy.send_private_message(player,game, f'Winter completed, it is now {season} {year}')

async def notify_reinforcements(player,supply,name):
    await discplomacy.send_private_message(player,name,f'You can resupply your forces up to {supply}. Use the ?supply add command, remembering that the only valid supply locations are unoccupied supply centers you began the game with.')

async def notify_disbandment(player,supply,name):
    await discplomacy.send_private_message(player,name,f'You must disband your forces up to {supply}. Use the ?supply remove command.')

async def notify_retreats_required(retreats,name):
    for player in retreats.keys():
        locations = retreats[player]
        discplomacy.send_private_message(player, name,f'The turn has executed and you are forced to retreat from the following locations: {locations}')

async def notify_unit_destroyed(location, player, name):
    await discplomacy.send_private_message(player,name,f'Your unit at {location} was defeated and had nowhere to retreat, so was destroyed.')

async def notify_game_start(game_doc):
    players=game_doc['currently_playing']
    game=game_doc['name']
    for player in players.keys():
        country = game_doc['currently_playing'][player]
        await discplomacy.send_private_message(player, game, f'Your game has started! You have been assigned {country}')

async def notify_game_over(winners,players):
    print('Game has ended')