# Andrea Diamantini
# UDP Client

import asyncio
import socket


async def sendMessage(udp_socket, serverAddress):
    loop = asyncio.get_running_loop()

    print(f"[INFO] Sending messages to {serverAddress}")
    print("[INFO] Write a message and press ENTER (/quit to exit)")
    print("-" * 50)

    while True:
        # async read input
        msg = await loop.run_in_executor(None, input)
        msg = msg.strip()

        if msg.lower() == "/quit":
            print("[INFO] Closing client... now press CTRL + C")
            break

        if msg:
            # sending msg
            udp_socket.sendto(msg.encode(), serverAddress)
            print(f"[ME] {msg}")

    udp_socket.close()


async def recvMessage(udp_socket):
    loop = asyncio.get_running_loop()

    print(f"[INFO] listening on {udp_socket.getsockname()}")

    while True:
        data = await loop.sock_recv(udp_socket, 1024)
        msg = data.decode()
        print(msg)

    udp_socket.close()


async def runClient(server_port):
    server_host = input("Server host or IP: ")
    name = input("Nome: ")

    serverAddress = (server_host, server_port)

    import random

    client_host = socket.gethostname()
    client_ip = socket.gethostbyname(client_host)
    client_port = random.randint(22223, 55555)
    clientAddress = (client_ip, client_port)

    # UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(clientAddress)
    udp_socket.setblocking(False)

    udp_socket.sendto(("CONNECT " + name).encode(), serverAddress)

    # async gather execution
    await asyncio.gather(
        sendMessage(udp_socket, serverAddress),
        recvMessage(udp_socket),
    )


if __name__ == "__main__":
    server_port = 22222

    try:
        # async run process
        asyncio.run(runClient(server_port))

    # close on CTRL + C
    except KeyboardInterrupt:
        print("[INFO] Closing client...")
