"""
Módulo de estrutura de dados: Fila de Prioridade (Max-Heap).

Implementa uma árvore binária quase completa baseada num array,
garantindo acesso rápido ao elemento de maior prioridade.
Utilizada para o algoritmo de ordenação de candidaturas (RF08).
"""

from typing import Any, List, Optional, Tuple


class MaxHeap:
    """
    Implementação genérica de um Max-Heap.

    Garante que o elemento com maior prioridade numérica está sempre na
    raiz (índice 0). Utiliza um array interno (Lista) para representar a árvore.
    """

    def __init__(self) -> None:
        """Inicializa um Max-Heap vazio."""
        # A lista vai guardar tuplos: (prioridade_numerica, objeto_valor)
        # O float permite lidar com os desempates decimais do Gestor.
        self._heap: List[Tuple[float, Any]] = []

    def is_empty(self) -> bool:
        """
        Verifica se o Heap está vazio.

        Complexidade de Tempo: O(1).

        :return: True se vazio, False caso contrário.
        :rtype: bool
        """
        return len(self._heap) == 0

    def espreitar_max(self) -> Optional[Tuple[float, Any]]:
        """
        Retorna o elemento de maior prioridade (e a sua pontuação) sem o remover.

        Complexidade de Tempo: O(1).

        :return: Tuplo contendo (prioridade, valor) da raiz, ou None se vazio.
        :rtype: Optional[Tuple[float, Any]]
        """
        if self.is_empty():
            return None
        return self._heap[0]

    def inserir(self, prioridade: float, valor: Any) -> None:
        """
        Insere um novo elemento no fim da árvore e reorganiza-a para cima.

        Complexidade de Tempo: O(log n).

        :param prioridade: Valor numérico da prioridade (maior = mais prioritário).
        :type prioridade: float
        :param valor: Objeto a ser armazenado.
        :type valor: Any
        :return: Nada.
        :rtype: None
        """
        self._heap.append((prioridade, valor))
        self._subir(len(self._heap) - 1)

    def extrair_max(self) -> Optional[Any]:
        """
        Remove e retorna o objeto com a maior prioridade (a raiz).

        A árvore é automaticamente reorganizada para manter a propriedade do Max-Heap.
        Complexidade de Tempo: O(log n).

        :return: O objeto que estava no topo, ou None se o Heap estiver vazio.
        :rtype: Optional[Any]
        """
        if self.is_empty():
            return None

        # Se só houver um elemento, retira-o e devolve o valor imediatamente
        if len(self._heap) == 1:
            return self._heap.pop()[1]

        # Guarda o valor máximo (a raiz atual)
        max_valor = self._heap[0][1]

        # Move o último elemento da árvore para a raiz e reorganiza para baixo
        self._heap[0] = self._heap.pop()
        self._descer(0)

        return max_valor

    def _subir(self, indice: int) -> None:
        """
        Navega do fim para a raiz, subindo o nó enquanto a sua prioridade for maior que a do pai.

        :param indice: O índice do nó a ser verificado e movido para cima.
        :type indice: int
        :return: Nada.
        :rtype: None
        """
        indice_pai = (indice - 1) // 2

        if indice > 0 and self._heap[indice][0] > self._heap[indice_pai][0]:
            # Troca o elemento atual com o seu pai
            self._heap[indice], self._heap[indice_pai] = self._heap[indice_pai], self._heap[indice]
            # Chamada recursiva para continuar a verificação para cima
            self._subir(indice_pai)

    def _descer(self, indice: int) -> None:
        """
        Navega da raiz para as folhas, descendo o nó se a sua prioridade for menor que a dos filhos.

        :param indice: O índice do nó a ser verificado e movido para baixo.
        :type indice: int
        :return: Nada.
        :rtype: None
        """
        maior = indice
        filho_esq = 2 * indice + 1
        filho_dir = 2 * indice + 2

        # Verifica se o filho esquerdo existe e se é maior que a raiz atual
        if filho_esq < len(self._heap) and self._heap[filho_esq][0] > self._heap[maior][0]:
            maior = filho_esq

        # Verifica se o filho direito existe e se é maior que o 'maior' encontrado até agora
        if filho_dir < len(self._heap) and self._heap[filho_dir][0] > self._heap[maior][0]:
            maior = filho_dir

        # Se o nó original não for o maior, troca de lugar com o maior filho e continua a descer
        if maior != indice:
            self._heap[indice], self._heap[maior] = self._heap[maior], self._heap[indice]
            self._descer(maior)