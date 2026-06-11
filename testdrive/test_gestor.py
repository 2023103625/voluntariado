"""
Testes Unitários para a Gestão Central do Sistema.

Verifica o carregamento de dados (OR02) e a execução das regras 
de negócio principais orquestradas pela classe SistemaVoluntariado.
"""

import unittest
import sys
import os
import types
from typing import Any
import io
from unittest.mock import patch
from typing import Any, List, Optional

# Garante que o Python encontra as pastas do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _instalar_stub_matplotlib() -> None:
    """
    Instala um stub (falso módulo) de matplotlib para ambientes sem dependência.
    """
    if "matplotlib" in sys.modules:
        return
        
    modulo_matplotlib = types.ModuleType("matplotlib")
    modulo_pyplot = types.ModuleType("matplotlib.pyplot")
    modulo_patches = types.ModuleType("matplotlib.patches")
    
    # Simula o objeto Patch usado nas legendas
    class _Patch:
        def __init__(self, *args: Any, **kwargs: Any): pass
    modulo_patches.Patch = _Patch

    class _Axis:
        class _Bar: pass
        
        def bar(self, *args: Any, **kwargs: Any) -> List[Any]: 
            return [self._Bar(), self._Bar()] 
            
        def pie(self, *args: Any, **kwargs: Any) -> None: return None
        def set_title(self, *args: Any, **kwargs: Any) -> None: return None
        def set_xlabel(self, *args: Any, **kwargs: Any) -> None: return None
        def set_ylabel(self, *args: Any, **kwargs: Any) -> None: return None
        def set_xticks(self, *args: Any, **kwargs: Any) -> None: return None
        def set_xticklabels(self, *args: Any, **kwargs: Any) -> None: return None
        def legend(self, *args: Any, **kwargs: Any) -> None: return None
        def add_artist(self, *args: Any, **kwargs: Any) -> None: return None
        def axis(self, *args: Any, **kwargs: Any) -> None: return None
        def grid(self, *args: Any, **kwargs: Any) -> None: return None
        def tick_params(self, *args: Any, **kwargs: Any) -> None: return None 
        
    def _subplots(*args: Any, **kwargs: Any) -> tuple:
        return object(), (_Axis(), _Axis())
        
    modulo_pyplot.subplots = _subplots
    modulo_pyplot.tight_layout = lambda: None
    modulo_pyplot.show = lambda: None
    modulo_pyplot.gca = lambda: _Axis()
    modulo_pyplot.text = lambda *args, **kwargs: object()
    modulo_pyplot.margins = lambda *args, **kwargs: None
    modulo_pyplot.axis = lambda *args, **kwargs: None
    modulo_pyplot.legend = lambda *args, **kwargs: object()
    modulo_pyplot.figure = lambda *args, **kwargs: None
    modulo_pyplot.title = lambda *args, **kwargs: None
    
    modulo_matplotlib.pyplot = modulo_pyplot
    modulo_matplotlib.patches = modulo_patches
    sys.modules["matplotlib"] = modulo_matplotlib
    sys.modules["matplotlib.pyplot"] = modulo_pyplot
    sys.modules["matplotlib.patches"] = modulo_patches

# Instalar o stub antes de importar os módulos que usam matplotlib
_instalar_stub_matplotlib()

from sistema.gestor import SistemaVoluntariado
from sistema.modelos.voluntario import Voluntario
from sistema.modelos.acao import Acao
from sistema.modelos.inscricao import Inscricao


