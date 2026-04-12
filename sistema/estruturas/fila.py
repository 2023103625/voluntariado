from typing import List, Any, Optional

class Fila:
    """Implementação do TDA Fila (FIFO)."""
    def __init__(self):
        self.itens: List[Any] = []

    def is_empty(self) -> bool:
        return len(self.itens) == 0

    def enqueue(self, item: Any) -> None:
        self.itens.append(item)

    def dequeue(self) -> Optional[Any]:
        if self.is_empty():
            return None
        return self.itens.pop(0)