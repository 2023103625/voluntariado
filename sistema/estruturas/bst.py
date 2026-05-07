"""
Módulo de estrutura de dados: Árvore Binária de Pesquisa (BST).

Implementa uma árvore binária otimizada para organizar e pesquisar
ações de voluntariado com base na sua métrica de impacto (RF07).
"""

from typing import Any, List, Optional


class NoBST:
    """
    Nó da Árvore Binária de Pesquisa.
    
    Guarda uma chave numérica (impacto) e os respetivos valores associados.
    Em caso de impacto igual, os valores são acumulados na lista interna
    deste nó e ordenados para critério de desempate.

    :param chave: O valor numérico que define a posição na árvore.
    :type chave: float
    :param valor: O objeto inicial (ex: Acao) a guardar neste nó.
    :type valor: Any
    """

    def __init__(self, chave: float, valor: Any) -> None:
        """Inicializa um novo nó da árvore."""
        self.chave: float = chave
        # Usamos uma lista para os valores. Se duas ações tiverem 
        # exatamente a mesma métrica de impacto, ficam no mesmo nó.
        self.valores: List[Any] = [valor]
        self.esquerda: Optional['NoBST'] = None
        self.direita: Optional['NoBST'] = None


class BST:
    """
    Implementação de uma Árvore Binária de Pesquisa (Binary Search Tree).
    """

    def __init__(self) -> None:
        """Inicializa a árvore vazia com raiz nula."""
        self.raiz: Optional[NoBST] = None

    def inserir(self, chave: float, valor: Any) -> None:
        """
        Insere um novo valor na árvore de acordo com a sua chave numérica.

        :param chave: Valor numérico usado para a ordenação (ex: impacto).
        :type chave: float
        :param valor: Objeto a ser armazenado.
        :type valor: Any
        :return: Nada.
        :rtype: None
        """
        if self.raiz is None:
            self.raiz = NoBST(chave, valor)
        else:
            self._inserir_recursivo(self.raiz, chave, valor)

    def _inserir_recursivo(self, no_atual: NoBST, chave: float, valor: Any) -> None:
        """
        Navega recursivamente na árvore para encontrar a posição correta de inserção.

        Se a chave já existir, o valor é adicionado à lista do nó e ordenado
        alfabeticamente para garantir o critério de desempate constante (RF07).

        :param no_atual: O nó atual a ser avaliado na recursão.
        :type no_atual: NoBST
        :param chave: Valor numérico de ordenação.
        :type chave: float
        :param valor: Objeto a ser armazenado.
        :type valor: Any
        :return: Nada.
        :rtype: None
        """
        if chave == no_atual.chave:
            # --- CRITÉRIO DE DESEMPATE (RF07) ---
            no_atual.valores.append(valor)
            # Ordena a lista internamente por ordem alfabética do Título.
            # O getattr tenta ler o 'titulo', caso não exista usa a string do objeto.
            no_atual.valores.sort(key=lambda item: getattr(item, 'titulo', str(item)).lower())
            
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
        """
        Retorna todos os valores armazenados na árvore ordenados de forma crescente.

        Faz uma travessia 'in-order' (esquerda -> raiz -> direita).

        :return: Lista contendo todos os objetos da árvore ordenados pela chave.
        :rtype: List[Any]
        """
        resultados: List[Any] = []
        self._in_order_recursivo(self.raiz, resultados)
        return resultados

    def _in_order_recursivo(self, no_atual: Optional[NoBST], resultados: List[Any]) -> None:
        """
        Percorre a árvore 'in-order' de forma recursiva e acumula os valores.

        :param no_atual: O nó atualmente a ser visitado.
        :type no_atual: Optional[NoBST]
        :param resultados: Lista acumuladora onde os valores são injetados.
        :type resultados: List[Any]
        :return: Nada.
        :rtype: None
        """
        if no_atual is not None:
            self._in_order_recursivo(no_atual.esquerda, resultados)
            
            # Adiciona todos os valores guardados neste nó (já ordenados por desempate)
            resultados.extend(no_atual.valores)
            
            self._in_order_recursivo(no_atual.direita, resultados)