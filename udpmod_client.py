import socket
import threading
import time
import random
import logging

# Configurações
SERVER_ADDRESS_UDP = ('127.0.0.1', 12348)
NUM_MESSAGES = 1000
WINDOW_SIZE = 10
TIMEOUT = 0.1  # Timeout inicial de 100ms
MAX_RETRIES = 3  # Número máximo de retransmissões

# Controle de Fluxo e Controle de Congestionamento
CONGESTION_WINDOW_SIZE = 20
THRESHOLD = 15

# Probabilidade reduzida de perda de pacotes
PACKET_LOSS_PROBABILITY = 0.001  # Probabilidade de perda de pacotes: 0.1%

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

stop_client = threading.Event()

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
                logging.info(f"Enviando mensagem: {msg}")
                flow_control.window.append((flow_control.next_seq_num, msg))
                sock.sendto(msg.encode(), addr)
                flow_control.next_seq_num += 1

        start_time = time.time()
        while time.time() - start_time < TIMEOUT and not stop_client.is_set():
            with flow_control.lock:
                for seq_num, msg in flow_control.window:
                    if seq_num not in flow_control.acks:
                        if random.random() > PACKET_LOSS_PROBABILITY:
                            logging.info(f"Reenviando mensagem: {msg}")
                            sock.sendto(msg.encode(), addr)
                            retries[seq_num] += 1
                            if retries[seq_num] > MAX_RETRIES:
                                logging.warning(f"Mensagem {msg} não entregue após {MAX_RETRIES} tentativas.")
                                flow_control.packet_loss_detected()
                                retries[seq_num] = 0

            time.sleep(0.001)  # Sleep para liberar CPU

        flow_control.congestion_avoidance()

    stop_client.set()

def receive_acks(sock, flow_control):
    sock.settimeout(TIMEOUT)
    while not stop_client.is_set():
        try:
            ack, _ = sock.recvfrom(1024)
            ack = int(ack.decode())
            logging.info(f"ACK recebido: {ack}")
            flow_control.handle_ack(ack)
        except socket.timeout:
            continue
        except OSError:
            break

def start_udp_client():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.settimeout(2.0)  # Timeout para recebimento de ACKs

    flow_control = FlowControl()

    threading.Thread(target=receive_acks, args=(client_sock, flow_control), daemon=True).start()

    messages = [f"Mensagem {i}" for i in range(NUM_MESSAGES)]
    udp_send_with_reliability(client_sock, SERVER_ADDRESS_UDP, messages, flow_control)

    client_sock.close()

if __name__ == "__main__":
    stop_client.clear()
    start_udp_client()
