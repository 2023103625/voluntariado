from typing import Any, Optional

class Fila:
    """Implementação dinâmica do TDA Fila (FIFO) com ``dequeue`` em ``O(1)``."""

    class _No:
        """Nó interno da fila ligada."""

        def __init__(self, valor: Any):
            self.valor = valor
            self.proximo: Optional["Fila._No"] = None

    def __init__(self):
        """Inicializa uma fila vazia."""
        self._cabeca: Optional[Fila._No] = None
        self._cauda: Optional[Fila._No] = None
        self._tamanho: int = 0

    def is_empty(self) -> bool:
        """Indica se a fila está vazia.

        :return: ``True`` se vazia; caso contrário ``False``.
        """
        return self._tamanho == 0

    def enqueue(self, item: Any) -> None:
        """Insere um elemento no fim da fila.

        :param item: Elemento a enfileirar.
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
        """Remove e devolve o elemento da frente da fila.

        :return: Elemento removido ou ``None`` se a fila estiver vazia.
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
        """Retorna o número de elementos na fila."""
        return self._tamanho