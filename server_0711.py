import time
import socket
import selectors
import types
import argparse

sel = selectors.DefaultSelector()
parser = argparse.ArgumentParser()

command_list = ["self_move_OW", "self_move_WA", "self_move_AO"]

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
            message = recv_data.decode()
            print(f"Receive '{message}' from {data.addr}")

            if message == "self_move_OW":
                print("開始移動到配膳間")
                time.sleep(3)
                print("抵達配膳間, 停止移動")
                print("病人A想喝水")
                data.outb += b"OK"

            elif message == "self_move_WA":
                print("已收到照護人員放置的水")
                print("將從配膳間前往病房A")
                time.sleep(3)
                print("抵達病房A, 停止移動")
                print("水帶來了")
                data.outb += b"OK"

            elif message == "self_move_AO":
                print("開始移動到護理站")
                time.sleep(3)
                print("已到達護理站, 停止移動")
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