import random
from village import Village

class Game:
    def __init__(self):
        self.villages = []
        self.players = []
        self.game_over = False
        self.add_village()
        self.add_village()

    def state(self):
        # Return the current state of the game
        game_state = {
            "v": [{village.id: village.time, "night": village.night} for village in self.villages],
            "p": [ player.state() for player in self.players]
        }
        return { "game": game_state }

    def add_village(self):
        self.villages.append(Village(self.villages.__len__()))
        print(f"Added new village: {self.villages.__len__()}")

    def remove_player(self, player):
        player.village.remove_player(player)
        print(f"Removed player: {player.id}")

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
        if(self.villages.__len__() == 0):
           self.add_village()
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
    
    def establish_village(self, player):
        # establish a new village
        if player.home_village != None:
            return { "msg": "already established village" }
        
        self.add_village()
        # move player to new village
        result = player.move(self, self.villages[-1].id)
        if player.village.id != self.villages[-1].id:
            return result

        player.village.established_by = player
        player.home_village = player.village
        return { "new_village": player.village.state() }
    
    def remove_village(self, village_id):
        # remove village
        self.villages.remove(village_id)
        return {"removed_village": village_id}

    def update(self):
        # go through all villages and update them
        # print(f"Updating villages {self.villages.__len__()}")
        all_actions = []
        # remove all empty villages 
        for village in self.villages:
            if village.players.__len__() == 0 and village.established_by != None:
                village.days_without_people += 1
                if village.days_without_people > 96:
                    self.villages.remove(village)
                    all_actions.append( {"removed_village": village.id})

        for village in self.villages:
            actions = village.update()
            # if messages are not empty array, add each item to all_messages
            all_actions.extend(actions)
        
        return all_actions

