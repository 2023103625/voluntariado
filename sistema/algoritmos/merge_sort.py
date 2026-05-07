"""
Módulo de algoritmo de ordenação (Merge Sort).

Implementa a lógica de ordenação por intercalação para organizar
listas de ações de forma decrescente, cumprindo o requisito RF03(ii).
"""

from typing import List, Any


def merge_sort_acoes(lista: List[Any], atributo: str) -> None:
    """
    Ordena uma lista de objetos (ações) in-place usando Merge Sort.

    A ordenação é feita de forma decrescente com base no atributo
    fornecido. O algoritmo divide a lista recursivamente e intercala
    os resultados.

    .. note::
        Complexidade de Tempo:
        - Pior, Médio e Melhor caso: O(n log n).

        Complexidade de Espaço: 
        - O(n) (devido à criação de sublistas auxiliares durante a divisão).

    :param lista: Lista de objetos a ser ordenada.
    :type lista: List[Any]
    :param atributo: Nome do atributo usado como critério de ordenação.
    :type atributo: str
    :return: Nada (a lista original é modificada in-place).
    :rtype: None
    """
    if len(lista) <= 1:
        return

    lista_ordenada: List[Any] = _merge_sort_rec(lista, atributo)
    lista[:] = lista_ordenada


def _merge_sort_rec(lista: List[Any], atributo: str) -> List[Any]:
    """
    Função auxiliar recursiva que divide a lista pela metade.

    :param lista: Sublista a ser dividida e ordenada.
    :type lista: List[Any]
    :param atributo: Nome do atributo usado na ordenação.
    :type atributo: str
    :return: Nova lista ordenada de forma decrescente.
    :rtype: List[Any]
    """
    if len(lista) <= 1:
        return lista[:]

    meio: int = len(lista) // 2
    esquerda: List[Any] = _merge_sort_rec(lista[:meio], atributo)
    direita: List[Any] = _merge_sort_rec(lista[meio:], atributo)

    return _merge(esquerda, direita, atributo)


def _merge(esquerda: List[Any], direita: List[Any], atributo: str) -> List[Any]:
    """
    Intercala (merge) duas sublistas ordenadas numa única lista ordenada.

    A intercalação garante que os maiores valores do atributo aparecem
    primeiro (ordenação decrescente).

    :param esquerda: Sublista ordenada da metade esquerda.
    :type esquerda: List[Any]
    :param direita: Sublista ordenada da metade direita.
    :type direita: List[Any]
    :param atributo: Nome do atributo usado para comparar os objetos.
    :type atributo: str
    :return: Lista combinada e ordenada decrescentemente.
    :rtype: List[Any]
    """
    resultado: List[Any] = []
    i: int = 0
    j: int = 0

    # Compara os elementos das duas sublistas e insere o maior no resultado
    while i < len(esquerda) and j < len(direita):
        if getattr(esquerda[i], atributo) >= getattr(direita[j], atributo):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1

    # Adiciona eventuais elementos restantes da sublista esquerda
    while i < len(esquerda):
        resultado.append(esquerda[i])
        i += 1

    # Adiciona eventuais elementos restantes da sublista direita
    while j < len(direita):
        resultado.append(direita[j])
        j += 1

    return resultado