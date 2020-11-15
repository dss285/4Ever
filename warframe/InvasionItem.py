class InvasionItem:
    def __init__(self, attacker, defender, node, starttime, status):
        self.attacker = attacker
        self.defender = defender
        self.start_time = starttime
        self.node = node
        self.status = status

class InvasionOpp:
    #0 DEFENDING
    #1 ATTACKING
    def __init__(self, faction, rewards):
        self.faction = faction
        self.rewards = rewards


