import random
import threading
import time
from queue import Queue
import matplotlib.pyplot as plt
import pandas as pd

# Classes básicas
class SolicitaçãoCliente:
    def __init__(self, id_solicitacao, tipo_solicitacao):
        self.id = id_solicitacao
        self.tipo = tipo_solicitacao  # "Técnica" ou "Vendas"

class Atendente:
    def __init__(self, id_atendente, tipo_atendente):
        self.id = id_atendente
        self.tipo = tipo_atendente
        self.ativo = True

    def processar_solicitacao(self, solicitacao):
        if not self.ativo:
            raise Exception("Atendente inativo não pode processar solicitações")
        time.sleep(0.1)  # Simula o tempo de processamento
        return f"Solicitação {solicitacao.id} processada por Atendente {self.id} ({self.tipo})"

class Servidor:
    def __init__(self, id_servidor, capacidade):
        self.id = id_servidor
        self.capacidade = capacidade
        self.atendentes = []
        self.lock = threading.Lock()

    def adicionar_atendente(self, atendente):
        with self.lock:
            self.atendentes.append(atendente)

    def remover_atendente(self, id_atendente):
        with self.lock:
            self.atendentes = [a for a in self.atendentes if a.id != id_atendente]

    def obter_atendentes_ativos(self, tipo_atendente):
        with self.lock:
            return [a for a in self.atendentes if a.tipo == tipo_atendente and a.ativo]

class Supervisor:
    def __init__(self):
        self.servidores = []
        self.logs = []

    def adicionar_servidor(self, servidor):
        self.servidores.append(servidor)

    def monitorar_e_realocar(self, solicitacao, tipo_atendente):
        for servidor in self.servidores:
            atendentes_ativos = servidor.obter_atendentes_ativos(tipo_atendente)
            if atendentes_ativos:
                atendente = random.choice(atendentes_ativos)
                return atendente.processar_solicitacao(solicitacao)
        return f"Solicitação {solicitacao.id} não pôde ser processada devido à falta de atendentes."

class SimuladorFalhas:
    def __init__(self, servidores):
        self.servidores = servidores

    def injetar_falhas(self, probabilidade=0.1):
        for servidor in self.servidores:
            for atendente in servidor.atendentes:
                if random.random() < probabilidade:
                    atendente.ativo = False

class GeradorSolicitacoes:
    def __init__(self):
        self.contador = 0

    def gerar_solicitacoes(self, num_solicitacoes):
        solicitacoes = []
        for _ in range(num_solicitacoes):
            tipo_solicitacao = random.choice(["Técnica", "Vendas"])
            self.contador += 1
            solicitacoes.append(SolicitaçãoCliente(self.contador, tipo_solicitacao))
        return solicitacoes

# Simulação
def simulacao():
    # Configuração inicial
    supervisor = Supervisor()
    gerador_solicitacoes = GeradorSolicitacoes()
    servidores = [
        Servidor("A", 5),
        Servidor("B", 7),
        Servidor("C", 10)
    ]
    for i, servidor in enumerate(servidores):
        # Adiciona atendentes aleatórios a cada servidor
        for _ in range(servidor.capacidade):
            tipo_atendente = random.choice(["Técnica", "Vendas"])
            servidor.adicionar_atendente(Atendente(f"{servidor.id}-{random.randint(100, 999)}", tipo_atendente))
        supervisor.adicionar_servidor(servidor)

    simulador_falhas = SimuladorFalhas(servidores)

    # Logs para análise
    total_solicitacoes = []
    solicitacoes_processadas = 0
    solicitacoes_falhadas = 0

    # Buffer
    buffer = Queue(maxsize=50)

    for timestep in range(100):  # Simulação de 100 timesteps
        print(f"Timestep {timestep + 1}")

        # Geração de novas solicitações
        novas_solicitacoes = gerador_solicitacoes.gerar_solicitacoes(random.randint(10, 20))
        for solicitacao in novas_solicitacoes:
            if not buffer.full():
                buffer.put(solicitacao)
            else:
                print("Overflow do buffer! Terminando simulação.")
                solicitacoes_falhadas += buffer.qsize()
                return solicitacoes_processadas, solicitacoes_falhadas

        # Simulação de falhas
        simulador_falhas.injetar_falhas()

        # Processamento das solicitações no buffer
        tamanho_buffer_atual = buffer.qsize()
        for _ in range(tamanho_buffer_atual):
            solicitacao = buffer.get()
            resultado = supervisor.monitorar_e_realocar(solicitacao, solicitacao.tipo)
            if "não pôde ser processada" in resultado:
                solicitacoes_falhadas += 1
            else:
                solicitacoes_processadas += 1
                print(resultado)

        # Log do timestep
        total_solicitacoes.append({
            "Timestep": timestep + 1,
            "Solicitações Processadas": solicitacoes_processadas,
            "Solicitações Falhadas": solicitacoes_falhadas,
            "Tamanho do Buffer": buffer.qsize()
        })

    # Retorno dos logs
    return total_solicitacoes

# Execução da simulação
logs = simulacao()

# Análise de resultados
df = pd.DataFrame(logs)
print(df)

# Gráficos
plt.figure(figsize=(10, 6))
plt.plot(df["Timestep"], df["Solicitações Processadas"], label="Solicitações Processadas", color="green")
plt.plot(df["Timestep"], df["Solicitações Falhadas"], label="Solicitações Falhadas", color="red")
plt.xlabel("Timestep")
plt.ylabel("Número de Solicitações")
plt.title("Desempenho do Sistema ao Longo do Tempo")
plt.legend()
plt.grid()
plt.show()
