import sys
import socket
import selectors
import types
import argparse

sel = selectors.DefaultSelector()
parser = argparse.ArgumentParser()

command_list = ["start_agv_follow"]

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print(f"Receive '{recv_data.decode()}' from {data.addr}")
            if recv_data.decode() in command_list:
                data.outb += b"OK"
            else:
                data.outb += b"Wrong command!"
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Send {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def server(ip, port):
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((ip, port))
    lsock.listen()
    print(f"Listening on {(ip, port)}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

if __name__ == '__main__':
    parser.add_argument("--ip", help="The server IP address", required=True)
    parser.add_argument("--port", help="The server port number", type=int, required=True)
    args = parser.parse_args()
    server(args.ip, args.port)