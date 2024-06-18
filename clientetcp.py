import socket
import time
import matplotlib.pyplot as plt

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))

    total_time = 0
    times = []

    for _ in range(1000):
        start = time.time()
        client_socket.sendall(b'Mensagem')
        data = client_socket.recv(1024)
        end = time.time()

        times.append(end - start)
        total_time += (end - start)

    client_socket.close()

    avg_time = total_time / 1000

    # Plotando os gráficos
    plot_times(total_time, avg_time)

    print(f"Tempo total: {total_time} segundos")
    print(f"Tempo médio: {avg_time} segundos")

    return total_time, times

def plot_times(total_time, avg_time):
    plt.figure(figsize=(10, 5))

    # Plotando tempo Medio
    plt.subplot(1, 2, 2)
    plt.bar(['Tempo Medio'], [total_time], color='blue')
    plt.ylabel('Tempo (s)')
    plt.title('Tempo Medio de Comunicação')

    # Plotando tempo Total
    plt.subplot(1, 2, 1)
    plt.bar(['Tempo Total'], [avg_time], color='orange')
    plt.ylabel('Tempo (s)')
    plt.title('Tempo Total de Comunicação')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    start_client()
