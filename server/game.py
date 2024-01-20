import random
from village import Village

class Game:
    def __init__(self):
        self.villages = []
        self.players = []
        self.game_over = False
        self.add_village()
        self.add_village()

    def add_village(self):
        self.villages.append(Village(self.villages.__len__()))
        print(f"Added new village: {self.villages.__len__()}")

    def assign_new_role(self, player):
        # random normal (n) or werewolf (w) or vampire (v)
        player.role = random.choice(["n", "w", "v"])
        # check if there are more then 2 werewolves
        werewolves = [p for p in self.players if p.role == "w"]
        if werewolves.__len__() > 2:
            player.role = "n"
        # check if there is more then 1 vampire
        vampires = [p for p in self.players if p.role == "v"]
        if vampires.__len__() > 1:
            player.role = "n"

    def add_player(self, player):
        self.players.append(player)
        if(self.villages[-1].players.__len__() >= 10):
           self.add_village()
           
        # Assign the player to a village (simplified for this example)
        self.villages[-1].add_player(player) # add player to last village
        player.village = self.villages[-1] # assign player to last village
        self.assign_new_role(player)

        # player.role = "n" # assign player role
        return player

    def get_village(self, village_id):
        return self.villages[village_id]
    
    def update(self):
        # go through all villages and update them
        # print(f"Updating villages {self.villages.__len__()}")
        for village in self.villages:
            village.update()

    def get_state(self):
        # Return the current state of the game
        game_state = {
            "v": [{village.id: village.time, "night": village.night} for village in self.villages],
            "p": [ player.state() for player in self.players]
        }
        return game_state
