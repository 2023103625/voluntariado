from typing import List
from sistema.modelos.voluntario import Voluntario

def ordenar_voluntarios_nome(lista: List[Voluntario]) -> None:
    """Ordena voluntários alfabeticamente pelo atributo ``nome``.

    Implementação do algoritmo Insertion Sort, conforme RF03(i).

    :param lista: Lista de objetos :class:`Voluntario` a ordenar in-place.
    :return: ``None``.

    .. note::
        Complexidade:
        - melhor caso: ``O(n)`` (lista já ordenada);
        - pior caso: ``O(n^2)``.
    """
    for i in range(1, len(lista)):
        chave = lista[i]
        j = i - 1
        while j >= 0 and lista[j].nome.lower() > chave.nome.lower():
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = chave