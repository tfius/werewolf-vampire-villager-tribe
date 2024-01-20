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
}

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

    def get_state(self): 
        state = {
            "i": self.id,
            "r": self.role,
            "l": self.life,
            "v": self.village,
            "a": self.alive,
            "b": self.ballots,
        } 
        return state

async def listen_for_messages(reader, writer, player: Player):
    while True:
        data = await reader.read(1024)
        if data:
            message = data.decode()
            # print(f"Client received: {message}")
            # check if message is json
            try:
                data = json.loads(message)
                if "message" in data:
                    print(data["message"])
                if "new_player" in data: # new player info
                   new_player = data["new_player"]
                   player.id = new_player["i"] # id
                   player.role = new_player["r"] # role
                   player.life = new_player["l"] # life
                   player.village = new_player["v"] # village
                   player.alive = new_player["a"] # alive
                   player.ballots = new_player["b"] # ballots

                   print(f"I'm '{player.id}' in village {player.village} with role {player.role} and life {player.life}")
                   await send_message(writer, json.dumps(player.get_state()))

                if "v" in data: # villages
                    # print(f"Villages: {data['v']}")
                    pass

                if "p" in data: # players
                    # find myplayer in players 
                    myplayer = [p for p in data['p'] if p['i'] == player.id][0]

                    # if life is different update myplayer
                    if myplayer["l"] != player.life:
                       player.life = myplayer["l"]
                       # player.alive = myplayer["a"]
                       print(f"My {names[player.role]} life is {player.life} ")
                       if myplayer["a"] != player.alive:
                        player.alive = myplayer["a"]
                        print(f"State of {names[player.role]} is {player.alive} (R)evive ? ")



                # check if message is a command
                if "command" in data:
                    command = data["command"]
                    print(f"Client received command: {command}")
                    if command == "quit":
                        print("Quitting...")
                        break
                    elif command == "attack":
                        print("Attacking...")
                    elif command == "defend":
                        print("Defending...")
                    else:
                        print("Unknown command.")
            except Exception as e:
                print(f"Error: {e}")
                pass


            # Process received message (update game state, player role, etc.)
        else:
            print("Server connection closed.")
            break

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
