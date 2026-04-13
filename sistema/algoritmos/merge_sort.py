"""Algoritmo Merge Sort para ordenação de ações (RF03-ii)."""

from typing import List, Any


def merge_sort_acoes(lista: List[Any], atributo: str) -> None:
    """Ordena lista de ações in-place usando Merge Sort.

    Ordenação por ordem decrescente do atributo.

    :param lista: Lista de objetos/ações.
    :param atributo: Atributo usado na ordenação.
    """
    if len(lista) <= 1:
        return

    lista_ordenada = _merge_sort_rec(lista, atributo)
    lista[:] = lista_ordenada


def _merge_sort_rec(lista: List[Any], atributo: str) -> List[Any]:
    if len(lista) <= 1:
        return lista[:]

    meio = len(lista) // 2
    esquerda = _merge_sort_rec(lista[:meio], atributo)
    direita = _merge_sort_rec(lista[meio:], atributo)
    return _merge(esquerda, direita, atributo)


def _merge(esquerda: List[Any], direita: List[Any], atributo: str) -> List[Any]:
    resultado: List[Any] = []
    i = 0
    j = 0

    while i < len(esquerda) and j < len(direita):
        if getattr(esquerda[i], atributo) >= getattr(direita[j], atributo):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1

    while i < len(esquerda):
        resultado.append(esquerda[i])
        i += 1

    while j < len(direita):
        resultado.append(direita[j])
        j += 1

    return resultado