"""
Testes Unitários para os Tipos de Dados Abstratos (TDAs).

Verifica a integridade, ordem e limites das estruturas de dados personalizadas:
- Fila (FIFO)
- Pilha (LIFO)
- Árvore Binária de Pesquisa (BST)
- Fila de Prioridade (Max-Heap)
"""

import unittest
import sys
import os

# Garante que o Python encontra as pastas do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sistema.estruturas.fila import Fila
from sistema.estruturas.pilha import Pilha
from sistema.estruturas.bst import BST
from sistema.estruturas.heap import MaxHeap


class TestEstruturas(unittest.TestCase):
    """Testes exaustivos das Estruturas de Dados do sistema."""

    # ==========================================
    # TESTES DA FILA (QUEUE)
    # ==========================================

    def test_fila_mantem_ordem_fifo_e_tamanho(self) -> None:
        """
        [Propósito]: Garantir que o primeiro a entrar é o primeiro a sair (FIFO),
        validar o controlo de tamanho e a resiliência ao tentar extrair de uma fila vazia.
        """
        # 1. Arrange
        fila = Fila()
        
        # 2. Act
        fila.enqueue("A")
        fila.enqueue("B")
        
        # 3. Assert (Tamanho e Remoção FIFO)
        self.assertEqual(len(fila), 2, "Tamanho da fila incorreto após inserções.")
        self.assertEqual(fila.dequeue(), "A", "O elemento mais antigo não foi o primeiro a sair.")
        self.assertEqual(fila.dequeue(), "B", "A ordem do segundo elemento falhou.")
        
        # 3. Assert (Edge Case: Fila Vazia)
        self.assertTrue(fila.is_empty(), "Fila não reporta estar vazia após extração total.")
        self.assertIsNone(fila.dequeue(), "Fila deve devolver None quando vazia.")

    # ==========================================
    # TESTES DA PILHA (STACK)
    # ==========================================

    def test_pilha_mantem_ordem_lifo_e_historico(self) -> None:
        """
        [Propósito]: Garantir o conceito LIFO, testar o 'peek' sem remover
        e validar a conversão para lista para uso no histórico de Undo.
        """
        # 1. Arrange
        pilha = Pilha()
        
        # 2. Act
        pilha.push("Estado 1")
        pilha.push("Estado 2")
        
        # 3. Assert (Verificação sem remover e Conversão)
        self.assertEqual(pilha.peek(), "Estado 2", "O peek não devolveu o topo corretamente.")
        self.assertEqual(pilha.para_lista(), ["Estado 2", "Estado 1"], "A conversão para lista não manteve a ordem LIFO.")
        
        # 3. Assert (Remoção LIFO e Edge Case)
        self.assertEqual(pilha.pop(), "Estado 2", "O último a entrar não foi o primeiro a sair.")
        self.assertEqual(pilha.pop(), "Estado 1")
        self.assertTrue(pilha.is_empty(), "Pilha não está vazia após os pops.")
        self.assertIsNone(pilha.pop(), "Pilha deve devolver None ao fazer pop vazio.")

    # ==========================================
    # TESTES DA ÁRVORE BINÁRIA DE PESQUISA (BST)
    # ==========================================

    def test_bst_insercao_ordem_e_desempate(self) -> None:
        """
        [Propósito]: Testar a travessia in-order e, criticamente, validar
        se o critério de desempate (mesmo impacto = ordem alfabética) funciona.
        """
        # 1. Arrange
        arvore = BST()
        
        # 2. Act
        arvore.inserir(50.0, "Ação Média")
        arvore.inserir(80.0, "Ação Alta")
        arvore.inserir(20.0, "Ação Baixa")
        
        # Inserir outra ação com exatamente o mesmo impacto (50.0) para testar desempate
        arvore.inserir(50.0, "Ação Alfa") 
        
        # 3. Assert
        ordenado = arvore.listar_em_ordem()
        
        # "Ação Alfa" deve aparecer antes de "Ação Média" devido à ordenação interna do nó!
        esperado = ["Ação Baixa", "Ação Alfa", "Ação Média", "Ação Alta"]
        self.assertEqual(ordenado, esperado, "A BST não aplicou corretamente o critério de desempate alfabético.")

    # ==========================================
    # TESTES DA FILA DE PRIORIDADE (MAX-HEAP)
    # ==========================================

    def test_max_heap_ordena_com_decimais(self) -> None:
        """
        [Propósito]: Validar se o Max-Heap reorganiza a árvore corretamente
        suportando valores float (para simular a matemática de compatibilidade).
        """
        # 1. Arrange
        heap = MaxHeap()
        
        # 2. Act
        heap.inserir(3.5, "Voluntário C")
        heap.inserir(5.1, "Voluntário B")
        heap.inserir(1.0, "Voluntário D")
        heap.inserir(5.9, "Voluntário A")
        
        # 3. Assert (Peek e Extração Máxima)
        # O Peek devolve o tuplo inteiro (Prioridade, Valor)
        self.assertEqual(heap.espreitar_max()[1], "Voluntário A", "O Peek falhou em ler o topo.")
        
        # O Extrair devolve apenas o objeto
        self.assertEqual(heap.extrair_max(), "Voluntário A")
        self.assertEqual(heap.extrair_max(), "Voluntário B")
        self.assertEqual(heap.extrair_max(), "Voluntário C")
        self.assertEqual(heap.extrair_max(), "Voluntário D")
        self.assertIsNone(heap.extrair_max(), "Extrair de heap vazio não devolveu None.")


if __name__ == '__main__':
    unittest.main()