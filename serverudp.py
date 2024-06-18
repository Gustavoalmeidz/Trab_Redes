import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 12345))
    print("Servidor esperando mensagens...")

    total_received = 0
    addr = None

    while total_received < 1000:
        data, addr = server_socket.recvfrom(1024)
        if not data:
            break
        total_received += 1
        server_socket.sendto(data, addr)

    server_socket.close()
    return addr

if __name__ == "__main__":
    start_server()
