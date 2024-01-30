class Village:
    def __init__(self, village_id):
        self.id = village_id
        self.players = {}
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
            "p": [ player.state() for player in self.players.values()],
            "e": self.established_by.id if self.established_by != None else "",
            "d": self.days_without_people
        }
        return { "village": village_state }

    def add_player(self, player):
        self.players[player.id] = player
        player.assign_village(self)

    def remove_player(self, player):
        del self.players[player.id]
        #self.players.remove(player)

    def get_players(self):
        return self.players
    
    # see who is winning in the village
    def check_governance(self):
        governance = None
        if self.players.__len__() == 0:
            governance = "n"
        # count warewolves
        warewolves = 0
        vampires = 0
        villagers = 0
        # iterate and count player roles 
        for player in self.players.values():
            if player.role == "w":
                warewolves += 1
            if player.role == "v":
                vampires += 1
            if player.role == "n":
                villagers += 1

        # if more werewolves then villagers and vampires
        if warewolves >= villagers + vampires:
            governance = "w"; #"werewolves lead"
        # if more vampires then villagers and werewolves
        if vampires  >= villagers + warewolves: 
            governance = "v" # "vampires lead"
        # if more villagers then vampires and werewolves
        if villagers >= vampires + warewolves:
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
            for player in self.players.values():
                action = player.live(self.night)

            if not self.night and self.players.values().__len__()>0: # if day starts sort players by ballots
                # get players in village sorted by ballots
                sorted_players = sorted(self.players.values(), key=lambda x: x.ballots, reverse=True)
                # remove player that are eliminated                
                sorted_players = [p for p in sorted_players if p.eliminated == False]
                # self.players.sort(key=lambda x: x.ballots, reverse=True)
                # print(f"Village {self.id} sorted players by ballots: {self.players}")
                # kill player with most ballots
                if sorted_players.__len__() > 0 and sorted_players[0].ballots > 0:
                   sorted_players[0].change_life(-100)
                   sorted_players[0].eliminated = True
                   actions.append( { "eliminated": sorted_players[0].id } )

                # reset ballots
                for player in self.players.values():
                    player.ballots = 0

        if actions.__len__() > 0:
            print(f"Village {self.id} actions: {actions}")
        return actions

        # print night if night or day if day
        # print(f'Village {self.id} in {"night" if self.night else "day"} time: {self.time}')
