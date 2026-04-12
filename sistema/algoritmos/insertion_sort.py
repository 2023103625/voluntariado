from typing import List
from sistema.modelos.voluntario import Voluntario

def ordenar_voluntarios_nome(lista: List[Voluntario]) -> None:
    """
    Ordena voluntários por nome (A-Z).
    Melhor caso: O(n). [cite: 57]
    """
    for i in range(1, len(lista)):
        chave = lista[i]
        j = i - 1
        while j >= 0 and lista[j].nome.lower() > chave.nome.lower():
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = chave

        