class TestGestor(unittest.TestCase):
    """Testes de carregamento e execução das regras de negócio do Gestor."""

    # ==========================================
    # TESTES DE PERSISTÊNCIA (OR02)
    # ==========================================

    def test_carregar_dados_json_pasta(self) -> None:
        """
        [Propósito]: Garantir que o sistema consegue ler e instanciar os 
        ficheiros JSON da pasta 'dados', populando os dicionários principais.
        """
        # 1. Arrange
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_json = os.path.join(base_dir, "dados", "json")
        sistema = SistemaVoluntariado()

        # 2. Act
        sistema.carregar_sistema(pasta_json)

        # 3. Assert (Valida se o JSON carregou dados reais, caso existam no disco)
        # Nota: Só fará os asserts de > 0 se efetivamente houver dados no JSON.
        if os.path.exists(pasta_json) and len(os.listdir(pasta_json)) > 0:
            self.assertGreater(len(sistema.voluntarios), 0, "Falha ao carregar voluntários.")
            self.assertGreater(len(sistema.entidades), 0, "Falha ao carregar entidades.")
            self.assertGreater(len(sistema.acoes), 0, "Falha ao carregar ações.")
            self.assertGreater(len(sistema.ods_catalogo), 0, "Falha ao carregar catálogo ODS.")
            
            total_pendentes = sum(len(a.fila_inscricoes) for a in sistema.acoes.values())
            total_aprovadas = sum(len(getattr(a, 'inscricoes_aprovadas', [])) for a in sistema.acoes.values())
            self.assertGreaterEqual(total_pendentes + total_aprovadas, 0)

    # ==========================================
    # TESTES DE REGRAS DE NEGÓCIO (RF01 e RF02)
    # ==========================================

    def test_gestor_adicionar_voluntario_gera_id(self) -> None:
        """
        [Propósito]: Verificar se ao adicionar um voluntário, o Gestor gera 
        um ID válido e armazena o objeto no dicionário com a chave em minúsculas (O(1)).
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        voluntario = Voluntario("Rui Silva", "LEI", "FCUP", "estudante", 1)

        # 2. Act
        sistema.adicionar_voluntario(voluntario)

        # 3. Assert
        chave_esperada = "rui silva"
        self.assertIn(chave_esperada, sistema.voluntarios, "Voluntário não foi gravado no dicionário com a chave correta.")
        
        voluntario_guardado = sistema.voluntarios[chave_esperada]
        self.assertIsNotNone(voluntario_guardado.voluntario_id, "O Gestor não gerou o ID do voluntário.")
        self.assertTrue(voluntario_guardado.voluntario_id.startswith("V"), "O ID gerado não começa com 'V'.")

    def test_gestor_processar_inscricao_reduz_vagas(self) -> None:
        """
        [Propósito]: Validar o fluxo FIFO. Quando uma inscrição é aprovada, 
        o estado deve mudar, a ação deve perder 1 vaga e a fila deve diminuir.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        
        acao = Acao("Recolha de Lixo", "ONG Verde", "2025-01-01", 2, 5, "externo")
        sistema.acoes["recolha de lixo"] = acao
        
        inscricao = Inscricao("Rui Silva", "Recolha de Lixo", "2024-12-01")
        acao.fila_inscricoes.enqueue(inscricao)

        vagas_iniciais = acao.vagas

        # 2. Act
        # Aprova a inscrição que está na cabeça da fila
        sistema.processar_inscricao_na_acao("recolha de lixo", aprovada=True)

        # 3. Assert
        self.assertEqual(acao.vagas, vagas_iniciais - 1, "As vagas não foram reduzidas após a aprovação.")
        self.assertTrue(acao.fila_inscricoes.is_empty(), "A inscrição não foi removida (dequeue) da fila pendente.")
        self.assertIn(inscricao, acao.inscricoes_aprovadas, "A inscrição não foi movida para a lista de aprovadas.")
        self.assertEqual(inscricao.estado, "aprovada", "O estado interno da inscrição não foi atualizado.")

    # ==========================================
    # TESTES DE REGRAS DE NEGÓCIO (RF03, 04, 05)
    # ==========================================

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_gestor_pesquisar_acoes_filtros_rf03(self, mock_stdout: io.StringIO) -> None:
        """
        [Propósito]: Validar o RF03. O sistema deve aplicar os filtros de forma 
        estrita e imprimir apenas as ações que cumprem todos os requisitos.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        
        a1 = Acao("Limpeza da Praia", "ONG Mar", "2025-01-01", 2, 10, "externo")
        a1.area = "ambiente"
        
        a2 = Acao("Apoio Escolar", "Escola X", "2025-01-01", 2, 2, "online")
        a2.area = "educação"
        
        sistema.acoes["limpeza da praia"] = a1
        sistema.acoes["apoio escolar"] = a2
        
        filtros = {"area": "ambiente", "vagas_min": 5}
        
        # 2. Act
        sistema.pesquisar_e_listar_acoes(filtros, ordenar_por="vagas")
        
        # 3. Assert (Intercetamos o que a função tentou imprimir no terminal)
        output = mock_stdout.getvalue()
        self.assertIn("Limpeza da Praia", output, "Ação que cumpria os filtros não foi encontrada.")
        self.assertNotIn("Apoio Escolar", output, "Ação que falhava os filtros foi listada indevidamente.")

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_gestor_dashboard_rf04(self, mock_stdout: io.StringIO) -> None:
        """
        [Propósito]: Garantir que o Dashboard V1 (RF04) faz a agregação estatística
        (como contar horas em ações concluídas) e aciona os gráficos sem estourar.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        acao = Acao("Plantar Árvores", "ONG Verde", "2025-01-01", 5, 10, "externo")
        acao.adicionar_ods(13)
        acao.estado = "concluída"  # As horas só contam se a ação estiver concluída
        sistema.acoes["plantar árvores"] = acao
        
        # 2. Act
        sistema.gerar_dashboard()
        
        # 3. Assert
        output = mock_stdout.getvalue()
        self.assertIn("DASHBOARD E ESTATÍSTICAS DO PROGRAMA", output, "O título do dashboard não foi impresso.")
        self.assertIn("ODS 13: 1 ações", output, "A contagem de ações por ODS falhou.")

    def test_gestor_exportar_csv_rf05(self) -> None:
        """
        [Propósito]: Validar o RF05. O sistema deve gerar o diretório 'relatorios',
        escrever o ficheiro CSV formatado corretamente, e converter pontos em vírgulas.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        acao = Acao("Doação Sangue", "Cruz Vermelha", "2025-01-01", 1, 50, "campus")
        acao.metrica_impacto = 99.9  # Testar a conversão da casa decimal
        sistema.acoes["doação sangue"] = acao
        
        pasta_relatorios = "relatorios"
        
        # 2. Act
        sistema.exportar_relatorio_csv()
        
        # 3. Assert
        self.assertTrue(os.path.exists(pasta_relatorios), "A pasta 'relatorios' não foi criada.")
        
        # Procurar o ficheiro CSV (garantindo que pegamos no mais RECENTE gerado pelo teste)
        ficheiros_csv = [f for f in os.listdir(pasta_relatorios) if f.startswith("relatorio_dados_") and f.endswith(".csv")]
        self.assertGreater(len(ficheiros_csv), 0, "O ficheiro CSV não foi gerado.")
        
        ficheiros_csv.sort() # Ordena cronologicamente
        caminho_csv = os.path.join(pasta_relatorios, ficheiros_csv[-1]) # [-1] apanha o último!
        
        with open(caminho_csv, 'r', encoding='utf-8-sig') as f:
            conteudo = f.read()
            
        self.assertIn("Doação Sangue", conteudo, "Os dados não foram exportados.")
        self.assertIn("99,9", conteudo, "A conversão de pontos decimais para formato PT (Excel) falhou.")
        
        # TearDown (Limpeza): Apagar o ficheiro de teste para não poluir o computador
        os.remove(caminho_csv)

    # ==========================================
    # TESTES DE REGRAS DE NEGÓCIO (RF06, 07, 08)
    # ==========================================

    def test_gestor_formacao_equipas_e_undo_rf06(self) -> None:
        """
        [Propósito]: Validar o RF06. Garantir que um voluntário só é adicionado
        se tiver o perfil adequado, e confirmar que a Pilha de Undo reverte a ação.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        
        voluntario = Voluntario("João", "LEI", "FCUP", "estudante", 2)
        voluntario.adicionar_competencia("Python", 4)  # Competência chave
        sistema.voluntarios["joão"] = voluntario

        acao = Acao("Projeto Dev", "Núcleo X", "2025-01-01", 2, 5, "online")
        acao.adicionar_competencia("Python", 3)  # Exige Python
        sistema.acoes["projeto dev"] = acao

        # 2. Act 1: Adicionar à equipa
        sucesso_add, msg_add = sistema.adicionar_voluntario_equipa("projeto dev", "João")

        # 3. Assert 1: A adição funcionou e a Pilha registou?
        self.assertTrue(sucesso_add, "O voluntário compatível foi rejeitado.")
        self.assertIn("João", acao.equipa, "O João não foi parar à equipa.")
        self.assertEqual(acao.historico_equipa.size(), 1, "A Pilha de histórico não registou a alteração.")

        # 2. Act 2: Desfazer a alteração (UNDO)
        sucesso_undo, msg_undo = sistema.desfazer_alteracao_equipa("projeto dev")

        # 3. Assert 2: A equipa voltou ao normal?
        self.assertTrue(sucesso_undo, "O Undo falhou.")
        self.assertNotIn("João", acao.equipa, "O João continuou na equipa após o Undo.")
        self.assertEqual(acao.historico_equipa.size(), 0, "A Pilha não fez o pop() corretamente.")

    def test_gestor_consultar_impacto_bst_rf07(self) -> None:
        """
        [Propósito]: Validar o RF07. Assegurar que o Gestor constrói a BST 
        corretamente e devolve as Ações ordenadas pelo seu impacto.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        
        a1 = Acao("Ação Fraca", "E1", "2025-01-01", 2, 5, "online")
        a1.metrica_impacto = 10.0
        
        a2 = Acao("Ação Forte", "E2", "2025-01-01", 2, 5, "online")
        a2.metrica_impacto = 90.0
        
        a3 = Acao("Ação Média", "E3", "2025-01-01", 2, 5, "online")
        a3.metrica_impacto = 50.0

        sistema.acoes["a1"] = a1
        sistema.acoes["a2"] = a2
        sistema.acoes["a3"] = a3

        # 2. Act
        resultados_decrescentes = sistema.consultar_acoes_por_impacto_ordem(crescente=False)

        # 3. Assert
        self.assertEqual(len(resultados_decrescentes), 3, "Nem todas as ações foram inseridas na BST.")
        self.assertEqual(resultados_decrescentes[0].titulo, "Ação Forte", "O maior impacto não ficou em 1º lugar.")
        self.assertEqual(resultados_decrescentes[-1].titulo, "Ação Fraca", "O menor impacto não ficou no fim.")

    def test_gestor_priorizacao_candidaturas_heap_rf08(self) -> None:
        """
        [Propósito]: Validar o RF08. O Gestor deve calcular os pontos de compatibilidade
        (+2 por ODS, +1 por Competência) e o Max-Heap deve devolver o melhor candidato primeiro.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        
        acao = Acao("Salvar o Planeta", "ONG", "2025-01-01", 2, 5, "externo")
        acao.adicionar_ods(13) # Ação Ação Climática
        sistema.acoes["salvar o planeta"] = acao

        # Voluntário 1: Não tem ODS em comum (Vai ter 0 pontos)
        v1 = Voluntario("Voluntário Fraco", "L", "F", "estudante")
        v1.adicionar_ods_interesse(1) 
        sistema.voluntarios["voluntário fraco"] = v1

        # Voluntário 2: Tem o ODS em comum (Vai ter +2 pontos)
        v2 = Voluntario("Voluntário Forte", "L", "F", "estudante")
        v2.adicionar_ods_interesse(13) 
        sistema.voluntarios["voluntário forte"] = v2

        # Colocamos na Fila de Inscrições
        acao.fila_inscricoes.enqueue(Inscricao("Voluntário Fraco", "Salvar o Planeta", "2024-01-01"))
        acao.fila_inscricoes.enqueue(Inscricao("Voluntário Forte", "Salvar o Planeta", "2024-01-02"))

        # 2. Act
        lista_prioridades = sistema.gerar_candidaturas_ordenadas_heapsort("salvar o planeta")

        # 3. Assert
        self.assertEqual(len(lista_prioridades), 2, "Nem todas as candidaturas foram extraídas do Heap.")
        
        insc_vencedora, pontos = lista_prioridades[0]
        self.assertEqual(insc_vencedora.voluntario, "Voluntário Forte", "O Max-Heap não colocou o voluntário com mais pontos no topo.")
        self.assertGreaterEqual(pontos, 2, "A matemática dos pontos (+2 por ODS) falhou.")

    # ==========================================
    # TESTES DE REGRAS DE NEGÓCIO (RF14, 15, 16)
    # ==========================================

    def test_gestor_rede_entidades_rf14_rf15(self) -> None:
        """
        [Propósito]: Validar RF14 e RF15. O sistema deve reconstruir o grafo
        corretamente, calcular o caminho mais curto entre entidades e determinar
        a centralidade (proximidade) com sucesso.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        
        from sistema.modelos.entidade import Entidade
        from sistema.modelos.acao import Acao
        
        # Criar 3 entidades
        sistema.entidades["e1"] = Entidade("E1", "Núcleo", "Educação", "Campus")
        sistema.entidades["e2"] = Entidade("E2", "Associação", "Ambiente", "Campus")
        sistema.entidades["e3"] = Entidade("E3", "ONG", "Saúde", "Externo")
        
        # Criar ações partilhadas para formar a rede: [E1-E2] e [E2-E3]
        a1 = Acao("Ação 1", ["E1", "E2"], "2025-01-01", 2, 5, "campus")
        a2 = Acao("Ação 2", ["E2", "E3"], "2025-01-02", 2, 5, "campus")
        sistema.acoes["ação 1"] = a1
        sistema.acoes["ação 2"] = a2
        
        # 2. Act (RF14 - Reconstruir Rede)
        sistema.reconstruir_rede_entidades()
        
        # 3. Assert (RF14 - Validar Ligações)
        self.assertIn("e1", sistema.rede_entidades.adjacencias, "O vértice E1 não foi criado no grafo.")
        self.assertIn("e2", sistema.rede_entidades.adjacencias["e1"], "A aresta E1-E2 não foi criada.")
        self.assertIn("e3", sistema.rede_entidades.adjacencias["e2"], "A aresta E2-E3 não foi criada.")
        
        # 4. Act & Assert (RF15 - Caminho Mais Curto)
        # O caminho de E1 a E3 tem de passar obrigatoriamente por E2
        caminho = sistema.pesquisar_caminho_curto_entidades("e1", "e3")
        self.assertEqual(caminho, ["e1", "e2", "e3"], "O caminho mais curto calculado está incorreto.")
        
        # 5. Act & Assert (RF15 - Centralidade de Proximidade)
        centralidades = sistema.calcular_centralidade_rede()
        # E2 está no centro da rede, logo tem a maior centralidade (menor soma de distâncias geodésicas)
        entidade_top, grau = centralidades[0]
        self.assertEqual(entidade_top, "E2", "A entidade E2 deveria ter o maior grau de centralidade.")

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_gestor_visualizacao_rede_rf16(self, mock_stdout: io.StringIO) -> None:
        """
        [Propósito]: Validar RF16. Garantir que a renderização da rede 
        usando NetworkX e Matplotlib não lança exceções (Crash).
        Nota: O plt.show e adjustText não bloqueiam o teste graças ao stub.
        """
        # 1. Arrange
        sistema = SistemaVoluntariado()
        from sistema.modelos.entidade import Entidade
        from sistema.modelos.acao import Acao
        
        # Popular com dados mínimos para não ser uma rede vazia
        sistema.entidades["e1"] = Entidade("E1", "Núcleo", "Educação", "Campus")
        a1 = Acao("Ação 1", ["E1"], "2025-01-01", 2, 5, "campus")
        sistema.acoes["ação 1"] = a1
        
        # 2. Act
        houve_excecao = False
        try:
            sistema.visualizar_rede_parceiros()
        except Exception as e:
            houve_excecao = True
            print(f"Exceção gerada: {e}")
            
        # 3. Assert
        self.assertFalse(houve_excecao, "A visualização gráfica (RF16) falhou com uma exceção.")


if __name__ == '__main__':
    unittest.main()