import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    print("Servidor esperando conexões...")
    conn, addr = server_socket.accept()
    print(f"Conectado a {addr}")

    for _ in range(1000):
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
