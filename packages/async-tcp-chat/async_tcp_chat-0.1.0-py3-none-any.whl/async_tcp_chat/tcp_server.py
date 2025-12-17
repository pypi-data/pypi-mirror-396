# Andrea Diamantini
# TCP Server

import asyncio
import socket

clientList = []


async def TcpServer(server_port):
    """TCP Chat server, working on every LAN. It can send and receive msgs"""

    loop = asyncio.get_running_loop()

    # Create TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("0.0.0.0", server_port))
    tcp_socket.setblocking(False)

    tcp_socket.listen()
    print(f"TCP server up and listening on port {server_port}...")

    # Listen for incoming connections
    while True:
        conn, addr = await loop.sock_accept(tcp_socket)
        print(f"[INFO] New connection from {addr}")
        clientList.append(conn)
        asyncio.create_task(manageConnection(conn, addr))

    tcp_socket.close()


async def manageConnection(conn, addr):
    """TCP chat server connection management"""

    loop = asyncio.get_running_loop()

    try:
        while True:
            msg = await loop.sock_recv(conn, 1024)
            if not msg:
                break  # close connection

            print(f"msg received: {msg.decode()} from {addr}")

            for connection in clientList:
                if connection != conn:
                    connection.sendall(msg)
                    print(f"sending to {connection.getpeername()}")
    except Exception as e:
        print(f"[ERROR] Connection error with {addr}: {e}")
    finally:
        # remove from list and close
        clientList.remove(conn)
        conn.close()
        print(f"[INFO] {addr} disconnected")


async def runServer(server_port):
    await TcpServer(server_port)


if __name__ == "__main__":
    # server test port
    local_port = 33333

    try:
        # async process execution
        asyncio.run(runServer(local_port))

    # Close on CTRL + C
    except KeyboardInterrupt:
        print("[INFO] Closing Server")
