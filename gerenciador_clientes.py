import random
import threading
import time
from queue import Queue
import matplotlib.pyplot as plt
import pandas as pd

# Classes básicas
class ClientRequest:
    def _init_(self, request_id, request_type):
        self.id = request_id
        self.type = request_type  # "Technical" or "Sales"

class Attendant:
    def _init_(self, attendant_id, attendant_type):
        self.id = attendant_id
        self.type = attendant_type
        self.active = True

    def process_request(self, request):
        if not self.active:
            raise Exception("Inactive attendant cannot process requests")
        time.sleep(0.1)  # Simulate processing time
        return f"Request {request.id} processed by {self.type} Attendant {self.id}"

class Server:
    def _init_(self, server_id, capacity):
        self.id = server_id
        self.capacity = capacity
        self.attendants = []
        self.lock = threading.Lock()

    def add_attendant(self, attendant):
        with self.lock:
            self.attendants.append(attendant)

    def remove_attendant(self, attendant_id):
        with self.lock:
            self.attendants = [a for a in self.attendants if a.id != attendant_id]

    def get_active_attendants(self, attendant_type):
        with self.lock:
            return [a for a in self.attendants if a.type == attendant_type and a.active]

class Supervisor:
    def _init_(self):
        self.servers = []
        self.logs = []

    def add_server(self, server):
        self.servers.append(server)

    def monitor_and_reallocate(self, request, attendant_type):
        for server in self.servers:
            active_attendants = server.get_active_attendants(attendant_type)
            if active_attendants:
                attendant = random.choice(active_attendants)
                return attendant.process_request(request)
        return f"Request {request.id} could not be processed due to lack of attendants."

class FailureSimulator:
    def _init_(self, servers):
        self.servers = servers

    def inject_failures(self, probability=0.1):
        for server in self.servers:
            for attendant in server.attendants:
                if random.random() < probability:
                    attendant.active = False

class RequestGenerator:
    def _init_(self):
        self.counter = 0

    def generate_requests(self, num_requests):
        requests = []
        for _ in range(num_requests):
            request_type = random.choice(["Technical", "Sales"])
            self.counter += 1
            requests.append(ClientRequest(self.counter, request_type))
        return requests

# Simulação
def simulation():
    # Configuração inicial
    supervisor = Supervisor()
    request_generator = RequestGenerator()
    servers = [
        Server("A", 5),
        Server("B", 7),
        Server("C", 10)
    ]
    for i, server in enumerate(servers):
        # Adiciona atendentes aleatórios a cada servidor
        for _ in range(server.capacity):
            attendant_type = random.choice(["Technical", "Sales"])
            server.add_attendant(Attendant(f"{server.id}-{random.randint(100, 999)}", attendant_type))
        supervisor.add_server(server)

    failure_simulator = FailureSimulator(servers)

    # Logs para análise
    total_requests = []
    processed_requests = 0
    failed_requests = 0

    # Buffer
    buffer = Queue(maxsize=50)

    for timestep in range(100):  # Simulação de 100 timesteps
        print(f"Timestep {timestep + 1}")

        # Geração de novas solicitações
        new_requests = request_generator.generate_requests(random.randint(10, 20))
        for request in new_requests:
            if not buffer.full():
                buffer.put(request)
            else:
                print("Buffer overflow! Terminating simulation.")
                failed_requests += buffer.qsize()
                return processed_requests, failed_requests

        # Simulação de falhas
        failure_simulator.inject_failures()

        # Processamento das solicitações no buffer
        current_buffer_size = buffer.qsize()
        for _ in range(current_buffer_size):
            request = buffer.get()
            result = supervisor.monitor_and_reallocate(request, request.type)
            if "could not be processed" in result:
                failed_requests += 1
            else:
                processed_requests += 1
                print(result)

        # Log do timestep
        total_requests.append({
            "Timestep": timestep + 1,
            "Processed Requests": processed_requests,
            "Failed Requests": failed_requests,
            "Buffer Size": buffer.qsize()
        })

    # Retorno dos logs
    return total_requests

# Execução da simulação
logs = simulation()

# Análise de resultados
df = pd.DataFrame(logs)
print(df)

# Gráficos
plt.figure(figsize=(10, 6))
plt.plot(df["Timestep"], df["Processed Requests"], label="Processed Requests", color="green")
plt.plot(df["Timestep"], df["Failed Requests"], label="Failed Requests", color="red")
plt.xlabel("Timestep")
plt.ylabel("Number of Requests")
plt.title("System Performance Over Time")
plt.legend()
plt.grid()
plt.show()