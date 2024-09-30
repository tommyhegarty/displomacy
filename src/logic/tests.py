import adjudicator

testadj = adjudicator.Adjudicator()

olist1 = [
    {'order': 'MOVE', 'to': 'BOH','from': 'VIE', 'sup': 'NAN', 'country': 'AUS', 'unit': 'A'},
    {'order': 'MOVE', 'to': 'ADR','from': 'TRI', 'sup': 'NAN', 'country': 'AUS', 'unit': 'F'},
    {'order': 'HOLD', 'to': 'BUD','from': 'BUD', 'sup': 'NAN', 'country': 'AUS', 'unit': 'F'}
]

result = testadj.execute_orders(olist1)
print('***************************************************')
for i in result:
    print(f'THE MOVE {i[0]} SUCCESS STATE IS {i[1]}')
    print('***************************************************')