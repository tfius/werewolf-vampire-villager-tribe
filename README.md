# werewolf-vampire-villager-tribe
Extended social deduction game based on werewolf game 

Involves a group of players, each assigned a secret role as either a
 - Werewolf (knows who other werewolfs are)
 - villager (they know nothing)
 - Vampire (no one knows)

Game proceeds in alternating night and day phases.

At night, the werewolves secretly choose a villager to attack, while during the day, all players debate and vote to eliminate a suspected werewolf or vampire. 

The game continues until all the werewolves and vampires are eliminated or the werewolves outnumber the villagers. 


### Mechanics 
- Player's can revive to different role and village after they are elimintated.
- They can only attack others within the village they are in 
- Vampires can move at night
- Werewolfs can move at day 
- Villagers can move anytime if not acted 
- Valar Morgulis (all men must slowly die)
  - Vampires slowly die if not acted during night 
  - Werewolfs slowly die if acted during day
  - Villagers gain life if acted and slowly die during night
- voting during day 
- elimination in the morning 
- Village is governed by:
  - villagers if they outnumber werewolfs and vampires
  - werewolfs if they outnumber villagers and vampires
  - vampires if they outnumber werewolfs 
- Anyone can defend agains attack of other player
  - villagers never loose defence
  - werewolfs loose defence at night 
  - vampires loose defence at day

***Game highlights the challenge an uninformed majority (the villagers) faces against an informed minority (the werewolves).*** 

This dynamic makes the game an interesting study in social dynamics, communication, and strategy. The werewolves have the advantage of knowing each other's identities and can plan their actions accordingly, While the villagers must rely on discussion, observation, and deduction to make their decisions. 

## start server
`python server.py`

## start client
`python client.py`

Python > 3.10