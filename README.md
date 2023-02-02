# Server
## How to use
```bash
python server.py [-h] --ip IP --port PORT
```
* --ip: The server IP address
* --port: The server port number

It will create a server listen on `IP:PORT` and accept connection from miltiple clients. The server now can only accept command `API1`, `API2`, and `API3` and returns `OK` to the client. Otherwise, it returns `Wrong command!` to the client.

# Client
## How to use
```bash
client.py [-h] --ip IP --port PORT --command COMMAND
```
* --ip: The server IP address you want to connect
* --port: The server port number listend
* --command: The command you want to send to server

It will start a client connect to `IP:PORT` and send a `command ` to the server. The server will return `OK` if the command can be dealt with by the server.