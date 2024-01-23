import asyncio
import json
import uuid 
import threading
import queue
command_queue = queue.Queue() # Global variable to store the command

names = {
    "n": "Villager",
    "w": "Werewolf",
    "v": "Vampire",
    "n+e": "Villager Eliminated",
    "w+e": "Werewolf Eliminated",
    "v+e": "Vampire Eliminated",
}

# def print_at_position(text, x=0, y=0):
#      # Move the cursor to the position (x, y)
#      print(f'\033[{y};{x}H{text}', end='', flush=True)

# Print 'Hello, world!' at position (5, 10)
# print_at_position('Hello, world!', 5, 10)

def get_input():
    while True:
        key = input("Enter command (a)ttack [villager] (d)efend [villager] (v)ote [villager] (m)ove [village] (c)hat (q)uit ")
        command_queue.put(key)

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
    
# async def process_command(message, player: Player):
#     # check if message is a command
#     if "command" in data:
#         command = data["command"]
#         print(f"Client received command: {command}")
#         if command == "quit":
#             print("Quitting...")
#             break

async def process_message(writer, message, player: Player):
    # check if message is json
    try:
        data = json.loads(message)
        # print(f"Client received: {data}")
        if "move" in data:
            print(f"Moved to {data['move']}")
            # player.village = data["move"]
        # see if data is in form of { "msg": "message"}
        if "msg" in data:
            print(data["msg"])
        if "players" in data:
            print("got players " + str(data["players"]))            
        if "village" in data:
            print("got village " + str(data["village"]))
        if "game" in data:
            # print("got game", data["game"])
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
