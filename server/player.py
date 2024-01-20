import random 
from village import Village

class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.life = 100
        self.role = None  # Roles like "Villager", "Werewolf", "Vampire"
        self.village = None  # The village this player belongs to
        self.has_acted = False
        self.alive = True
        self.has_voted = False
        self.ballots = 0
        self.defend = None
        # self.alive = True
   
    def state(self): 
        state = {
            "i": self.id,
            "l": self.life,
            "r": self.role,
            "v": self.village.id,
            "a": self.alive,
            "b": self.ballots,
        }
        return state 


    def assign_role(self, role):
        self.role = role

    def assign_village(self, village):
        self.village = village

    def revive(self, game):
        self.alive = True
        self.life = 100
        # move to random village
        self.move(game, random.randint(0, game.villages.__len__()))
        return self
    
    def defense(self, game, villager_idx: int):
        if not self.alive:
            return "dead"
        if self.has_acted:
            return "already acted"
        
        self.defend = self.village.get_players()[villager_idx]
        return "defence"

    def change_life(self, amount):
        if not self.alive:
            return
        self.life += amount; 
        if(self.life <= 0):
            self.life = 0
            self.alive = False 
        if(self.life > 100):
            self.life = 100
    
    def attack(self, game, villager_idx: int):
        if not self.alive:
            return "dead"
        if self.has_acted:
            return "already acted"
        
        if self.role == "n" and not self.village.night:
            return "not day v"
        if self.role == "v" and self.village.night:
            return "not night v"
        
        # if self.role == "v": # vampiers can only attack at night
        #     if not self.village.night:
        #         return "not night v"
        # if self.role == "n": # normal can only attack at day
        #     if self.village.night:
        #         return "not day n"
            
        other_player = self.village.get_players()[villager_idx]
        if(other_player == self.defend):
            other_player.change_life(-1)
            self.change_life(1)
            return "defended"
        if(other_player == self and self.role == "n"):
            return "cannot attack self " + self.role; 

        # normals beat werewolves and vampires at day, beat normals anytime
        if(self.role == "n"):
          if(other_player.role == "n"):
            other_player.change_life(-1)
            self.change_life(-1)
          elif(other_player.role == "w"):
            other_player.change_life(-1)
            self.change_life(1)
          elif(other_player.role == "v"):
            other_player.change_life(-1)
            self.change_life(1)

        # vampires lose against werewolves and vampires, beat normals
        if(self.role == "v"):
          if(other_player.role == "w"):
            other_player.change_life(1)
            self.change_life(-1)
          elif(other_player.role == "v"):
            other_player.change_life(1)
            self.change_life(1)
          elif(other_player.role == "n"):
            other_player.change_life(-1)
            self.change_life(1)
            
        # werewolves beat werewolves, beat vampires at day and normals at night
        if(self.role == "w"):
          if(other_player.role == "w"):
            other_player.change_life(-1)
            self.change_life(1)
          elif(other_player.role == "v" and not self.village.night):
            other_player.change_life(-1)
            self.change_life(1)
          elif(other_player.role == "n" and self.village.night):
            other_player.change_life(-1)
            self.change_life(1)

        # other_player.change_life(-1)
        self.has_acted = True
        return "acted"

    def vote(self, game, villager_idx: int):
        if self.has_voted:
            return "already voted"
        if self.village.night:
            return "not day"
        other_player = self.village.get_players()[villager_idx]
        other_player.ballots += 1
        self.has_voted = True
        return "voted"

    def move(self, game, village_idx: int):
        if not self.alive:
            return "dead"
        # villager cant move if acted 
        if self.has_acted and self.role == "n":
            return "already acted n"
        # vampires can move at night
        if not self.village.night and self.role == "v":
            return "not night v"
        # werewolves can move at day
        if self.village.night and self.role == "w":
            return "not day w"
        
        if village_idx < 0 or village_idx >= game.villages.__len__():
            return "invalid village"
        
        self.village.remove_player(self)
        self.village = game.villages[village_idx]
        self.village.add_player(self)
        # villager cant move without acting if not previously acted
        if role.role == "w" or role.role == "v":
           self.has_acted = True

        return "moved to village " + str(village_idx)
    
    def live(self, night):
        # Process player life logic
        # all things must die
        # warewolf loses life if they did not attack villager
        if self.role == "w": 
            if not night and not self.has_acted:
                self.change_life(-1)
            if night and self.has_acted:
                self.change_life(1)

        # vampire loses life if they did not attack villager
        if self.role == "v":
            if not night and self.has_acted:
                self.change_life(1)
            if night and not self.has_acted:
                self.change_life(-1)
            
        if self.role == "n" and self.has_acted:
            self.change_life(1)
        else 
            self.change_life(-1)
               
        # self.change_life(-10)
        self.has_acted = False

        if not night:
           self.has_voted = False

        if self.defend != None and self.role != "n":
           self.defend = None

        pass