# Andrea Diamantini
# TCP Client

import asyncio
import socket


async def sendMessage(tcp_socket):
    """async server msg sender routine"""

    loop = asyncio.get_running_loop()

    print("[INFO] Write a msg and press ENTER (or /quit to exit)")
    print("-" * 50)

    while True:
        # async input read
        msg = await loop.run_in_executor(None, input)

        if msg:
            msg = msg.strip()

            if msg.lower() == "/quit":
                print("[INFO] Closing client... Now press CTRL + C")
                break

            # send message with name
            msg = name + ": " + msg
            tcp_socket.sendall(msg.encode())


async def recvMessage(tcp_socket):
    """async server msg receiver routine"""

    loop = asyncio.get_running_loop()

    while True:
        data = await loop.sock_recv(tcp_socket, 1024)
        msg = data.decode()
        print(msg)


async def runClient(server_port):
    global name
    name = input("Name: ")

    host = input("Server PC Name or IP address: ")

    s_addr = (host, server_port)

    # Create TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setblocking(False)

    loop = asyncio.get_running_loop()

    await loop.sock_connect(tcp_socket, s_addr)
    print(f"[INFO] Connected to {s_addr}...")

    try:
        # async execution
        await asyncio.gather(
            sendMessage(tcp_socket),
            recvMessage(tcp_socket),
        )
    finally:
        tcp_socket.close()


if __name__ == "__main__":
    server_port = 33333

    try:
        # async process execution
        asyncio.run(runClient(server_port))

    # Close on CTRL + C
    except KeyboardInterrupt:
        print("[INFO] Closing client")
