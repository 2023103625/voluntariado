"""
Módulo de algoritmo de ordenação (Insertion Sort).

Implementa a lógica de ordenação por inserção para organizar
listas de voluntários alfabeticamente, cumprindo o requisito RF03(i).
"""

from typing import List
from sistema.modelos.voluntario import Voluntario


def ordenar_voluntarios_nome(lista: List[Voluntario]) -> None:
    """
    Ordena uma lista de voluntários alfabeticamente pelo atributo nome.

    A ordenação é feita in-place (modifica a lista original) usando o 
    algoritmo Insertion Sort. A comparação ignora o caso (maiúsculas/minúsculas)
    para garantir uma ordem alfabética natural.

    .. note::
        Complexidade de Tempo:
        - Melhor caso: O(n) (lista já ordenada).
        - Pior/Médio caso: O(n^2) (lista inversamente ordenada ou aleatória).
        
        Complexidade de Espaço: O(1).

    :param lista: Lista de objetos Voluntario a ser ordenada.
    :type lista: List[Voluntario]
    :return: Nada (a lista é modificada in-place).
    :rtype: None
    """
    for i in range(1, len(lista)):
        chave: Voluntario = lista[i]
        j: int = i - 1
        
        # Desloca os elementos que são alfabeticamente maiores que a chave
        while j >= 0 and lista[j].nome.lower() > chave.nome.lower():
            lista[j + 1] = lista[j]
            j -= 1
            
        lista[j + 1] = chave