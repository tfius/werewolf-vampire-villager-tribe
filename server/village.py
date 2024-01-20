class Village:
    def __init__(self, village_id):
        self.id = village_id
        self.players = []
        self.time = 0 # time goes from 0 to 24
        self.night = False  # Tracks whether it's day or night

    def add_player(self, player):
        self.players.append(player)
        player.assign_village(self)

    def remove_player(self, player):
        self.players.remove(player)

    def get_players(self):
        return self.players
    
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

        # print night if night or day if day
        # print(f'Village {self.id} in {"night" if self.night else "day"} time: {self.time}')
