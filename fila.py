class Fila:
    def __init__(self, interval_servico, interval_chegada, servidores, clientes, capacidade):
        self.interval_servico = interval_servico
        self.interval_chegada = interval_chegada
        self.servidores = servidores
        self.clientes = clientes
        self.capacidade = capacidade
        self.servidores_ocupados = 0
        self.tempo_estados = [0.0] * (capacidade + 1)
        self.clientes_perdidos = 0
        self.clientes_atendidos = 0
        self.eventos = []
        self.prox = None
    
    def adicionar_evento(self, tipo, tempo):
        self.eventos.append((tipo, tempo))

    def proximo_a_sair(self):
        soonest = float('inf')
        for evento in self.eventos:
            tipo, tempo = evento
            if tipo == 'SAIDA' and tempo < soonest:
                soonest = tempo
        return soonest
