"""
Módulo de algoritmo de ordenação (Heap Sort).

Implementa a lógica de ordenação baseada na estrutura Max-Heap,
cumprindo o requisito RF08 para a priorização de candidaturas.
"""

from typing import List, Tuple, Any
from sistema.estruturas.heap import MaxHeap


def heap_sort(elementos: List[Tuple[float, Any]]) -> List[Tuple[float, Any]]:
    """
    Ordena uma lista de elementos com base na sua prioridade usando um Max-Heap.

    O algoritmo divide-se em duas fases:
    1. Construção (Build-Heap): Insere todos os elementos na estrutura Max-Heap.
    2. Extração (Extract-Max): Retira repetidamente o elemento de maior prioridade.

    .. note::
        Complexidade de Tempo:
        - Pior, Médio e Melhor caso: O(n log n) (inserção e extração).
        
        Complexidade de Espaço: O(n) (para armazenar o Heap auxiliar).

    :param elementos: Lista de tuplos onde o primeiro valor é a prioridade numérica.
    :type elementos: List[Tuple[float, Any]]
    :return: Nova lista ordenada da maior para a menor prioridade.
    :rtype: List[Tuple[float, Any]]
    """
    heap: MaxHeap = MaxHeap()
    
    # 1. Fase de Construção (Build Heap)
    for prioridade, valor in elementos:
        heap.inserir(prioridade, valor)
        
    # 2. Fase de Extração (Extract Max)
    resultado: List[Tuple[float, Any]] = []
    while not heap.is_empty():
        topo = heap.espreitar_max()
        if topo:
            resultado.append(topo)
        heap.extrair_max()
        
    return resultado