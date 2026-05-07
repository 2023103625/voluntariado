"""
Módulo de estrutura de dados: Fila (Queue).

Implementa o Tipo de Dados Abstrato Fila com base em nós encadeados (Linked List),
garantindo complexidade O(1) para operações de inserção (enqueue) e remoção (dequeue).
Esta estrutura é utilizada para processar as inscrições pendentes nas ações (RF02).
"""

from typing import Any, Optional


class Fila:
    """
    Implementação dinâmica do TDA Fila (FIFO - First-In-First-Out).
    """

    class _No:
        """
        Nó interno da fila ligada.

        :param valor: O dado a ser armazenado no nó.
        :type valor: Any
        """

        def __init__(self, valor: Any) -> None:
            """Inicializa um novo nó de fila."""
            self.valor: Any = valor
            self.proximo: Optional["Fila._No"] = None

    def __init__(self) -> None:
        """
        Inicializa uma fila vazia com apontadores de cabeça, cauda e tamanho zerados.
        """
        self._cabeca: Optional[Fila._No] = None
        self._cauda: Optional[Fila._No] = None
        self._tamanho: int = 0

    def is_empty(self) -> bool:
        """
        Verifica se a fila não contém elementos.

        :return: True se a fila estiver vazia, False caso contrário.
        :rtype: bool
        """
        return self._tamanho == 0

    def enqueue(self, item: Any) -> None:
        """
        Insere um novo elemento no fim da fila (cauda).

        A operação atualiza o apontador da cauda para o novo nó.
        Complexidade de Tempo: O(1).

        :param item: Elemento a ser enfileirado.
        :type item: Any
        :return: Nada.
        :rtype: None
        """
        novo_no = self._No(item)
        if self._cauda is None:
            self._cabeca = novo_no
            self._cauda = novo_no
        else:
            self._cauda.proximo = novo_no
            self._cauda = novo_no
            
        self._tamanho += 1

    def dequeue(self) -> Optional[Any]:
        """
        Remove e devolve o elemento da frente da fila (cabeça).

        A operação avança o apontador da cabeça para o nó seguinte.
        Complexidade de Tempo: O(1).

        :return: O elemento removido, ou None se a fila estiver vazia.
        :rtype: Optional[Any]
        """
        if self.is_empty():
            return None
            
        assert self._cabeca is not None
        valor = self._cabeca.valor
        self._cabeca = self._cabeca.proximo
        
        if self._cabeca is None:
            self._cauda = None
            
        self._tamanho -= 1
        return valor

    def __len__(self) -> int:
        """
        Retorna o número atual de elementos guardados na fila.

        Complexidade de Tempo: O(1).

        :return: A quantidade de elementos.
        :rtype: int
        """
        return self._tamanho