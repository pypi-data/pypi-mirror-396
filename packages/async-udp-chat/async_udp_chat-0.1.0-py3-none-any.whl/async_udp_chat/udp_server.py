# Andrea Diamantini
# async UDP server

import asyncio
import socket


async def udpServer(server_port):
    serverAddress = ("0.0.0.0", server_port)

    clientList = {}

    loop = asyncio.get_running_loop()

    # UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(serverAddress)
    udp_socket.setblocking(False)

    print("UDP server up and listening")

    # Listen for incoming datagrams
    while True:
        data, address = await loop.sock_recvfrom(udp_socket, 1024)
        msg = data.decode()

        # connection protocol
        if msg.startswith("CONNECT"):
            wordList = msg.split()
            name = wordList[1]
            clientList[address] = name
            continue

        sender = clientList.get(address, "boh")
        name_msg = f"[{sender}] {msg}"
        print(name_msg)
        for addr in clientList:
            if addr != address:
                udp_socket.sendto(name_msg.encode(), addr)
                print(f"sending to {addr}")

    udp_socket.close()


async def runServer(server_port):
    # async gather execution
    await asyncio.gather(
        udpServer(server_port),
    )


if __name__ == "__main__":
    server_port = 22222

    try:
        # async run server
        asyncio.run(runServer(server_port))

    # close on CTRL + C
    except KeyboardInterrupt:
        print("[INFO] Server closed.")
