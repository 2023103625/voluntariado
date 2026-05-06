"""Estrutura de Dados: Pilha (Stack)."""

from typing import Any, Optional


class NoPilha:
    """Representa um elemento individual (Nó) dentro da Pilha."""
    def __init__(self, valor: Any):
        self.valor = valor
        self.abaixo: Optional['NoPilha'] = None


class Pilha:
    """Implementação de uma Pilha (Stack) usando Nós ligados (LIFO).
    
    O último elemento a entrar é o primeiro a sair.
    Ideal para guardar históricos e fazer operações de Undo (Desfazer).
    """

    def __init__(self):
        self._topo: Optional[NoPilha] = None
        self._tamanho: int = 0

    def is_empty(self) -> bool:
        """Verifica se a pilha está vazia."""
        return self._topo is None

    def size(self) -> int:
        """Retorna o número de elementos na pilha."""
        return self._tamanho

    def push(self, valor: Any) -> None:
        """Adiciona um novo elemento ao topo da pilha.
        
        :param valor: O dado a ser guardado (ex: estado da equipa).
        """
        novo_no = NoPilha(valor)
        novo_no.abaixo = self._topo
        self._topo = novo_no
        self._tamanho += 1

    def pop(self) -> Optional[Any]:
        """Remove e retorna o elemento que está no topo da pilha.
        
        :return: O valor removido, ou None se a pilha estiver vazia.
        """
        if self.is_empty():
            return None
        
        no_removido = self._topo
        self._topo = self._topo.abaixo
        self._tamanho -= 1
        return no_removido.valor

    def peek(self) -> Optional[Any]:
        """Observa o elemento do topo sem o remover.
        
        :return: O valor do topo, ou None se a pilha estiver vazia.
        """
        if self.is_empty():
            return None
        return self._topo.valor
    
    def para_lista(self) -> list:
        """Percorre a pilha do topo para a base e devolve os elementos como lista.
        Ideal para visualização (Dashboard/Histórico) sem remover os itens com pop().
        """
        elementos = []
        no_atual = self._topo
        while no_atual is not None:
            elementos.append(no_atual.valor)
            no_atual = no_atual.abaixo
        return elementos