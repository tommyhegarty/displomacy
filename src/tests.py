import os
os.environ["TOKEN"]="meaninglesstesttoken"
import dbs.player as p, dbs.order as o, cfg
import boto3, boto3.dynamodb.conditions as con

def test_player():

    p.player_join_game('testid','testchannel')
    p.player_join_game('testid','testchannel2')
    p.player_join_game('testid','testchannel3')
    print(p.get_player_games('testid'))

    p.player_finish_game('testid','testchannel2')
    print(p.get_player_games('testid'))

def test_failed_update():

    ddb = boto3.resource('dynamodb').Table(cfg.player_table)
    ddb.update_item(
        Key={'id':'thisoneisntthere'},
        ExpressionAttributeNames={'#ag':'active_games'},
        ExpressionAttributeValues={':a':['fakegame']},
        UpdateExpression='SET #ag = list_append(#ag, :a)'
    )

def test_order():

    testorder1={'location':'a','b':'b'}
    testorder2={'location':'b','c':'c'}
    testorder3={'location':'a','d':'d'}

    o.submit_order('testplayer','testgame',testorder1)
    o.submit_order('testplayer','testgame',testorder2)
    print(o.get_all_player_orders('testplayer','testgame'))

    o.submit_order('testplayer1','testgame',testorder1)
    o.submit_order('testplayer','testgame',testorder3)
    print(o.get_all_player_orders('testplayer','testgame'))
    print(o.get_all_game_orders('testgame'))

#test_player()
#test_failed_update()
test_order()