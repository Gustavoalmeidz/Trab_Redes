import socket
import threading
import time
import random
import matplotlib.pyplot as plt

# Configurações
SERVER_ADDRESS_UDP = ('127.0.0.1', 12348)
NUM_MESSAGES = 1000

# Controle de Fluxo e Controle de Congestionamento
CONGESTION_WINDOW_SIZE = 20
THRESHOLD = 15

# Probabilidade reduzida de perda de pacotes
PACKET_LOSS_PROBABILITY = 0.001  # Probabilidade de perda de pacotes: 0.1%

# Variáveis para medição de tempo
udp_modified_times = []

stop_server = threading.Event()
stop_client = threading.Event()

# Servidor UDP Modificado
class FlowControl:
    def __init__(self):
        self.congestion_window = 1
        self.threshold = THRESHOLD
        self.base = 0
        self.next_seq_num = 0
        self.window = []
        self.acks = set()
        self.lock = threading.Lock()

    def handle_ack(self, ack_num):
        with self.lock:
            self.acks.add(ack_num)
            if ack_num == self.base:
                while self.base in self.acks:
                    self.base += 1
                    if self.window:
                        self.window.pop(0)

    def congestion_avoidance(self):
        if self.congestion_window < self.threshold:
            self.congestion_window += 1
        else:
            self.congestion_window += 1 / self.congestion_window

    def packet_loss_detected(self):
        self.threshold = max(self.congestion_window / 2, 1)
        self.congestion_window = 1

def udp_send_with_reliability(sock, addr, messages, flow_control):
    retries = [0] * len(messages)
    while flow_control.base < len(messages) and not stop_client.is_set():
        with flow_control.lock:
            while flow_control.next_seq_num < flow_control.base + flow_control.congestion_window and flow_control.next_seq_num < len(messages):
                msg = f"{flow_control.next_seq_num}:{messages[flow_control.next_seq_num]}"
                flow_control.window.append((flow_control.next_seq_num, msg))
                sock.sendto(msg.encode(), addr)
                flow_control.next_seq_num += 1

        start_time = time.time()
        while time.time() - start_time < 0.1 and not stop_client.is_set():
            with flow_control.lock:
                for seq_num, msg in flow_control.window:
                    if seq_num not in flow_control.acks:
                        if random.random() > PACKET_LOSS_PROBABILITY:
                            sock.sendto(msg.encode(), addr)
                            retries[seq_num] += 1
                            if retries[seq_num] > 3:
                                flow_control.packet_loss_detected()
                                retries[seq_num] = 0

                time.sleep(0.001)

        flow_control.congestion_avoidance()

def udp_modified_client(message_count):
    flow_control = FlowControl()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    messages = [f"{i}:{'Mensagem ' + str(i)}" for i in range(message_count)]
    for _ in range(message_count):
        start_time = time.time()
        udp_send_with_reliability(client_sock, SERVER_ADDRESS_UDP, messages, flow_control)
        client_sock.recvfrom(1024)
        end_time = time.time()
        udp_modified_times.append(end_time - start_time)
    client_sock.close()

# Função principal para UDP Modificado
def run_udp_modified():
    message_count = NUM_MESSAGES

    # Iniciando o servidor UDP em uma thread
    threading.Thread(target=udp_server, daemon=True).start()

    # Espera para garantir que o servidor esteja pronto
    time.sleep(1)

    # Executando o cliente UDP modificado e medindo o tempo
    threading.Thread(target=udp_modified_client, args=(message_count,)).start()

    # Espera para garantir que o cliente termine
    time.sleep
