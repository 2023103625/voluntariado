"""
Testes Unitários para os Modelos de Domínio.

Valida as regras de negócio, restrições de atributos e transições de estado
nas classes principais do sistema (Voluntario, Entidade, Acao, Inscricao).
"""

import unittest
import sys
import os

# Garante que o Python encontra as pastas do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sistema.modelos.acao import Acao
from sistema.modelos.entidade import Entidade
from sistema.modelos.inscricao import Inscricao
from sistema.modelos.voluntario import Voluntario
from sistema.constantes import VinculoVoluntario


class TestModelos(unittest.TestCase):
    """Testes detalhados de validações e regras de negócio dos modelos."""

    # ==========================================
    # TESTES: MODELO VOLUNTÁRIO
    # ==========================================

    def test_voluntario_limites_competencias(self) -> None:
        """
        [Propósito]: Garantir que o voluntário aceita até 8 competências 
        com níveis válidos (1-5), rejeitando níveis fora desse espetro e excessos.
        """
        # 1. Arrange
        voluntario = Voluntario("Ana", "LEI", "FCUP", VinculoVoluntario.ESTUDANTE, 2)
        
        # 2. Act & 3. Assert (Níveis inválidos)
        self.assertFalse(voluntario.adicionar_competencia("Python", 0), "Aceitou nível abaixo de 1.")
        self.assertFalse(voluntario.adicionar_competencia("Java", 6), "Aceitou nível acima de 5.")

        # 2. Act & 3. Assert (Limite máximo)
        for i in range(8):
            sucesso = voluntario.adicionar_competencia(f"Comp_{i}", 3)
            self.assertTrue(sucesso, f"Falhou ao adicionar a competência válida {i}.")
            
        self.assertFalse(voluntario.adicionar_competencia("Extra", 3), "Ultrapassou o limite de 8 competências.")

    def test_voluntario_rejeita_tags_vazias_ou_duplicadas(self) -> None:
        """
        [Propósito]: Testar se a limpeza de strings impede tags vazias 
        e se o Conjunto (Set) impede a adição de interesses repetidos.
        """
        # 1. Arrange
        voluntario = Voluntario("Ana", "LEI", "FCUP", VinculoVoluntario.ESTUDANTE, 2)
        
        # 2. Act
        voluntario.adicionar_interesse("   ")  # Apenas espaços
        voluntario.adicionar_interesse("Ambiente")
        voluntario.adicionar_interesse(" Ambiente ")  # Duplicado com espaços extras
        
        # 3. Assert
        self.assertEqual(len(voluntario.interesses), 1, "Tags vazias ou duplicadas foram aceites incorretamente.")
        self.assertIn("Ambiente", voluntario.interesses)

    def test_voluntario_limites_ods(self) -> None:
        """
        [Propósito]: Validar regras dos ODS de interesse (Máximo 3, IDs entre 1 e 17).
        """
        # 1. Arrange
        voluntario = Voluntario("Ana", "LEI", "FCUP", VinculoVoluntario.ESTUDANTE, 2)
        
        # 2. Act & 3. Assert
        self.assertFalse(voluntario.adicionar_ods_interesse(0), "Aceitou ODS 0.")
        self.assertFalse(voluntario.adicionar_ods_interesse(18), "Aceitou ODS 18.")
        
        self.assertTrue(voluntario.adicionar_ods_interesse(1))
        self.assertTrue(voluntario.adicionar_ods_interesse(2))
        self.assertTrue(voluntario.adicionar_ods_interesse(3))
        self.assertFalse(voluntario.adicionar_ods_interesse(4), "Ultrapassou o limite de 3 ODS.")

    # ==========================================
    # TESTES: MODELO ENTIDADE
    # ==========================================

    def test_entidade_limites_tags_e_ods(self) -> None:
        """
        [Propósito]: Testar o máximo de tags (6) e de ODS foco (5) para uma Entidade.
        """
        # 1. Arrange
        entidade = Entidade("Núcleo X", "núcleo", "educação", "campus")
        
        # 2. Act & 3. Assert (Tags)
        for i in range(6):
            self.assertTrue(entidade.adicionar_tag(f"tag{i}"))
        self.assertFalse(entidade.adicionar_tag("tag_extra"), "Ultrapassou limite de 6 tags.")

        # 2. Act & 3. Assert (ODS)
        for i in range(1, 6):  # ODS de 1 a 5
            self.assertTrue(entidade.adicionar_ods_foco(i))
        self.assertFalse(entidade.adicionar_ods_foco(6), "Ultrapassou limite de 5 ODS.")

    # ==========================================
    # TESTES: MODELO AÇÃO
    # ==========================================

    def test_acao_vagas_nao_negativas(self) -> None:
        """
        [Propósito]: Garantir que a criação de uma ação com vagas negativas 
        é automaticamente corrigida para 0 (limite inferior).
        """
        # 1. Arrange & Act
        acao = Acao("Ação Bugada", "Entidade", "2025-01-01 10:00", 2, -5, "online", "educação")
        
        # 3. Assert
        self.assertEqual(acao.vagas, 0, "O construtor aceitou um número negativo de vagas.")

    def test_acao_limites_competencias_e_ods(self) -> None:
        """
        [Propósito]: Testar os limites de competências desejadas (max 6) e ODS (max 3).
        """
        # 1. Arrange
        acao = Acao("Limpeza", "ONG Verde", "2025-01-01", 2, 10, "externo")
        
        # 2. Act & 3. Assert
        self.assertTrue(acao.adicionar_competencia("comunicação", 3))
        self.assertFalse(acao.adicionar_competencia("nivel_invalido", 8), "Aceitou nível de proficiência acima de 5.")
        
        self.assertTrue(acao.adicionar_ods(4))
        self.assertTrue(acao.adicionar_ods(14))
        self.assertTrue(acao.adicionar_ods(15))
        self.assertFalse(acao.adicionar_ods(16), "Permitiu mais de 3 ODS para uma mesma ação.")

    # ==========================================
    # TESTES: MODELO INSCRIÇÃO
    # ==========================================

    def test_inscricao_atualizacao_estado(self) -> None:
        """
        [Propósito]: Verificar o estado inicial padrão e as transições de estado 
        (com tolerância a maiúsculas/minúsculas).
        """
        # 1. Arrange
        inscricao = Inscricao("Ana", "Ação 1", "2025-01-01 10:00")
        
        # 3. Assert (Estado Inicial)
        self.assertEqual(inscricao.estado, "pendente", "O estado inicial não é 'pendente'.")
        
        # 2. Act (Testar case-insensitivity)
        sucesso_maiusculas = inscricao.atualizar_estado("APROVADA")
        
        # 3. Assert (Sucesso e falha)
        self.assertTrue(sucesso_maiusculas, "Falhou ao atualizar com letras maiúsculas.")
        self.assertEqual(inscricao.estado, "aprovada", "O estado interno não foi gravado em minúsculas.")
        
        self.assertFalse(inscricao.atualizar_estado("estado_inventado"), "Aceitou um estado fora das constantes.")

if __name__ == '__main__':
    unittest.main()