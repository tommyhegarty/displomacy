from games import process_orders as po

def make_order(command, new, conflict, target, unit, owner):
    return {
        'command':command,
        'new':new,
        'conflict':conflict,
        'target':target,
        'unit_type':unit,
        'owner':owner
    }

def test_order_execution():
    orders=[
        make_order('HOL','RUM','RUM','','A','AUS'),
        make_order('MOV','RUM','BUD','','A','RUS'),
        make_order('SUP','SER','RUM','BUD','A','RUS')
    ]
    print(po.execute_orders(orders))