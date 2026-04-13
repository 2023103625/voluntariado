"""Testes automáticos do sistema de voluntariado.

Este módulo valida os principais componentes pedidos na Entrega 1:
- TDA Fila
- modelos de domínio e validações
- algoritmos de ordenação
- carregamento do sistema a partir dos JSON
"""

import os
import sys
import types
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _instalar_stub_matplotlib() -> None:
    """Instala um stub simples de matplotlib para ambientes sem dependência."""
    if "matplotlib" in sys.modules:
        return

    modulo_matplotlib = types.ModuleType("matplotlib")
    modulo_pyplot = types.ModuleType("matplotlib.pyplot")

    class _Axis:
        def bar(self, *args, **kwargs):
            return None

        def set_title(self, *args, **kwargs):
            return None

    def _subplots(*args, **kwargs):
        return object(), (_Axis(), _Axis())

    modulo_pyplot.subplots = _subplots
    modulo_pyplot.tight_layout = lambda: None
    modulo_pyplot.show = lambda: None

    modulo_matplotlib.pyplot = modulo_pyplot
    sys.modules["matplotlib"] = modulo_matplotlib
    sys.modules["matplotlib.pyplot"] = modulo_pyplot


_instalar_stub_matplotlib()

from sistema.algoritmos.insertion_sort import ordenar_voluntarios_nome
from sistema.algoritmos.merge_sort import merge_sort_acoes
from sistema.estruturas.fila import Fila
from sistema.gestor import SistemaVoluntariado
from sistema.modelos.acao import Acao
from sistema.modelos.entidade import Entidade
from sistema.modelos.inscricao import Inscricao
from sistema.modelos.voluntario import Voluntario


class TestFila(unittest.TestCase):
    """Testes do TDA Fila (FIFO)."""

    def test_enqueue_dequeue_fifo(self):
        fila = Fila()
        fila.enqueue("A")
        fila.enqueue("B")
        fila.enqueue("C")

        self.assertEqual(fila.dequeue(), "A")
        self.assertEqual(fila.dequeue(), "B")
        self.assertEqual(fila.dequeue(), "C")
        self.assertIsNone(fila.dequeue())


class TestModelos(unittest.TestCase):
    """Testes de validações e regras dos modelos."""

    def test_voluntario_limites(self):
        voluntario = Voluntario("Ana", "LEI", "FCUP", "estudante", 2)
        for i in range(8):
            self.assertTrue(voluntario.adicionar_competencia(f"c{i}", 3))
        self.assertFalse(voluntario.adicionar_competencia("extra", 4))

        for i in range(6):
            self.assertTrue(voluntario.adicionar_interesse(f"t{i}"))
        self.assertFalse(voluntario.adicionar_interesse("extra"))

        self.assertTrue(voluntario.adicionar_ods_interesse(1))
        self.assertTrue(voluntario.adicionar_ods_interesse(2))
        self.assertTrue(voluntario.adicionar_ods_interesse(3))
        self.assertFalse(voluntario.adicionar_ods_interesse(4))
        self.assertFalse(voluntario.adicionar_ods_interesse(0))

    def test_entidade_limites(self):
        entidade = Entidade("Núcleo X", "núcleo", "educação", "campus")
        for i in range(6):
            self.assertTrue(entidade.adicionar_tag(f"tag{i}"))
        self.assertFalse(entidade.adicionar_tag("extra"))

        self.assertTrue(entidade.adicionar_ods_foco(1))
        self.assertTrue(entidade.adicionar_ods_foco(2))
        self.assertTrue(entidade.adicionar_ods_foco(3))
        self.assertTrue(entidade.adicionar_ods_foco(4))
        self.assertTrue(entidade.adicionar_ods_foco(5))
        self.assertFalse(entidade.adicionar_ods_foco(6))
        self.assertFalse(entidade.adicionar_ods_foco(18))

    def test_acao_validacoes(self):
        acao = Acao("Ação", "Entidade", "2025-01-01 10:00", 2, -5, "online", "educação")
        self.assertEqual(acao.vagas, 0)

        self.assertTrue(acao.adicionar_competencia("comunicação", 3))
        self.assertFalse(acao.adicionar_competencia("nivel_invalido", 8))

        self.assertTrue(acao.adicionar_ods(4))
        self.assertFalse(acao.adicionar_ods(18))

    def test_inscricao_estado(self):
        inscricao = Inscricao("Ana", "Ação 1", "2025-01-01 10:00")
        self.assertEqual(inscricao.estado, "pendente")
        self.assertTrue(inscricao.atualizar_estado("aprovada"))
        self.assertFalse(inscricao.atualizar_estado("estado-invalido"))


class TestAlgoritmos(unittest.TestCase):
    """Testes dos algoritmos de ordenação estudados."""

    def test_insertion_sort_voluntarios_por_nome(self):
        lista = [
            Voluntario("Zeca", "LEI", "FCUP", "estudante"),
            Voluntario("ana", "LEI", "FCUP", "estudante"),
            Voluntario("Bruno", "LEI", "FCUP", "estudante"),
        ]
        ordenar_voluntarios_nome(lista)
        self.assertEqual([v.nome for v in lista], ["ana", "Bruno", "Zeca"])

    def test_merge_sort_acoes_por_impacto_desc(self):
        a1 = Acao("A1", "E", "2025-01-01 10:00", 2, 5, "online")
        a2 = Acao("A2", "E", "2025-01-01 10:00", 2, 5, "online")
        a3 = Acao("A3", "E", "2025-01-01 10:00", 2, 5, "online")
        a1.metrica_impacto = 20
        a2.metrica_impacto = 70
        a3.metrica_impacto = 50
        lista = [a1, a2, a3]

        merge_sort_acoes(lista, "metrica_impacto")
        self.assertEqual([a.titulo for a in lista], ["A2", "A3", "A1"])


class TestCargaSistema(unittest.TestCase):
    """Testes de carregamento dos dados do projeto."""

    def test_carregar_dados_json_pasta(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_json = os.path.join(base_dir, "dados", "json")

        sistema = SistemaVoluntariado()
        sistema.carregar_sistema(pasta_json)

        self.assertGreater(len(sistema.voluntarios), 0)
        self.assertGreater(len(sistema.entidades), 0)
        self.assertGreater(len(sistema.acoes), 0)
        self.assertGreater(len(sistema.ods_catalogo), 0)
        self.assertGreater(len(sistema.inscricoes), 0)
        self.assertGreater(len(sistema.presencas), 0)

        total_pendentes = sum(len(a.fila_inscricoes) for a in sistema.acoes)
        total_aprovadas = sum(len(a.inscricoes_aprovadas) for a in sistema.acoes)
        self.assertGreater(total_pendentes + total_aprovadas, 0)


if __name__ == "__main__":
    unittest.main()