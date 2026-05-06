"""Estrutura de Dados: Fila de Prioridade (Max-Heap)."""

from typing import Any, Tuple, Optional


class MaxHeap:
    """Implementação de um Max-Heap usando um Array (Lista) interno.
    
    Garante que o elemento com maior prioridade está sempre na raiz (índice 0).
    Ideal para ordenar candidaturas (RF08).
    """

    def __init__(self):
        # A lista vai guardar tuplos: (prioridade_numerica, objeto_valor)
        self._heap: List[Tuple[int, Any]] = []

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def inserir(self, prioridade: int, valor: Any) -> None:
        """Insere um novo elemento e reorganiza a árvore para cima (_subir)."""
        self._heap.append((prioridade, valor))
        self._subir(len(self._heap) - 1)

    def extrair_max(self) -> Optional[Any]:
        """Remove e retorna o elemento com maior prioridade."""
        if self.is_empty():
            return None
        
        # Se só houver um elemento, tira-o e devolve
        if len(self._heap) == 1:
            return self._heap.pop()[1]

        # Guarda o valor máximo (a raiz)
        max_valor = self._heap[0][1]
        
        # Move o último elemento para a raiz e reorganiza para baixo (_descer)
        self._heap[0] = self._heap.pop()
        self._descer(0)
        
        return max_valor

    def _subir(self, indice: int) -> None:
        """Move o elemento para cima se a sua prioridade for maior que a do pai."""
        indice_pai = (indice - 1) // 2
        
        if indice > 0 and self._heap[indice][0] > self._heap[indice_pai][0]:
            # Troca o elemento com o pai
            self._heap[indice], self._heap[indice_pai] = self._heap[indice_pai], self._heap[indice]
            self._subir(indice_pai)

    def _descer(self, indice: int) -> None:
        """Move o elemento para baixo se for menor que os seus filhos."""
        maior = indice
        filho_esq = 2 * indice + 1
        filho_dir = 2 * indice + 2

        # Verifica se o filho esquerdo é maior que a raiz atual
        if filho_esq < len(self._heap) and self._heap[filho_esq][0] > self._heap[maior][0]:
            maior = filho_esq

        # Verifica se o filho direito é maior que o maior até agora
        if filho_dir < len(self._heap) and self._heap[filho_dir][0] > self._heap[maior][0]:
            maior = filho_dir

        # Se o maior não for o índice atual, troca e continua a descer
        if maior != indice:
            self._heap[indice], self._heap[maior] = self._heap[maior], self._heap[indice]
            self._descer(maior)