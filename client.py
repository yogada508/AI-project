import sys
import socket
import selectors
import types
import argparse

sel = selectors.DefaultSelector()
parser = argparse.ArgumentParser()

def client(ip, port, command):
    server_addr = (ip, port)
    message = " ".join(command)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_addr)
        print(f"Connect to {server_addr}")

        s.sendall(message.encode())
        print(f"Send command: {message}")

        data = s.recv(1024)
        print(f"Receive: {data.decode()}")


if __name__ == '__main__':
    parser.add_argument("--ip", help="The server IP address you want to connect", required=True)
    parser.add_argument("--port", help="The server port number listend", type=int, required=True)
    parser.add_argument("--command", help="The command you want to send to server", required=True, nargs="+")
    args = parser.parse_args()
    client(args.ip, args.port, args.command)