from typing import Dict, List, Optional
from collections import deque

def caminho_mais_curto_bfs(adjacencias: Dict[str, Dict[str, int]], origem: str, destino: str) -> Optional[List[str]]:
    """
    Algoritmo de Travessia em Largura (BFS) para encontrar o caminho com menos vértices.
    """
    if origem not in adjacencias or destino not in adjacencias:
        return None

    fila = deque([(origem, [origem])])
    visitados = set([origem])

    while fila:
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
    BFS modificado para calcular a soma de todas as distâncias mais curtas 
    a partir de um vértice (necessário para o cálculo de Centralidade - RF15).
    """
    visitados = set([inicio])
    fila = deque([(inicio, 0)]) # (Vértice, Distância da Origem)
    soma = 0

    while fila:
        no_atual, dist_atual = fila.popleft()
        soma += dist_atual

        for vizinho in adjacencias[no_atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append((vizinho, dist_atual + 1))

    return soma