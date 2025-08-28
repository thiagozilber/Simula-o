def time(time_range, x):
    a, b = time_range
    return a + (b - a) * x

# Parâmetros do LCG
M = 2**31
a_lcg = 1103515245
c = 12345
X0 = 42

def lcg(seed, a, c, m, n):
    valores = []
    X = seed
    for _ in range(n):
        X = (a * X + c) % m
        valores.append(X / m)
    return valores

numeros = lcg(X0, a_lcg, c, M, 100000)

# Stats para o sistema
intervalo_chegada = [2.0, 5.0] # Mudar isso pra não ser hard coded alguma hora :)
intervalo_servico = [3.0, 5.0]
servidores = 2
capacidade = 5
index = 0
tempo_atual = 0.0
tempo_anterior = 0.0
fila = 0  # clientes esperando na fila (não incluindo quem está sendo atendido)
servidores_ocupados = 0
pop_media = 0.0
clientes_atendidos = 0
clientes_perdidos = 0
tempo_estados = [0.0] * (capacidade + 1)  # estados 0 até capacidade
eventos = [('CHEGADA', 2.0)]

print("Tempo | Evento   | Fila | Ocupados | Sistema | Ação")
print("------|----------|------|----------|---------|---------------")

while eventos and index < len(numeros): 
    eventos.sort(key=lambda x: x[1])
    evento = eventos.pop(0)
    tipo, tempo_atual = evento
    
    # Atualizar estatísticas do estado anterior
    tempo_delta = tempo_atual - tempo_anterior
    clientes_no_sistema = fila + servidores_ocupados
    
    if clientes_no_sistema < len(tempo_estados):
        tempo_estados[clientes_no_sistema] += tempo_delta
    else:
        tempo_estados[-1] += tempo_delta
    
    tempo_anterior = tempo_atual
    
    acao = ''
    if tipo == 'CHEGADA':
        clientes_no_sistema_atual = fila + servidores_ocupados
        
        if clientes_no_sistema_atual < capacidade:
            # Cliente pode entrar no sistema
            if servidores_ocupados < servidores:
                # Servidor livre - atende imediatamente
                servidores_ocupados += 1
                tempo_servico = time(intervalo_servico, numeros[index])
                index += 1
                tempo_saida = tempo_atual + tempo_servico
                eventos.append(('SAIDA', tempo_saida))
                acao = f'Atendido. Saida em {tempo_saida:.2f}'
            else:
                # Todos servidores ocupados - vai para fila
                fila += 1
                acao = 'Entrou na fila'
        else:
            # Sistema cheio - cliente perdido
            clientes_perdidos += 1
            acao = 'Cliente perdido (sistema cheio)'
        
        # Agenda próxima chegada
        proxima_chegada = tempo_atual + time(intervalo_chegada, numeros[index])
        index += 1
        eventos.append(('CHEGADA', proxima_chegada))
        
        #print(f'{tempo_atual:5.2f} | CHEGADA | {fila:4} | {servidores_ocupados:8} | {fila + servidores_ocupados:7} | {acao}')
    
    elif tipo == 'SAIDA':
        servidores_ocupados -= 1
        clientes_atendidos += 1
        acao = 'Servidor liberado'
        
        if fila > 0:
            # Tem cliente na fila - atende o próximo
            fila -= 1
            servidores_ocupados += 1
            tempo_servico = time(intervalo_servico, numeros[index])
            index += 1
            tempo_saida = tempo_atual + tempo_servico
            eventos.append(('SAIDA', tempo_saida))
            acao = f'Atendendo próximo. Saida em {tempo_saida:.2f}'
        
        #print(f'{tempo_atual:5.2f} | SAIDA   | {fila:4} | {servidores_ocupados:8} | {fila + servidores_ocupados:7} | {acao}')

# Fim da simulação - atualizar estatísticas finais
tempo_delta_final = tempo_atual - tempo_anterior
clientes_no_sistema_final = fila + servidores_ocupados
if clientes_no_sistema_final < len(tempo_estados):
    tempo_estados[clientes_no_sistema_final] += tempo_delta_final

tempo_total = tempo_atual
prob_vazio = (tempo_estados[0] / tempo_total) * 100
populacao_media = sum(i * tempo for i, tempo in enumerate(tempo_estados)) / tempo_total

print(f"\n--- RESULTADOS ---")
print(f"Tempo total de simulação: {tempo_total:.2f} min")
print(f"Capacidade do sistema: {capacidade} clientes")
print(f"Probabilidades de cada estado:")
for i, tempo in enumerate(tempo_estados):
    probabilidade = (tempo / tempo_total) * 100
    print(f"  {i} clientes - {probabilidade:6.2f}%")
print(f"Tempo em cada estado:")
for i, tempo in enumerate(tempo_estados):
    print(f"  {i} clientes - {tempo:6.2f} min")
print(f"\nPopulação média do sistema: {populacao_media:.2f} clientes")
print(f"Clientes atendidos: {clientes_atendidos}")
print(f"Clientes perdidos: {clientes_perdidos}")