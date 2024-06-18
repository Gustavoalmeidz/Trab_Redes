import socket
import time
import matplotlib.pyplot as plt

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 12345)

    total_time = 0
    times = []

    for _ in range(1000):
        start = time.time()
        client_socket.sendto(b'Mensagem', server_address)
        data, _ = client_socket.recvfrom(1024)
        end = time.time()

        times.append(end - start)
        total_time += (end - start)

    client_socket.close()

    avg_time = total_time / 1000

    return total_time, avg_time

def plot_times(total_time, avg_time):
    plt.figure(figsize=(10, 5))

    # Plotando tempo total
    plt.subplot(1, 2, 1)
    plt.bar(['Tempo Total'], [total_time], color='red')
    plt.ylabel('Tempo (s)')
    plt.title('Tempo Total de Comunicação')

    # Plotando tempo médio
    plt.subplot(1, 2, 2)
    plt.bar(['Tempo Médio'], [avg_time], color='green')
    plt.ylabel('Tempo (s)')
    plt.title('Tempo Médio de Comunicação')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    total_time, avg_time = start_client()

    print(f"Tempo total: {total_time} segundos")
    print(f"Tempo médio: {avg_time} segundos")

    # Plotando os gráficos
    plot_times(total_time, avg_time)
