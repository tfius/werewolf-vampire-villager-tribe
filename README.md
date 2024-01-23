# Werewolf-Vampire-Villager-Tribe
Extended social deduction game based on "Werewolf" game by Dimitry Davidoff.

Involves a group of players, each assigned a secret role as either a
 - Werewolf (knows who other werewolfs are)
 - villager (they know nothing)
 - Vampire (no one knows)

Game proceeds in alternating night and day phases.

At night, the werewolves secretly choose a villager to attack, while during the day, all players debate and vote to eliminate a suspected werewolf or vampire. 

The game continues until all the werewolves and vampires are eliminated or the werewolves outnumber the villagers. 


## Mechanics 
- Player's can revive to different role and village after they are elimintated.
- They can only attack others within the village they are in
- Moving to other villages 
  - Vampires can move at night
  - Werewolfs can move at day 
  - Villagers can move anytime if not acted  
- Valar Morgulis (all men must slowly die)
  - Vampires slowly die if not acted during night 
  - Werewolfs slowly die if acted during day
  - Villagers gain life if acted and slowly die during night
- Voting only during day.
- Elimination happens in the morning, ballots are reset. 
- Village is governed by:
  - villagers if they outnumber werewolfs and vampires
  - werewolfs if they outnumber villagers and vampires
  - vampires if they outnumber werewolfs 
- Anyone can defend agains attack of other player
  - villagers never loose defence
  - werewolfs loose defence at night 
  - vampires loose defence at day
- Each hour is 12s long. Day is from 6h to 19h.
- 

***Game highlights the challenge an uninformed majority (the villagers) faces against an informed minority (the werewolves).*** 

This dynamic makes the game an interesting study in social dynamics, communication, and strategy. The werewolves have the advantage of knowing each other's identities and can plan their actions accordingly, While the villagers must rely on discussion, observation, and deduction to make their decisions. 

## How to run
### start server
`python server.py`

### start client
`python client.py`

### Requirements 
Python > 3.10


## Remarks
This came out as Friday night project after a beautiful snowy day. Maybe a TikTok game after another snowy day. 
