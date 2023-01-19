import adjudicator

testadj = adjudicator.Adjudicator()
olist1 = [
    {'order': 'MOVE', 'to': 'ION','from': 'AEG', 'sup': 'NAN', 'country': 'TUR'},
    {'order': 'SUPPORT', 'to': 'ION','from': 'GRE', 'sup': 'AEG', 'country': 'TUR'},
    {'order': 'SUPPORT', 'to': 'ION','from': 'ALB', 'sup': 'AEG', 'country': 'AUS'},
    {'order': 'MOVE', 'to': 'GRE','from': 'TUN', 'sup': 'NAN', 'country': 'ITA'},
    {'order': 'CONVOY', 'to': 'GRE','from': 'ION', 'sup': 'TUN', 'country': 'ITA'}
]
olist2 = [
    {'order': 'MOVE', 'to': 'ION','from': 'AEG', 'sup': 'NAN', 'country': 'TUR'},
    {'order': 'MOVE', 'to': 'AEG','from': 'GRE', 'sup': 'NAN', 'country': 'TUR'},
    {'order': 'MOVE', 'to': 'GRE','from': 'ION', 'sup': 'NAN', 'country': 'TUR'}
]

result = testadj.execute_orders(olist2)
print('***************************************************')
for i in result:
    print(f'THE MOVE {i[0]} SUCCESS STATE IS {i[1]}')
    print('***************************************************')