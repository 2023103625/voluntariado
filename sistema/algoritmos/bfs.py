from typing import Dict, List, Optional
from collections import deque

def caminho_mais_curto_bfs(adjacencias: Dict[str, Dict[str, int]], origem: str, destino: str) -> Optional[List[str]]:
    """
    Algoritmo de Travessia em Largura (BFS) para encontrar o caminho com menos vértices
    (menor número de saltos) entre duas entidades num grafo não direcionado.

    :param adjacencias: O dicionário que representa as listas de adjacências do grafo.
    :type adjacencias: Dict[str, Dict[str, int]]
    :param origem: O identificador da entidade de partida.
    :type origem: str
    :param destino: O identificador da entidade de chegada.
    :type destino: str
    :return: Uma lista com a sequência de vértices do caminho mais curto, ou None se não houver caminho.
    :rtype: Optional[List[str]]
    """
    if origem not in adjacencias or destino not in adjacencias:
        return None

    # A fila armazena tuplos contendo o vértice atual e o caminho percorrido até ele
    fila = deque([(origem, [origem])])
    
    visitados = set([origem])

    while fila:
        # Retira o primeiro elemento da fila 
        no_atual, caminho = fila.popleft()

        if no_atual == destino:
            return caminho

        for vizinho in adjacencias[no_atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append((vizinho, caminho + [vizinho]))

    return None

def soma_distancias_geodesicas_bfs(adjacencias: Dict[str, Dict[str, int]], inicio: str) -> int:
    """
    BFS modificado para calcular a soma de todas as distâncias mais curtas (em saltos)
    a partir de um vértice central para todos os outros vértices alcançáveis.
    
    Este cálculo é frequentemente necessário para métricas de Centralidade de Proximidade 
    (Closeness Centrality).

    :param adjacencias: O dicionário que representa as listas de adjacências do grafo.
    :type adjacencias: Dict[str, Dict[str, int]]
    :param inicio: O identificador do vértice de partida.
    :type inicio: str
    :return: A soma total do número de saltos (distância) até todos os nós alcançáveis.
    :rtype: int
    """
    # Controla os nós já processados para evitar ciclos
    visitados = set([inicio])
    
    # A fila armazena tuplos: (Vértice, Distância em saltos a partir da Origem)
    fila = deque([(inicio, 0)]) 
    soma = 0

    while fila:   
        no_atual, dist_atual = fila.popleft()
        
        soma += dist_atual
        # Expande a fronteira de pesquisa para a camada seguinte de vizinhos
        for vizinho in adjacencias[no_atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                # Cada novo vizinho descoberto está a uma distância de +1 salto em relação ao nó atual
                fila.append((vizinho, dist_atual + 1))

    return soma