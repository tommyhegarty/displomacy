# order: {
#   order: type,
#   to: location the order goes to,
#   from: location of the unit being ordered,
#   sup: location of the thing being affected, None for MOVE and HOLD,
#   country: the country of the order,
#   type: the type of unit in the order
# }
from . import game_vars as gv

class Adjudicator():
    resolved=[]
    success=[]

    dependencies=[]
    order_list=[]

    def adjudicate(self, onum):
        order = self.order_list[onum]
        otype = order['order']
        ofrom = order['from']
        oto = order['to']
        osup = order['sup']
        ocountry = order['country']

        dislodge = [i for i,o in enumerate(self.order_list) if o['order'] == 'MOVE' and o['to'] == ofrom]

        if otype == 'CONVOY':
            for num in dislodge:
                if self.resolve(num):
                    return False
        elif otype == 'HOLD':
            for num in enumerate(self.order_list):
                if self.resolve(num):
                    return False
        elif otype == 'SUPPORT':
            if len(dislodge) > 0:
                return False
        else:
            if oto not in gv.game_map['adjacency'][ofrom]:
                convoy_list = [i for i,o in enumerate(self.order_list) if o['order'] == 'CONVOY' and o['to'] == oto and o['sup'] == ofrom]
                for num in convoy_list:
                    if not self.resolve(num):
                        return False
            
            holding_units = [(i,o) for i,o in enumerate(self.order_list) if o['from'] == oto] # the unit currently stationed in the attacked province
            support_attack = [(i,o) for i,o in enumerate(self.order_list) if o['order'] == 'SUPPORT' and o['sup'] == ofrom and o['to'] == oto] # the unites supporting our move
            
            if len(holding_units) == 0: # if the province is empty
                attack_strength = 1
                for sup,o in support_attack:
                    if self.resolve(support_attack):
                        attack_strength=attack_strength+1
            elif holding_units[0][1]['order'] == 'MOVE': # if the unit is moving
                will_vacate = self.resolve(holding_units[0][0])
                if will_vacate: # if the unit will successfully leave the province
                    attack_strength = 1
                    for sup,o in support_attack:
                        if self.resolve(support_attack):
                            attack_strength=attack_strength+1 # attack strength is 1 plus each support order
                elif holding_units[0][1]['country'] == ocountry: # if we're colliding with our own unit
                    attack_strength = 0
            else: # the unit will not willingly leave
                attack_strength = 1
                for sup,o in support_attack:
                    if o['country'] != holding_units[0][1]['country']:
                        if self.resolve(sup):
                            attack_strength=attack_strength+1 # otherwise our strength is 1 plus supporting attack from not defender's country

            head_to_head = [(i,o) for i,o in enumerate(self.order_list) if o['to'] == ofrom and o['from'] == oto and o['order'] == 'MOVE']
            # head to head is a unit in the place we're moving that's moving TOWARDS us

            if len(head_to_head) == 0: # if there's no head to head combat, then we're contesting 'hold strength', i.e. the unit is holding against us                
                if len(holding_units) == 0: # if no one is there, no one is there
                    hold_strength=0
                elif holding_units[0][1]['order'] == 'MOVE': # check to see if the spot is moving
                    will_vacate = self.resolve(holding_units[0][0])
                    if will_vacate: # if its gonna be empty, no holding
                        hold_strength = 0
                    else: # failed move orders don't get hold support! so the hold strength is just 1
                        hold_strength = 1
                else:
                    hold_strength = 1
                    support_hold = [(i,o) for i,o in enumerate(self.order_list) if o['order'] == 'SUPPORT' and o['sup'] == oto and o['to'] == oto]
                    # supports for a hold have to be issued specifically "support unit from A to A". if its supporting the unit moving, then it wont count towards hold support
                    for sup, o in support_hold:
                        if self.resolve(sup):
                            hold_strength=hold_strength+1 # hold strength is equal to 1 plus each successful hold support order
                if hold_strength >= attack_strength: # if the hold strength is stronger than the attack strength then no matter what this move will fail
                    return False
            else: # if there is head to head combat, then we're contesting the defense strength instead of the hold strength
                defense_strength = 1
                support_head_to_head = [(i,o) for i,o in enumerate(self.order_list) if o['to'] == ofrom and o['sup'] == oto and o['order'] == 'SUPPORT']
                for snum, s in support_head_to_head: # defense strength is country agnostic -- any country can support a head-to-head fight, even your own (by accident)
                    if self.resolve(snum):
                        defense_strength = defense_strength+1
                if defense_strength >= attack_strength: # if defense strength is stronger than the attack strength then no matter what this move will fail
                    return False
                
            prevent_moves = [(i,o) for i,o in enumerate(self.order_list) if o['to'] == oto and o['from'] != ofrom and o['order'] == 'MOVE']
            # a prevent move is any other move that is attempting to affect the same province
            if len(prevent_moves) == 0:
                prevent_strength = 0 # if there's no moves into the place then nothing to worry about
                if prevent_strength >= attack_strength: # this isnt technically necessary, bc attack strength being 0 means its failed by now, but worth illustrating the equation anyway
                    return False
            elif len(head_to_head) != 0 and self.resolve(head_to_head[0][0]): # if we are fighting head to head and the head to head fight will win, then dont worry about prevent strength
                prevent_strength = 0
                if prevent_strength >= attack_strength: # see above
                    return False
            else:
                for num, p in prevent_moves: # otherwise prevent strength is 1 plus all the orders supporting the preventing moves
                    prevent_strength = 1
                    support_prevent_moves = [(i,o) for i,o in enumerate(self.order_list) if o['to'] == p['to'] and o['sup'] == p['from'] and o['order'] == 'MOVE']
                    for snum, s in support_prevent_moves:
                        if self.resolve(snum):
                            prevent_strength = prevent_strength+1
                    if prevent_strength >= attack_strength: # if any of the other moves are gonna win, then this move fails
                        return False
        return True

    def resolve(self, onum):
        if self.resolved[onum] == 'R': # obvious : if this move is resolved, then return whatever we resolved it to
            return self.success[onum]
        
        if self.resolved[onum] == 'G': # we have a guess stored for this order
            if onum not in self.dependencies:
                self.dependencies.append(onum) # whatever cycle we are on is dependent on this order, so if it isnt there, put it there
            return self.success[onum]

        self.resolved[onum] = 'G'
        self.success[onum] = False # this is a completely unresolved order, so we will start by guessing at it
        old_deplen = len(self.dependencies) # checking to see if we add more dependencies to the list

        fail_result = self.adjudicate(onum)
        if len(self.dependencies) == old_deplen: # didnt add more dependencies, meaning we adjudicated the order in one go
            if self.resolved[onum] != 'R': # make sure this hasnt already been resolved by the backup rule
                self.resolved[onum] = 'R'
                self.success[onum] = fail_result
            return fail_result
        
        if self.dependencies[old_deplen] != onum: # there are new dependencies added that arent just our guess, so we have to add our guess and run it
            self.dependencies.append(onum)
            self.success[onum] = fail_result
            return fail_result # make this order a dependency and return the result of the guess, but make sure the state stays guessing

        # if we've made it here, then the outcome of this cycle depends on THIS GUESS. reset the dependency list to the previous list, then
        # guess that the move succeeds instead and compare outcomes
        new_deplen = len(self.dependencies)
        while new_deplen > old_deplen:
            new_deplen=new_deplen-1
            self.resolved[self.dependencies[new_deplen]] = 'U'
        self.dependencies=self.dependencies[0:old_deplen]

        self.resolved[onum] = 'G'
        self.success[onum] = True # guessing that the move succeeds this time

        success_result = self.adjudicate(onum)
        if success_result == fail_result: # this means that both guesses result in the same resolution, so theres only one option to return
            new_deplen = len(self.dependencies)
            while new_deplen > old_deplen:
                new_deplen=new_deplen-1
                self.resolved[self.dependencies[new_deplen]] = 'U'
            self.dependencies=self.dependencies[0:old_deplen] # clean up the list of dependencies as we're good to go here
            self.success[onum] = fail_result # can be either fail or pass result, as they are the same
            self.resolved[onum] = 'R'
            return fail_result
        
        # we've made it here, which means there are either two or zero possible outcomes.
        # we need to make use of the paradox-resolving backup rule
        # this determines whether the loop we're in is a circle of moves or a convoy paradox and resolves accordingly
        # not sure how it works yet so lets do some tests
        # self.backup_rule(old_deplen)

        # finally, after backing up and everything, we can retry the resolution
        return self.resolve(onum)

    def execute_orders(self, order_list):
        self.order_list = order_list.copy()
        self.resolved = ['U'] * len(self.order_list)
        self.success = [False] * len(self.order_list)
        self.dependencies = []

        for num, order in enumerate(self.order_list):
            print(f'Resolving {order}')
            self.resolve(num)
        
        result = []
        for num, _ in enumerate(self.order_list):
            result.append((self.order_list[num],self.success[num]))
        
        return result