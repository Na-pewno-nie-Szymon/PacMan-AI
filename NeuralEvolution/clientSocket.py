import socket
import json
import time

HOST = "127.0.0.1"
PORT = 5555

def send_msg(sock, msg):
    sock.send(msg.encode())


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

moves = ["UP", "RIGHT", "DOWN", "LEFT"]
i = 0
while True:
    move = moves[i%4]
    i+=1

    print("Sending", move)
    send_msg(client, move)
    data = client.recv(1024).decode()
    # state = recv_msg(client)
    # print("Recived state:", state["pacman"])


