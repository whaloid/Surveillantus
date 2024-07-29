import os
import json
import time

with open("tokens.json","r") as f:
    clients=json.load(f)["clients"]

num_clients=5 #メモリのスパイクを抑えるため、ログイン時刻を分散させる。
for client in clients:
    os.system("python3 run_selfspybot.py {} &".format(client["token"]))
    time.sleep(30/num_clients)