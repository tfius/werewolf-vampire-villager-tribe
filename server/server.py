import socket
import threading
import asyncio
import json
import uuid
import hashlib
import base64

from game import Game
from village import Village
from player import Player  # Assuming these are defined

# to be read from environment variables
PORT = 65432
HOST = '127.0.0.1'
HOUR_IN_SECONDS = 0.0001
def generate_short_uuid():
    # Generate a UUID
    uuid_str = str(uuid.uuid4())

    # Hash the UUID
    hash_object = hashlib.sha256(uuid_str.encode())
    hashed_uuid = hash_object.digest()

    # Encode the hash using base64
    short_uuid = base64.urlsafe_b64encode(hashed_uuid)[:22]  # Trim padding
    return str(short_uuid.decode())

class GameServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port        
        self.connected_clients = {}
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = {}  # List of Player objects
        self.game = Game()

    async def add_village(self, village):
        self.game.add_village(village)

    # start server
    async def start_server(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    async def game_loop(self):
        while True:
            # print("Updating server state")
            self.game.update()  # Update the game state
            game_state = self.game.get_state()  # Get the current state of the game
            await self.broadcast(json.dumps(game_state))  # Broadcast the game state
            await asyncio.sleep(HOUR_IN_SECONDS)  # Wait for a specified interval before the next update

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        new_player = Player(generate_short_uuid())  # Player initialization logic
        new_player = self.game.add_player(new_player)
        self.connected_clients[writer] = {'addr': addr, 'reader': reader, 'writer': writer, "player": new_player } 
        print(f"{addr} is {new_player.state()}")
        self.players[new_player.id] = new_player

        try:
           # reply with new_player 
           await self.send(writer, json.dumps( {"new_player": new_player.state()} ) )  # Send the player state to the client

           while True:
                print(f"{addr} Waiting for")
                data = await reader.read(1024)
                if not data:
                    print(f"{addr} Connection closed")
                    break
                message = data.decode()
                print(f"from {addr} received {message}")               
                asyncio.create_task(self.process(writer, new_player, message))

        except asyncio.CancelledError:
            print(f"Canceled Error {addr}")
            pass
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print(f"Closing the connection from {addr}")
            del self.connected_clients[writer]
            writer.close()
            await writer.wait_closed()

    async def send(self, writer, message):
        # print(f"send {message}")
        writer.write(message.encode())
        await writer.drain()

    async def process(self, writer, player, message):
        data = json.loads(message) 
        result = "unknown command"
        print(f"{player.id} process {data}") # Process the message and update game state
        if "c" in data:
            incoming = data["c"] 
            # split command into command name and argument from ("Enter command (a)ttack player (d)efend from player (v)ote player (c)hat text (q)uit ")
            cmd = incoming.split(" ")
            command = cmd[0]
            argument = None
            # argument is index of player to attack, defend, vote, chat
            try: 
               argument = cmd[1] if cmd.__len__() >= 1 else None
            except Exception as e:
                pass

            try:
                match command:
                  case "a": # act
                    result = player.attack(self.game, int(argument))  
                  case "m": # move to village
                    result = player.move(self.game, int(argument))
                  case "d": # defend from player in village
                    result = player.defense(self.game, int(argument))
                  case "v": # vote for player in village
                    result = player.vote(self.game, int(argument))
                  case "i": # inspect village
                    result = player.inspect(self.game, int(argument))  

                  case "c":
                    # player.chat()
                    pass    
                  case "r":
                    if not player.alive:
                          self.game.assign_new_role(player)
                          result = player.revive(self.game)
                  case _: 
                    result = "Unknown command"
                
            except ValueError:
                print(f"Cannot convert {argument} to integer")
            except Exception as e:
                print(f"Error: {e}")
                result = "cannot perform action " + f"Error: {e}"
                pass

        print(f"{player.id} {data} result {result}")
        await self.send(writer, json.dumps({"message": result}))
        
    async def broadcast(self, message):
        # Create a list of coroutines
        tasks = [self.send(writer, message) for writer in self.connected_clients]
        # Run the coroutines concurrently
        await asyncio.gather(*tasks)


async def main():
    server = GameServer()
    loop = asyncio.get_running_loop()

    # Schedule the game loop to run concurrently with the server
    loop.create_task(server.game_loop())

    # Start the server
    await server.start_server()

asyncio.run(main())
