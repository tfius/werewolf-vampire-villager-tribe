import random 
from village import Village
names = {
    "n": "Villager",
    "w": "Werewolf",
    "v": "Vampire",
    "n+e": "Villager Eliminated",
    "w+e": "Werewolf Eliminated",
    "v+e": "Vampire Eliminated",
}

KILL_RATE = 1
DIE_RATE = 1
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
        self.home_village = None
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
        # return { "player" : state }
        return state

    def assign_role(self, role):
        self.role = role

    def assign_village(self, village):
        self.village = village

    def revive(self, game):
        self.alive = True
        self.life = 100
        self.ballots = 0
        self.defend = None
        self.home_village = None
        # move to random village
        self.move(game, random.randint(0, game.villages.__len__()))
        return { "msg": "revived" }
    
    def defense(self, game, villager_idx: int):
        if not self.alive:
            return { "msg":"already voted" }
        if self.has_acted:
            return { "msg":"already acted" }
        
        if villager_idx < 0 or villager_idx >= self.village.get_players().__len__():
            return { "msg": "invalid villager " + str(villager_idx) }
        
        self.defend = self.village.get_players()[villager_idx]
        return { "defense": self.defend.id }

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
            return { "msg": "dead" }
        if self.has_acted:
            return { "msg": "already acted" }
        
        if self.role == "v" and not self.village.night:
            return { "msg": "not night for vampire" }
        if self.role == "n" and self.village.night:
            return { "msg": "only during day" }
        
        if villager_idx < 0 or villager_idx >= self.village.get_players().__len__():
            return { "msg": "invalid villager " + str(villager_idx) }

        player_damage = 0
        target_damage = 0
                   
        other_player = self.village.get_players()[villager_idx]
        if(other_player == self.defend):
            target_damage = -KILL_RATE
            player_damage = KILL_RATE
            return { "msg": "defended" }
        if(other_player == self and self.role != "n"):
            return { "msg": "cannot attack self " + self.role }

        # normals beat werewolves and vampires at day, beat normals anytime
        if(self.role == "n"):
          if(other_player.role == "n"):
            target_damage = -KILL_RATE
            player_damage = -KILL_RATE
          elif(other_player.role == "w"):
            target_damage = -KILL_RATE
            player_damage = KILL_RATE
          elif(other_player.role == "v"):
            target_damage = -KILL_RATE
            player_damage = KILL_RATE

        # vampires lose against werewolves and vampires, beat normals
        if(self.role == "v"):
          if(other_player.role == "w"):
            target_damage = KILL_RATE
            player_damage = -KILL_RATE
          elif(other_player.role == "v"):
            target_damage = KILL_RATE
            player_damage = KILL_RATE
          elif(other_player.role == "n"):
            target_damage = -KILL_RATE
            player_damage = KILL_RATE
            
        # werewolves beat werewolves, beat vampires at day and normals at night
        if(self.role == "w"):
          if(other_player.role == "w"):
            target_damage = -KILL_RATE
            player_damage = KILL_RATE
          elif(other_player.role == "v" and not self.village.night):
            target_damage = -KILL_RATE
            player_damage = KILL_RATE
          elif(other_player.role == "n" and self.village.night):
            target_damage = -KILL_RATE
            player_damage = KILL_RATE

        other_player.change_life(target_damage)
        self.change_life(player_damage)

        # other_player.change_life(-1)
        self.has_acted = True
        return { "msg": "acted against " + other_player.id, 
                 "player_damage": target_damage,
                 "target_damage": player_damage }

    def vote(self, game, villager_idx: int):
        if self.has_voted:
            return { "msg":"already voted" }
        if self.village.night:
            return { "msg": "not day" }
        if villager_idx < 0 or villager_idx >= self.village.get_players().__len__():
            return { "msg": "invalid villager " + str(villager_idx) }
        
        other_player = self.village.get_players()[villager_idx]
        if other_player == self:
            return { "msg": "cannot vote for self" }
        if other_player.alive == False:
            return { "msg": "cannot vote for dead" }
        
        other_player.ballots += 1
        self.has_voted = True
        return { "msg":"voted" }

    def move(self, game, village_idx: int):
        if not self.alive:
            return { "msg": "dead" }
        # villager cant move if acted 
        if self.has_acted and self.role == "n":
            return { "msg":"already acted n" }
        # vampires can move at night
        if not self.village.night and self.role == "v":
            return { "msg": "not night for vampire" }
        # werewolves can move at day
        if self.village.night and self.role == "w":
            return { "msg": "not a day for werewolf" }
        
        if village_idx < 0 or village_idx >= game.villages.__len__():
            return { "msg": "invalid village " + str(village_idx) }
        
        self.village.remove_player(self)
        self.village = game.villages[village_idx]
        self.village.add_player(self)

        # villager can move without acting if not previously acted
        # if self.role == "w" or self.role == "v":
        #    self.has_acted = True

        return { "move": village_idx }
    
    def inspect(self, game, villager_idx: int):
        if villager_idx < 0 or villager_idx >= self.village.get_players().__len__():
            return { "msg": "invalid villager " + str(villager_idx) }
        
        other_player = self.village.get_players()[villager_idx]

        game_state = {
            "v": other_player.village.id,
            "t": other_player.village.time,
            "n": other_player.village.night,
            "p": other_player.state()
            # "p": [ player.state() for player in other_player.village.players]
        }
        return { "inspect" : game_state }

    def live(self, night):
        # Process player life logic, all things must die
        # warewolf loses life if they did not attack
        if self.role == "w": 
            if night:
               if self.has_acted:
                  self.change_life(-DIE_RATE)
               self.has_acted = False

        # vampire loses life if they did not attack 
        if self.role == "v":
            if not night:
               if self.has_acted:
                  self.change_life(-DIE_RATE)
               self.has_acted = False
            
        if self.role == "n": 
            if self.has_acted:
               self.change_life(DIE_RATE)
            else:
               if night:
                  self.change_life(-DIE_RATE)
            self.has_acted = False
               
        # self.change_life(-10)
        # self.has_acted = False

        if not night:
           self.has_voted = False

        if self.defend != None and self.role != "n":
           if night and self.role == "w":
              self.defend = None
           if not night and self.role == "v":
              self.defend = None

        pass
