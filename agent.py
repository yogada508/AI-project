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
        self.location_list = [str(i) for i in range(1,26)] # 1 ~ 25
        self.room_a = [str(i) for i in range(5,8)] # 5 ~ 7
        self.room_o = [str(i) for i in range(17,26)] # 17 ~ 25
        self.robot_location = "20"

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
                print(f"Receive '{recv_data.decode()}' from {data.addr}")
                # 量測團隊
                if recv_data.decode() == "measurement_done":
                    data.outb += b"OK"
                    # self.forward_command("start_agv_follow")

                # 語音團隊
                elif recv_data.decode() == "follow_me":
                    data.outb += b"OK"
                    self.forward_command("start_agv_follow")
                elif recv_data.decode() == "go_to_nursing_station":
                    data.outb += b"OK"
                    self.forward_command("self_move_BO")
                elif recv_data.decode() == "stop":
                    data.outb += b"OK"
                    self.forward_command("end_agv_follow")

                # 定位團隊
                elif recv_data.decode() in self.location_list:
                    data.outb += b"OK"
                    self.robot_location = recv_data.decode()
                    print("Update robot location to:", self.robot_location)

                # 腦波團隊
                elif recv_data.decode() == "Idle":
                    data.outb += b"OK"
                elif recv_data.decode() == "move":
                    data.outb += b"OK"
                    if self.robot_location in self.room_a:
                        self.forward_command("self_move_AO")
                    elif self.robot_location in self.room_o:
                        self.forward_command("self_move_OA")
                     
                # 機器人團隊
                elif recv_data.decode() == "agv_shut_down":
                    data.outb += b"OK"
                    self.forward_command("debug")
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
            print(f"Connect to {dst_addr}")

            s.sendall(command.encode())
            print(f"Send command: {command}")

            data = s.recv(1024)
            print(f"Receive: {data.decode()}")

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