import threading
import time
import queue
import random

# Parâmetros da simulação
BUFFER_CAPACITY = 10
NUM_PRODUCERS = 2
NUM_CONSUMERS = 3
NUM_TIMESTEPS = 100

# Buffer (fila limitada)
buffer = queue.Queue(BUFFER_CAPACITY)

# Semáforos
space_available = threading.Semaphore(BUFFER_CAPACITY)  # Espaço disponível para produtores
items_available = threading.Semaphore(0)  # Itens disponíveis para consumidores
buffer_lock = threading.Lock()  # Mutex para sincronizar acesso ao buffer

# Variáveis de relatório e de controle
produced_count = 0
consumed_count = 0
terminate = False  # Variável de controle para encerrar as threads

# Função do produtor
def producer(id):
    global produced_count, terminate
    for _ in range(NUM_TIMESTEPS):
        if terminate:
            break
        # Aguarda espaço disponível no buffer
        space_available.acquire()
        with buffer_lock:
            item = f"Item-{produced_count + 1}"
            buffer.put(item)
            produced_count += 1
            print(f"Produtor {id} produziu: {item}")
        # Sinaliza que um item foi adicionado
        items_available.release()
        time.sleep(random.uniform(0.1, 0.5))  # Simula tempo de produção

    # Sinaliza para encerrar após terminar
    terminate = True

# Função do consumidor
def consumer(id):
    global consumed_count, terminate
    while not terminate or not buffer.empty():
        # Aguarda por itens disponíveis no buffer
        items_available.acquire()
        with buffer_lock:
            if not buffer.empty():
                item = buffer.get()
                consumed_count += 1
                print(f"Consumidor {id} consumiu: {item}")
                # Sinaliza que um espaço foi liberado
                space_available.release()
        time.sleep(random.uniform(0.1, 0.5))  # Simula tempo de consumo

# Criação das threads de produtores e consumidores
producers = [threading.Thread(target=producer, args=(i+1,)) for i in range(NUM_PRODUCERS)]
consumers = [threading.Thread(target=consumer, args=(i+1,)) for i in range(NUM_CONSUMERS)]

# Inicia as threads
for p in producers:
    p.start()
for c in consumers:
    c.start()

# Aguarda o término das threads de produtores
for p in producers:
    p.join()

# Aguardar que todos os consumidores finalizem após o término dos produtores
for c in consumers:
    c.join()

# Exibe o relatório final
print("\n=== Relatório Final ===")
print(f"Total de itens produzidos: {produced_count}")
print(f"Total de itens consumidos: {consumed_count}")
print(f"Status final do buffer: {buffer.qsize()} itens restantes")