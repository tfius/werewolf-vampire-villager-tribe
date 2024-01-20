class Village:
    def __init__(self, village_id):
        self.id = village_id
        self.players = []
        self.time = 0 # time goes from 0 to 24
        self.night = False  # Tracks whether it's day or night
        self.governance = None  # Tracks the current governance

    def add_player(self, player):
        self.players.append(player)
        player.assign_village(self)

    def remove_player(self, player):
        self.players.remove(player)

    def get_players(self):
        return self.players
    
    # see who is winning in the village
    def governance(self):
        # count warewolves
        warewolves = [p for p in self.players if p.role == "w"]
        vampires = [p for p in self.players if p.role == "v"]
        villagers = [p for p in self.players if p.role == "n"]
        # if more werewolves then villagers and vampires
        if warewolves.__len__() >= villagers.__len__() + vampires.__len__():
            self.governance = "w"; #"werewolves win"
        # if more vampires then villagers and werewolves
        if vampires.__len__() >= villagers.__len__() + warewolves.__len__():
            self.governance = "v" # "vampires win"
        # if more villagers then vampires and werewolves
        if villagers.__len__() >= vampires.__len__() + warewolves.__len__():
            self.governance = "v" # "villagers win"
    
    def update(self):
        # Update village state, e.g., switch between day and night       
        self.time += 1
        if self.time == 24:
            self.time = 0

        previous_night = self.night
        self.night = self.time < 6 or self.time > 19

        if previous_night != self.night:
            # print(f"Village {self.id} is now in {'night' if self.night else 'day'} time: {self.time}")
            for player in self.players:
                player.live(self.night)

            if not self.night: # if day starts sort players by ballots
                # get players in village sorted by ballots
                sorted_players = sorted(self.players, key=lambda x: x.ballots, reverse=True)
                # self.players.sort(key=lambda x: x.ballots, reverse=True)
                # print(f"Village {self.id} sorted players by ballots: {self.players}")
                # kill player with most ballots
                if sorted_players[0].ballots > 0:
                   sorted_players[0].change_life(-100)
                   sorted_players[0].role = "e" # eliminated
                # reset ballots
                for player in self.players:
                    player.ballots = 0



        # print night if night or day if day
        # print(f'Village {self.id} in {"night" if self.night else "day"} time: {self.time}')
