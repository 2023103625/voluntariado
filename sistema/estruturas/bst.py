"""Estrutura de Dados: Árvore Binária de Pesquisa (Binary Search Tree)."""

from typing import Any, List, Optional


class NoBST:
    """Nó da Árvore Binária de Pesquisa.
    
    Guarda uma chave (ex: impacto) e os respetivos valores (ex: ações).
    """
    def __init__(self, chave: float, valor: Any):
        self.chave = chave
        # Usamos uma lista para os valores. Assim, se duas ações tiverem 
        # exatamente a mesma métrica de impacto, ficam guardadas no mesmo nó!
        self.valores: List[Any] = [valor]
        self.esquerda: Optional['NoBST'] = None
        self.direita: Optional['NoBST'] = None


class BST:
    """Implementação de uma Árvore Binária de Pesquisa."""

    def __init__(self):
        self.raiz: Optional[NoBST] = None

    def inserir(self, chave: float, valor: Any) -> None:
        """Insere um novo valor na árvore de acordo com a sua chave."""
        if self.raiz is None:
            self.raiz = NoBST(chave, valor)
        else:
            self._inserir_recursivo(self.raiz, chave, valor)

    def _inserir_recursivo(self, no_atual: NoBST, chave: float, valor: Any) -> None:
        if chave == no_atual.chave:
            # Desempate: Se o impacto for igual, adicionamos a ação à lista deste nó
            no_atual.valores.append(valor)
        elif chave < no_atual.chave:
            if no_atual.esquerda is None:
                no_atual.esquerda = NoBST(chave, valor)
            else:
                self._inserir_recursivo(no_atual.esquerda, chave, valor)
        else:
            if no_atual.direita is None:
                no_atual.direita = NoBST(chave, valor)
            else:
                self._inserir_recursivo(no_atual.direita, chave, valor)

    def listar_em_ordem(self) -> List[Any]:
        """Retorna todos os valores ordenados de forma crescente."""
        resultados = []
        self._in_order_recursivo(self.raiz, resultados)
        return resultados

    def _in_order_recursivo(self, no_atual: Optional[NoBST], resultados: List[Any]) -> None:
        if no_atual is not None:
            self._in_order_recursivo(no_atual.esquerda, resultados)
            # Adiciona todos os valores (ações) guardados neste nó
            resultados.extend(no_atual.valores)
            self._in_order_recursivo(no_atual.direita, resultados)