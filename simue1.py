from fila import Fila

def simu_encadeadas(filas, numeros):
    def time(time_range, x):
        a, b = time_range
        return a + (b - a) * x
    
    index = 0
    tempo_atual = 0.0
    tempo_anterior = 0.0

    # print("Tempo | Evento   | Fila | Ocupados | Sistema | Ação")
    # print("------|----------|------|----------|---------|---------------")

    # Enquanto não forem usados todos os números e existir algum evento em alguma fila...
    while index < len(numeros) and any(fila.eventos for fila in filas):
        next_event = None
        next_fila_index = -1
        
        for i, fila in enumerate(filas):
            if fila.eventos:
                fila.eventos.sort(key=lambda x: x[1])
                evento = fila.eventos[0]
                if next_event is None or evento[1] < next_event[1]:
                    next_event = evento
                    next_fila_index = i
        
        if next_event is None:
            break
            
        # Pega o próximo evento da fila atual
        fila = filas[next_fila_index]
        tipo, tempo_atual = next_event
        fila.eventos.remove(next_event)
        
        # Atualiza os tempos
        tempo_delta = tempo_atual - tempo_anterior
        if tempo_delta > 0:
            for f in filas:
                clientes_na_fila = min(f.clientes + f.servidores_ocupados, f.capacidade)
                f.tempo_estados[clientes_na_fila] += tempo_delta
        
        tempo_anterior = tempo_atual
        
        acao = ''
        if tipo == 'CHEGADA':
            clientes_na_fila_atual = fila.clientes + fila.servidores_ocupados
            
            if clientes_na_fila_atual < fila.capacidade:
                if fila.servidores_ocupados < fila.servidores:
                    # Servidor livre - atende imediatamente
                    fila.servidores_ocupados += 1
                    if index < len(numeros):
                        tempo_servico = time(fila.interval_servico, numeros[index])
                        index += 1
                        tempo_saida = tempo_atual + tempo_servico
                        fila.eventos.append(('SAIDA', tempo_saida))
                        acao = f'Atendido. Saida em {tempo_saida:.2f}'
                else:
                    # Todos servidores ocupados - vai para fila
                    fila.clientes += 1
                    acao = 'Entrou na fila'
            else:
                # Sistema cheio - cliente perdido
                fila.clientes_perdidos += 1
                acao = 'Cliente perdido (sistema cheio)'
            
            # Agenda chegada pra primeira fila
            if next_fila_index == 0 and index < len(numeros):
                proxima_chegada = tempo_atual + time(fila.interval_chegada, numeros[index])
                index += 1
                fila.eventos.append(('CHEGADA', proxima_chegada))
            
            #print(f'{tempo_atual:5.2f} | CHEGADA | {next_fila_index:4} | {fila.servidores_ocupados:8} | {fila.clientes + fila.servidores_ocupados:7} | {acao}')
        
        elif tipo == 'SAIDA':
            fila.servidores_ocupados -= 1
            fila.clientes_atendidos += 1
            acao = 'Servidor liberado'
            
            # Se for a primeira fila, agenda chegada pras próximas filas
            if next_fila_index == 0 and next_fila_index < len(filas) - 1:
                filas[next_fila_index + 1].eventos.append(('CHEGADA', tempo_atual))
            
            # Se tem clientes na fila, atende
            if fila.clientes > 0:
                fila.clientes -= 1
                fila.servidores_ocupados += 1
                if index < len(numeros):
                    tempo_servico = time(fila.interval_servico, numeros[index])
                    index += 1
                    tempo_saida = tempo_atual + tempo_servico
                    fila.eventos.append(('SAIDA', tempo_saida))
                    acao = f'Atendendo próximo. Saida em {tempo_saida:.2f}'
            
            #print(f'{tempo_atual:5.2f} | SAIDA   | {next_fila_index:4} | {fila.servidores_ocupados:8} | {fila.clientes + fila.servidores_ocupados:7} | {acao}')

    # Pega o total de tmepo
    tempo_total = tempo_atual
    
    def resultados():
        print(f"\n--- RESULTADOS ---")
        print(f"Tempo total de simulação: {tempo_total:.2f} min")
        
        print(f"\nProbabilidades de cada estado por fila:")
        for i, fila in enumerate(filas):
            print(f'--- Fila {i} ---')
            for estado, tempo in enumerate(fila.tempo_estados):
                if tempo_total > 0:
                    probabilidade = (tempo / tempo_total) * 100
                    print(f"  {estado} clientes - {probabilidade:6.2f}%")
        
        print(f"\nTempo em cada estado por fila:")
        for i, fila in enumerate(filas):
            print(f'--- Fila {i} ---')
            for estado, tempo in enumerate(fila.tempo_estados):
                print(f"  {estado} clientes - {tempo:6.2f} min")
        
        print(f"\nMédia populacional por fila:")
        for i, fila in enumerate(filas):
            if tempo_total > 0:
                populacao_media = sum(estado * tempo for estado, tempo in enumerate(fila.tempo_estados)) / tempo_total
                print(f"    Fila {i} - {populacao_media:.2f}")
        
        print(f"\nClientes atendidos por fila:")
        for i, fila in enumerate(filas):
            print(f"    Fila {i} - {fila.clientes_atendidos}")
        
        print(f"\nClientes perdidos por fila:")
        for i, fila in enumerate(filas):
            print(f"    Fila {i} - {fila.clientes_perdidos}")
        
        clientes_atendidos_total = sum(fila.clientes_atendidos for fila in filas)
        clientes_perdidos_total = sum(fila.clientes_perdidos for fila in filas)
        
        print(f"\n--- ESTATÍSTICAS GERAIS ---")
        print(f"Clientes atendidos totais: {clientes_atendidos_total}")
        print(f"Clientes perdidos totais: {clientes_perdidos_total}")
        
        # Média
        if tempo_total > 0:
            populacao_total = 0
            for fila in filas:
                populacao_total += sum(estado * tempo for estado, tempo in enumerate(fila.tempo_estados))
            populacao_media_total = populacao_total / tempo_total
            print(f"População média total do sistema: {populacao_media_total:.2f} clientes")
    
    resultados()

def main():
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
    print("----------------------------------")
    print("Simulação de um sistema de filas!")
    print("----------------------------------")
    print("Insira os parametros da simulação:")
    param = input("Número de filas: ").strip()
    num_filas = int(param)
    filas = []
    for i in range(num_filas):
        print(f'--- Fila {i+1} ---')
        param = input("Intervalo de chegada (min min): ").strip().split()
        intervalo_chegada = [float(param[0]), float(param[1])]
        param = input("Intervalo de serviço (min min): ").strip().split()
        intervalo_servico = [float(param[0]), float(param[1])]
        param = input("Número de servidores: ").strip()
        servidores = int(param)
        param = input("Capacidade da fila: ").strip()
        capacidade = int(param)
        fila = Fila(intervalo_servico, intervalo_chegada, servidores, 0, capacidade)
        filas.append(fila)
    print("----------------------------------")
    print("Por enquanto simulamos apenas filas encadeadas.")
    primeira_chegada = input("Insira o tempo da primeira chegada (min): ").strip()
    primeira_chegada = float(primeira_chegada)
    filas[0].adicionar_evento('CHEGADA', primeira_chegada)
    simu_encadeadas(filas, numeros)

if __name__ == '__main__':
    main()
