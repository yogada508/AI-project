import sys
import socket
import selectors
import types
import argparse

'''
機器人團隊
(1) start_agv_follow 開始追隨, 
(2) end_agv_follow 停止追隨, 
(3) self_move 軌跡追蹤,   
(4) self_move_hold 軌跡追蹤的途中暫停,   
(5) self_move_resume 繼續進行軌跡追蹤
(6) agv_shut_down

語音團隊
(1) follow me
(2) go to nursing station

腦波團隊
(1) Idle
(2) move

量測團隊
(1) measurement_done
'''

parser = argparse.ArgumentParser()

class Agent():
    def __init__(self, h_ip, h_port, dst_ip, dst_port) -> None:
        self.ip = h_ip
        self.port = h_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.sel = selectors.DefaultSelector()

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                message = recv_data.decode()
                print(f"Receive '{message}' from {data.addr}")

                # 腦波團隊 護理站去配膳間
                if message == "give_me_water":
                    self.forward_command("self_move_OW")
                    data.outb += b"OK"

                 # 腦波團隊 機器人回護理站
                elif message == "robot_go_back":
                    self.forward_command("self_move_AO")
                    data.outb += b"OK"
                
                # 語音團隊 配膳間去病房
                elif message == "put_water_into_robot":
                    self.forward_command("self_move_WA")
                    data.outb += b"OK"

                else:
                    data.outb += b"Wrong Command"
                
            else:
                print(f"Closing connection to {data.addr}")
                self.sel.unregister(sock)
                sock.close()

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print(f"Send {data.outb!r} to {data.addr}")
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def forward_command(self, command):
        dst_addr = (self.dst_ip, self.dst_port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(dst_addr)
            print("-----------------------------------")
            print(f"Forward '{command}' to robot")

            s.sendall(command.encode())

            data = s.recv(1024)
            print(f"Receive: {data.decode()} from robot")
            print("-----------------------------------")

    def run(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((self.ip, self.port))
        lsock.listen()
        print(f"Listening on {(self.ip, self.port)}")
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

if __name__ == '__main__':
    parser.add_argument("--h_ip", help="The host server IP address", required=True)
    parser.add_argument("--h_port", help="The host server port number", type=int, required=True)
    parser.add_argument("--dst_ip", help="The destination server IP address", required=True)
    parser.add_argument("--dst_port", help="The destination server port number", type=int, required=True)
    args = parser.parse_args()
    
    agent = Agent(args.h_ip, args.h_port, args.dst_ip, args.dst_port)
    agent.run()