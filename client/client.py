import asyncio
import json
import uuid 
import threading
import queue
command_queue = queue.Queue() # Global variable to store the command
villages = []
players = []

names = {
    "n": "Villager",
    "w": "Werewolf",
    "v": "Vampire",
    "d": "Doctor",
    "s": "Seer",
    "g": "Guardian",
    "p": "Priest",
    "h": "Hunter",   
}

def get_input():
    try:
      while True:
        key = input("Enter command (a)ttack [villager], (d)efend [villager], (v)ote [villager], (i)nspect [villager], w(ho) am i , (m)ove [village], (c)hat [message] (q)uit ")
        command_queue.put(key)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)

# Start the input thread
input_thread = threading.Thread(target=get_input)
input_thread.start()

class Player:
    def __init__(self):
        self.id = ""
        self.life = 100
        self.role = None
        self.village = None
        self.alive = False
        self.ballots = 0
        self.eliminated = False

    def state(self): 
        state = {
            "i": self.id,
            "r": self.role,
            "l": self.life,
            "v": self.village,
            "a": self.alive,
            "b": self.ballots,
        } 
        return state
    

async def process_message(writer, message, player: Player):
    global villages
    global players
    # check if message is json
    try:
        data = json.loads(message)
        # print(f"Client received: {data}")
        if "move" in data:
            print(f"Moved to {data['move']}")
            player.village = data["move"]
            # player.village = data["move"]
        # see if data is in form of { "msg": "message"}
        if "msg" in data:
            print(data["msg"])
        if "inspect" in data:
            print("inspect: " + str(data["inspect"]))            
        if "village" in data:
           print("village: " + str(data["village"]))
        if "new_village" in data:
           print("new_village: " + str(data["new_village"]))
        if "player" in data:
            print("player: " + str(data["player"]))
        if "player_damage" in data:
            print("player_damage: " + str(data["player_damage"]))            
        if "target_damage" in data:
            print("target_damage: " + str(data["target_damage"]))            
        if "eliminated" in data:
            print("eliminated: " + str(data["eliminated"]))            
        if "governance" in data:
            print("governance: " + str(data["governance"]))
            print("in village: " + str(data["village_id"]))
            print("governance: " + str(data))
        if "removed_village" in data:
            print("removed_village: " + str(data["removed_village"]))

        if "game" in data:
            # data["game"]  =  {'v': [{'0': 22, 'night': True}, {'1': 22, 'night': True}], 'p': [{'i': 'JVQE4n68Jh4I89Z-RYx88X', 'l': 100, 'r': 'v', 'v': 1, 'a': True, 'b': 0, 'e': False}]}
            # print("got game", data["game"])
            
            villages = list(data["game"]["v"]) # get all villages
            players = list(data["game"]["p"]) # get all players

            # get all players 
            # get village player is in 
            # village = [v for v in data["game"]["v"] if player.village == v.keys()[0]]
            # print("you are in village", player.village, villages)
            pass 
        if "message" in data:
            print("message", data["message"])
        if "new_player" in data: # new player info
            new_player = data["new_player"]
            player.id = new_player["i"] # id
            player.role = new_player["r"] # role
            player.life = new_player["l"] # life
            player.village = new_player["v"] # village
            player.alive = new_player["a"] # alive
            player.ballots = new_player["b"] # ballots
            player.eliminated = new_player["e"] # eliminated

            print(f"{names[player.role]} '{player.id}' {player.life} points in village:{player.village}")
            await send_message(writer, json.dumps(player.state()))

        if "v" in data: # villages
            # print(f"Villages: {data['v']}")
            pass

        if "p" in data: # players
            # find myplayer in players 
            myplayer = [p for p in data['p'] if p['i'] == player.id][0]

            # if life is different update myplayer
            if myplayer["l"] != player.life:
               player.life = myplayer["l"]
               print(f"My {names[player.role]} life is {player.life}")
               if myplayer["a"] != player.alive:
                  player.alive = myplayer["a"]
                  print(f"State of {names[player.role]} is {player.alive} (R)evive ? ")
    except ValueError:
        print(f"Cannot convert '{message}' to json")
    except Exception as e:
        print(f"Error: {e}")
        pass

async def listen_for_messages(reader, writer, player: Player):
    while True:
        try:
          data = await reader.read(4096)
          if data:
            messages = data.decode().split('\n')  # assuming '\n' is the delimiter

          for message in messages:
            await process_message(writer, message, player) # Process received message (update game state, player role, etc.)

        except ConnectionResetError:
          print("Connection lost, trying to reconnect...")
          break
        except Exception as e:
          print(f"Client Listen Error: {e} {message}")
          pass
            
        if not command_queue.empty():
            command = command_queue.get()

            cmd = command.split(" ")  
            # check to see if there are 2 arguments and get key from villages or players list (not correct as player might not be in village and command will fail)
            if cmd.__len__() == 2:
                # check if second argument is a number and if it is get player id from players list
                try:
                    if cmd[0] == "m":
                       id = villages[int(cmd[1])]["vkey"]
                    else:
                       id = players[int(cmd[1])]["i"]
                    command = cmd[0] + " " + id
                except Exception as e:
                    pass

            print(f"c: {command}")
            await send_message(writer, json.dumps({"c": command}))

async def send_message(writer, message):
    writer.write(message.encode())
    await writer.drain()

async def recieve(host, port):
    player = Player()
    reconnect_attempts = 0
    max_reconnect_attempts = 15
    
    while reconnect_attempts < max_reconnect_attempts:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            print("Connected to the server.")

            # keep reading messages from the server
            await asyncio.create_task(listen_for_messages(reader, writer, player))

            # if not command_queue.empty():
            #     command = command_queue.get()
            #     print(f"Command: {command}")
            #     await send_message(writer, json.dumps({"command": command}))
            
            # Start listening for messages from the server
            # await listen_for_messages(reader, writer, player)
            break
        except (ConnectionRefusedError, OSError):
            reconnect_attempts += 1
            print(f"Connection failed, retrying... ({reconnect_attempts})")
            await asyncio.sleep(3)  # Wait before retrying
        except Exception as e:
            print(f"An error occurred: {e}")
            break
        finally:
            writer.close()
            await writer.wait_closed()
            print("Writer closed.")

    print("Connection closed.")



asyncio.run(recieve('127.0.0.1', 65432))
