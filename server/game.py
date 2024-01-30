import random
from village import Village

class Game:
    def __init__(self):
        self.village_id = 0
        self.villages = {} 
        self.players = []
        self.game_over = False
        self.add_village()
        self.add_village()

    def state(self):
        # Return the current state of the game
        game_state = {
            #"v": [ {village.id: village.time, "night": village.night} for village in self.villages],
            #"v": [ village.state() for village in self.villages.values()],
            "v": [ {"vkey": village.id, "t": village.time, "night": village.night, "g": village.governance} for village in self.villages.values()],
            "p": [ player.state() for player in self.players]
        }
        return { "game": game_state }

    def add_village(self):
        self.villages[str(self.village_id)] = Village(str(self.village_id)) # add a new village 
        self.village_id += 1
        print(f"Added new village: {self.village_id-1}")
        return str(self.village_id-1)

    def remove_player(self, player):
        player.village.remove_player(player)
        del self.players[player.id] # remove player from player
        print(f"Removed player: {player.id}")

    def assign_new_role(self, player):
        # random normal (n) or werewolf (w) or vampire (v)
        player.random_role()
        # check if there are more then 2 werewolves
        werewolves = [p for p in player.village.players.values() if p.role == "w"]
        if werewolves.__len__() > 2:
            player.role = "n"
        # check if there is more then 1 vampire
        vampires = [p for p in player.village.players.values() if p.role == "v"]
        if vampires.__len__() > 1:
            player.role = "n"

    def add_player(self, player):
        self.players.append(player)

        # iterate through all villages and add player to first village with less then 10 players
        for village in self.villages.values():
           if village.players.__len__() < 10:
               player.village = village

        if player.village == None:
           village_id = self.add_village()
           player.village = self.villages[village_id]

        player.village.add_player(player)
        self.assign_new_role(player)
        return player
    
    def establish_village(self, player):
        # establish a new village
        if player.home_village != None:
            return { "msg": "already established village" }
        
        new_village_id = self.add_village()
        # move player to new village
        result = player.move(self, new_village_id)
        if player.village.id != new_village_id:
            return result

        player.village.established_by = player
        player.home_village = player.village
        return { "new_village": player.village.state() }
    
    def update(self):
        # go through all villages and update them
        # print(f"Updating villages {self.villages.__len__()}")
        all_actions = []
        keys_to_remove = []
        # remove all empty villages 
        for key, village in self.villages.items():
            if village.players.__len__() == 0 and village.established_by != None:
                village.days_without_people += 1
                if village.days_without_people > 96:
                    keys_to_remove.append(key)
                    if village.established_by != None:
                        village.established_by.home_village = None
                    
        for key in keys_to_remove:
            del self.villages[key]
            all_actions.append( {"removed_village": village.id})

        for village in self.villages.values():
            actions = village.update()
            all_actions.extend(actions)
        
        return all_actions

