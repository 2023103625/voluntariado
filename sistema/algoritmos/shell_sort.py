from typing import List, Any

def shell_sort_acoes(lista: List[Any], atributo: str) -> None:
    """
    Ordena uma lista de objetos in-place usando o algoritmo Shell Sort.
    Complexidade: O(n log n) dependendo da sequência de gaps.
    
    :param lista: A lista de ações a ser ordenada.
    *Método educativo:* O algoritmo divide a lista em sublistas menores
    separadas por um 'gap', ordenando-as com um raciocínio similar ao 
    Insertion Sort, e vai reduzindo o gap até 1.
    
    :param atributo: Nome do atributo pelo qual queremos ordenar 
                     (ex: 'data_hora' ou 'metrica_impacto').
    Nota: A ordenação é feita de forma DECRESCENTE (maior para o menor),
    conforme exigido pelo RF03 (ii).
    """
    n = len(lista)
    gap = n // 2  # Inicializa o intervalo (gap)
    
    while gap > 0:
        for i in range(gap, n):
            # Elemento atual que vamos comparar
            temp = lista[i]
            
            # Obtém o valor do atributo (ex: o valor do impacto do temp)
            valor_temp = getattr(temp, atributo)
            
            j = i
            # Compara com os elementos anteriores no mesmo gap.
            # Como queremos ordem DECRESCENTE, usamos o sinal '<' 
            # (se o valor anterior for menor, recua-o na lista).
            while j >= gap and getattr(lista[j - gap], atributo) < valor_temp:
                lista[j] = lista[j - gap]
                j -= gap
                
            # Coloca o elemento temporário na posição correta
            lista[j] = temp
            
        # Reduz o gap para a próxima iteração
        gap //= 2