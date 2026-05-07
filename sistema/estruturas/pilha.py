"""
Módulo de estrutura de dados: Pilha (Stack).

Implementa o Tipo de Dados Abstrato Pilha (LIFO - Last-In-First-Out)
usando nós encadeados. Esta estrutura é essencial para gerir o
histórico de operações e permitir a funcionalidade de Undo (RF06).
"""

from typing import Any, List, Optional


class NoPilha:
    """
    Representa um elemento individual (Nó) dentro da Pilha.

    :param valor: O dado a ser armazenado no nó.
    :type valor: Any
    """

    def __init__(self, valor: Any) -> None:
        """Inicializa um novo nó de pilha."""
        self.valor: Any = valor
        self.abaixo: Optional['NoPilha'] = None


class Pilha:
    """
    Implementação dinâmica de uma Pilha (Stack) usando nós ligados.

    O último elemento a entrar é o primeiro a sair (LIFO).
    Ideal para guardar históricos de estado e reverter ações (Undo).
    """

    def __init__(self) -> None:
        """Inicializa uma pilha vazia com o topo nulo e tamanho zero."""
        self._topo: Optional[NoPilha] = None
        self._tamanho: int = 0

    def is_empty(self) -> bool:
        """
        Verifica se a pilha está vazia.

        Complexidade de Tempo: O(1).

        :return: True se não existirem elementos, False caso contrário.
        :rtype: bool
        """
        return self._topo is None

    def size(self) -> int:
        """
        Retorna o número de elementos na pilha.

        Complexidade de Tempo: O(1).

        :return: A quantidade atual de elementos.
        :rtype: int
        """
        return self._tamanho

    def push(self, valor: Any) -> None:
        """
        Adiciona um novo elemento ao topo da pilha.

        Complexidade de Tempo: O(1).

        :param valor: O dado a ser guardado (ex: estado da equipa).
        :type valor: Any
        :return: Nada.
        :rtype: None
        """
        novo_no = NoPilha(valor)
        novo_no.abaixo = self._topo
        self._topo = novo_no
        self._tamanho += 1

    def pop(self) -> Optional[Any]:
        """
        Remove e retorna o elemento que está no topo da pilha.

        Complexidade de Tempo: O(1).

        :return: O valor removido, ou None se a pilha estiver vazia.
        :rtype: Optional[Any]
        """
        if self.is_empty():
            return None

        assert self._topo is not None
        no_removido = self._topo
        self._topo = self._topo.abaixo
        self._tamanho -= 1
        return no_removido.valor

    def peek(self) -> Optional[Any]:
        """
        Observa o elemento do topo sem o remover.

        Complexidade de Tempo: O(1).

        :return: O valor do topo, ou None se a pilha estiver vazia.
        :rtype: Optional[Any]
        """
        if self.is_empty():
            return None
            
        assert self._topo is not None
        return self._topo.valor

    def para_lista(self) -> List[Any]:
        """
        Percorre a pilha do topo para a base e devolve os elementos como lista.

        Ideal para visualização (Dashboard/Histórico) sem remover ou 
        alterar o estado dos itens com o método pop().
        Complexidade de Tempo: O(N).

        :return: Lista com os elementos da pilha (do mais recente para o mais antigo).
        :rtype: List[Any]
        """
        elementos: List[Any] = []
        no_atual = self._topo
        
        while no_atual is not None:
            elementos.append(no_atual.valor)
            no_atual = no_atual.abaixo
            
        return elementos