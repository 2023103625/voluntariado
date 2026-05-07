"""
Testes Unitários para os Algoritmos de Ordenação.

Verifica a correção, estabilidade e resiliência dos algoritmos
Insertion Sort (RF03-i), Merge Sort (RF03-ii) e Heap Sort (RF08)
aplicados às entidades de domínio do sistema.
"""

import unittest
import sys
import os
from typing import List, Tuple

# Garante que o Python encontra as pastas do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sistema.algoritmos.insertion_sort import ordenar_voluntarios_nome
from sistema.algoritmos.merge_sort import merge_sort_acoes
from sistema.algoritmos.heap_sort import heap_sort
from sistema.modelos.voluntario import Voluntario
from sistema.modelos.acao import Acao
from sistema.constantes import VinculoVoluntario


class TestAlgoritmos(unittest.TestCase):
    """Testes dos algoritmos de ordenação estudados na UC de AED."""

    # ==========================================
    # TESTES AO INSERTION SORT
    # ==========================================

    def test_insertion_sort_caminho_feliz(self) -> None:
        """
        [Propósito]: Garantir que o Insertion Sort ordena alfabeticamente 
        e ignora diferenças entre maiúsculas e minúsculas (Case-Insensitive).
        """
        # 1. Arrange (Preparar)
        lista = [
            Voluntario("Zeca", "LEI", "FCUP", VinculoVoluntario.ESTUDANTE),
            Voluntario("ana", "LEI", "FCUP", VinculoVoluntario.ESTUDANTE),
            Voluntario("Bruno", "LEI", "FCUP", VinculoVoluntario.ESTUDANTE),
        ]
        
        # 2. Act (Agir)
        ordenar_voluntarios_nome(lista)
        
        # 3. Assert (Validar)
        esperado = ["ana", "Bruno", "Zeca"]
        resultado = [v.nome for v in lista]
        self.assertEqual(resultado, esperado, "A ordenação não ignorou o case (maiúsculas/minúsculas).")

    def test_insertion_sort_lista_vazia_ou_unica(self) -> None:
        """
        [Propósito]: Garantir que o algoritmo não quebra ao receber 
        listas vazias ou com apenas um elemento (Edge Cases).
        """
        # 1. Arrange
        lista_vazia: List[Voluntario] = []
        lista_unica = [Voluntario("Sozinho", "LEI", "FCUP", VinculoVoluntario.ESTUDANTE)]
        
        # 2. Act
        ordenar_voluntarios_nome(lista_vazia)
        ordenar_voluntarios_nome(lista_unica)
        
        # 3. Assert
        self.assertEqual(len(lista_vazia), 0, "A lista vazia foi corrompida.")
        self.assertEqual(lista_unica[0].nome, "Sozinho", "Lista de um elemento foi corrompida.")

    # ==========================================
    # TESTES AO MERGE SORT
    # ==========================================

    def test_merge_sort_acoes_por_impacto_desc(self) -> None:
        """
        [Propósito]: Validar se o Merge Sort ordena corretamente uma 
        lista de ações por ordem DECRESCENTE com base num atributo dinâmico.
        """
        # 1. Arrange
        a1 = Acao("Ação Fraca", "E", "2025-01-01 10:00", 2, 5, "online")
        a2 = Acao("Ação Forte", "E", "2025-01-01 10:00", 2, 5, "online")
        a3 = Acao("Ação Média", "E", "2025-01-01 10:00", 2, 5, "online")
        a1.metrica_impacto = 20.0
        a2.metrica_impacto = 95.5
        a3.metrica_impacto = 50.0
        lista = [a1, a2, a3]

        # 2. Act
        merge_sort_acoes(lista, "metrica_impacto")
        
        # 3. Assert
        esperado = ["Ação Forte", "Ação Média", "Ação Fraca"]
        resultado = [a.titulo for a in lista]
        self.assertEqual(resultado, esperado, "A ordenação decrescente por impacto falhou.")

    def test_merge_sort_lista_vazia(self) -> None:
        """
        [Propósito]: Confirmar a resiliência do Merge Sort a listas vazias (Edge Case).
        """
        # 1. Arrange
        lista_vazia: List[Acao] = []
        
        # 2. Act
        merge_sort_acoes(lista_vazia, "metrica_impacto")
        
        # 3. Assert
        self.assertEqual(len(lista_vazia), 0, "Merge Sort quebrou com lista vazia.")

    # ==========================================
    # TESTES AO HEAP SORT
    # ==========================================

    def test_heap_sort_extracao_prioridade(self) -> None:
        """
        [Propósito]: Assegurar que o Heap Sort constrói o Max-Heap corretamente 
        e extrai os elementos sempre do mais prioritário para o menos prioritário.
        """
        # 1. Arrange
        # Simulamos tuplos (Prioridade, "Nome Candidato") idênticos aos usados no RF08
        elementos: List[Tuple[float, str]] = [
            (2.5, "Voluntario C"),
            (5.0, "Voluntario A"),
            (1.0, "Voluntario D"),
            (3.8, "Voluntario B")
        ]

        # 2. Act
        resultado_ordenado = heap_sort(elementos)

        # 3. Assert
        # A extração do Max-Heap deve ser obrigatoriamente decrescente
        esperado = [
            (5.0, "Voluntario A"),
            (3.8, "Voluntario B"),
            (2.5, "Voluntario C"),
            (1.0, "Voluntario D")
        ]
        self.assertEqual(resultado_ordenado, esperado, "O Heap Sort não extraiu os valores na ordem correta de prioridade.")


if __name__ == '__main__':
    unittest.main()