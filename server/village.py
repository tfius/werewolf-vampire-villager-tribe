class Village:
    def __init__(self, village_id):
        self.id = village_id
        self.players = []
        self.time = 0 # time goes from 0 to 24
        self.night = False  # Tracks whether it's day or night
        self.governance = None  # Tracks the current governance
        self.established_by = None # player that established village
        self.days_without_people = 0

    def state(self):
        # Return the current state of the village
        village_state = {
            "i": self.id,
            "t": self.time,
            "n": self.night,
            "g": self.governance,
            "p": [ player.state() for player in self.players],
            "e": self.established_by.id if self.established_by != None else "",
            "d": self.days_without_people
        }
        return { "village": village_state }

    def add_player(self, player):
        self.players.append(player)
        player.assign_village(self)

    def remove_player(self, player):
        self.players.remove(player)

    def get_players(self):
        return self.players
    
    # see who is winning in the village
    def check_governance(self):
        governance = None
        if self.players.__len__() == 0:
            governance = "n"
        # count warewolves
        warewolves = [p for p in self.players if p.role == "w"]
        vampires = [p for p in self.players if p.role == "v"]
        villagers = [p for p in self.players if p.role == "n"]
        # if more werewolves then villagers and vampires
        if warewolves.__len__() >= villagers.__len__() + vampires.__len__():
            governance = "w"; #"werewolves lead"
        # if more vampires then villagers and werewolves
        if vampires.__len__() >= villagers.__len__(): # + warewolves.__len__():
            governance = "v" # "vampires lead"
        # if more villagers then vampires and werewolves
        if villagers.__len__() >= vampires.__len__() + warewolves.__len__():
            governance = "n" # "villagers lead"

        if governance != self.governance:
            self.governance = governance
            return { "governance": governance, "village_id": self.id }
        
        return None
    
    def update(self):
        # Update village state, e.g., switch between day and night       
        self.time += 1
        if self.time == 24:
            self.time = 0

        previous_night = self.night
        self.night = self.time < 6 or self.time > 19
        actions = []

        if previous_night != self.night:
            # actions.append( { "time_of_day": "night" if self.night else "day", "village_id": self.id } ) 

            if self.night:
                action = self.check_governance()
                if action is not None:
                    actions.append(action)
                
            # # print(f"Village {self.id} is now in {'night' if self.night else 'day'} time: {self.time}")
            # for player in self.players:
            #     action = player.live(self.night)

            if not self.night and self.players.__len__()>0: # if day starts sort players by ballots
                # get players in village sorted by ballots
                sorted_players = sorted(self.players, key=lambda x: x.ballots, reverse=True)
                # remove player with role that has +e 
                sorted_players = [p for p in sorted_players if not p.role.endswith("+e")]
                # self.players.sort(key=lambda x: x.ballots, reverse=True)
                # print(f"Village {self.id} sorted players by ballots: {self.players}")
                # kill player with most ballots
                if sorted_players[0].ballots > 0:
                   sorted_players[0].change_life(-100)
                   sorted_players[0].role = sorted_players[0].role+"+e" # w|v|n eliminated
                   actions.append( { "eliminated": sorted_players[0].id } )
                # reset ballots
                for player in self.players:
                    player.ballots = 0

        if actions.__len__() > 0:
            print(f"Village {self.id} actions: {actions}")
        return actions

        # print night if night or day if day
        # print(f'Village {self.id} in {"night" if self.night else "day"} time: {self.time}')
