import move_adjudicator

# turns look like this:
# ["COMMAND","LOCATION","DESTINATION","TARGET","TYPE"]
# so then the four formats would be
# ["HOLD","SELF","","","A/F"]
# ["MOVE","SELF","NEW LOCATION","","A/F"],
# ["SUPPORT","SELF","TARGET'S NEW LOCATION","UNIT TO SUPPORT","A/F"]
# ["CONVOY","SELF","CONVOY TARGET","UNIT TO CONVOY","F"]
