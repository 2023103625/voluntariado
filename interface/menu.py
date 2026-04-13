"""Módulo de interface terminal principal.

Este módulo implementa a camada ``interface`` (OR03), expondo menus
terminal-based para os requisitos funcionais da aplicação.
"""

from sistema.gestor import SistemaVoluntariado
from sistema.modelos import Voluntario, Entidade, Acao
from interface.inputs import (
    ler_data_hora_iso_ou_vazio,
    ler_inteiro_intervalo,
    ler_ods_ou_vazio,
    ler_opcao,
    ler_texto_obrigatorio,
)


class MenuTerminal:
    """Interface terminal principal da aplicação."""

    def __init__(self, sistema: SistemaVoluntariado):
        """Inicializa o menu principal.

        :param sistema: Instância de :class:`SistemaVoluntariado`.
        """
        self.sistema = sistema

    def mostrar_menu_principal(self):
        """Mostra o menu principal e processa opções até sair."""
        while True:
            print("\n" + "=" * 50)
            print("   SISTEMA DE VOLUNTARIADO UNIVERSITÁRIO (AED)   ")
            print("=" * 50)
            print("1. Gestão do Programa (CRUD)")
            print("2. Processar Inscrições (Filas)")
            print("3. Pesquisas e Listagens")
            print("4. Dashboard e Estatísticas (Gráficos)")
            print("5. Exportar Relatório TXT (RF05)")
            print("0. Guardar e Sair")
            print("=" * 50)

            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self.menu_gestao_geral()
            elif opcao == "2":
                self.menu_inscricoes()
            elif opcao == "3":
                self.menu_pesquisas()
            elif opcao == "4":
                self.sistema.gerar_dashboard()
            elif opcao == "5":
                self.sistema.exportar_relatorio()
            elif opcao == "0":
                print("\nA guardar os dados e a fechar o sistema. Até logo!")
                break
            else:
                print("Opção inválida.")

    def menu_gestao_geral(self):
        """Mostra submenu de gestão CRUD (RF01)."""
        while True:
            print("\n--- GESTÃO DO PROGRAMA ---")
            print("1. Gerir Voluntários")
            print("2. Gerir Entidades")
            print("3. Gerir Ações")
            print("0. Voltar")
            op = input("Opção: ").strip()

            if op == "1":
                self.menu_crud_voluntarios()
            elif op == "2":
                self.menu_crud_entidades()
            elif op == "3":
                self.menu_crud_acoes()
            elif op == "0":
                break
            else:
                print("Inválido.")

    def _ler_competencias_voluntario(self, voluntario: Voluntario) -> None:
        """Lê competências do voluntário (até 8, nível 1..5)."""
        print("\nCompetências do voluntário (até 8).")
        print("Deixe o nome vazio para terminar.")
        while len(voluntario.competencias) < 8:
            nome = input("Competência: ").strip()
            if not nome:
                break
            if nome in voluntario.competencias:
                print("Competência já adicionada.")
                continue
            nivel = ler_inteiro_intervalo("Nível (1-5): ", 1, 5)
            if voluntario.adicionar_competencia(nome, nivel):
                print("Competência adicionada.")
            else:
                print("Não foi possível adicionar a competência.")

    def _ler_interesses_voluntario(self, voluntario: Voluntario) -> None:
        """Lê tags/interesses do voluntário (até 6)."""
        print("\nInteresses/tags do voluntário (até 6).")
        print("Deixe vazio para terminar.")
        while len(voluntario.interesses) < 6:
            tag = input("Tag de interesse: ").strip()
            if not tag:
                break
            if voluntario.adicionar_interesse(tag):
                print("Tag adicionada.")
            else:
                print("Tag inválida, repetida ou limite atingido.")

    def _ler_ods_voluntario(self, voluntario: Voluntario) -> None:
        """Lê ODS de interesse do voluntário (0..3)."""
        print("\nODS de interesse do voluntário (máx. 3).")
        print("Prima ENTER para terminar.")
        while len(voluntario.ods_interesse) < 3:
            ods = ler_ods_ou_vazio("ODS (1-17): ")
            if ods is None:
                break
            if voluntario.adicionar_ods_interesse(ods):
                print("ODS adicionado.")
            else:
                print("ODS inválido, repetido ou limite atingido.")

    def menu_crud_voluntarios(self):
        """Executa operações CRUD de voluntários."""
        print("\n[VOLUNTÁRIOS] 1:Adicionar | 2:Consultar | 3:Atualizar | 4:Remover | 0:Voltar")
        op = ler_opcao("Escolha: ", ["0", "1", "2", "3", "4"])

        if op == "1":
            nome = ler_texto_obrigatorio("Nome: ")
            curso = ler_texto_obrigatorio("Curso: ")
            faculdade = ler_texto_obrigatorio("Faculdade: ")
            vinculo = ler_opcao(
                "Vínculo (estudante/docente/tecnico): ",
                ["estudante", "docente", "tecnico"],
            ).lower()

            ano = None
            if vinculo == "estudante":
                ano = ler_inteiro_intervalo("Ano do estudante (1-8): ", 1, 8)

            voluntario = Voluntario(nome, curso, faculdade, vinculo, ano)
            self._ler_competencias_voluntario(voluntario)
            self._ler_interesses_voluntario(voluntario)
            self._ler_ods_voluntario(voluntario)
            self.sistema.adicionar_voluntario(voluntario)

        elif op == "2":
            nome = ler_texto_obrigatorio("Nome a consultar: ")
            voluntario = self.sistema.consultar_voluntario(nome)
            if voluntario:
                print(f"Encontrado: {voluntario.nome} - {voluntario.curso}")
                print(f"Competências: {voluntario.competencias}")
                print(f"Tags: {voluntario.interesses}")
                print(f"ODS interesse: {voluntario.ods_interesse}")
            else:
                print("Não encontrado.")

        elif op == "3":
            nome = ler_texto_obrigatorio("Nome a atualizar: ")
            novo_curso = ler_texto_obrigatorio("Novo curso: ")
            self.sistema.atualizar_voluntario(nome, novo_curso)

        elif op == "4":
            nome = ler_texto_obrigatorio("Nome a remover: ")
            self.sistema.remover_voluntario(nome)

    def _ler_tags_entidade(self, entidade: Entidade) -> None:
        """Lê tags da entidade (até 6)."""
        print("\nTags da entidade (até 6).")
        print("Deixe vazio para terminar.")
        while len(entidade.tags) < 6:
            tag = input("Tag: ").strip()
            if not tag:
                break
            if entidade.adicionar_tag(tag):
                print("Tag adicionada.")
            else:
                print("Tag inválida, repetida ou limite atingido.")

    def _ler_ods_entidade(self, entidade: Entidade) -> None:
        """Lê ODS principais da entidade (obrigatório 1..5)."""
        print("\nODS principais da entidade (entre 1 e 5 ODS).")
        while True:
            ods = ler_ods_ou_vazio("ODS (1-17): ")
            if ods is None:
                if len(entidade.ods_foco) >= 1:
                    break
                print("É obrigatório indicar pelo menos 1 ODS.")
                continue
            if entidade.adicionar_ods_foco(ods):
                print("ODS adicionado.")
            else:
                print("ODS inválido, repetido ou limite atingido (máx. 5).")

    def menu_crud_entidades(self):
        """Executa operações CRUD de entidades."""
        print("\n[ENTIDADES] 1:Adicionar | 2:Consultar | 3:Atualizar | 4:Remover | 0:Voltar")
        op = ler_opcao("Escolha: ", ["0", "1", "2", "3", "4"])

        if op == "1":
            nome = ler_texto_obrigatorio("Nome: ")
            tipo = ler_opcao(
                "Tipo (núcleo/associação/serviço/ong parceira): ",
                ["núcleo", "associação", "serviço", "ong parceira"],
            )
            area = ler_texto_obrigatorio("Área de intervenção: ")
            loc = ler_texto_obrigatorio("Localização: ")
            url = input("URL (opcional): ").strip() or None

            entidade = Entidade(nome, tipo, area, loc, url)
            self._ler_tags_entidade(entidade)
            self._ler_ods_entidade(entidade)
            self.sistema.adicionar_entidade(entidade)

        elif op == "2":
            nome = ler_texto_obrigatorio("Nome a consultar: ")
            entidade = self.sistema.consultar_entidade(nome)
            if entidade:
                print(f"Encontrada: {entidade.nome} - {entidade.tipo}")
                print(f"Tags: {entidade.tags}")
                print(f"ODS principais: {entidade.ods_foco}")
            else:
                print("Não encontrada.")

        elif op == "3":
            nome = ler_texto_obrigatorio("Nome da entidade a atualizar: ")
            print("Prima ENTER para manter o valor atual.")
            novo_tipo = input("Novo tipo: ").strip() or None
            nova_area = input("Nova área: ").strip() or None
            nova_localizacao = input("Nova localização: ").strip() or None
            self.sistema.atualizar_entidade(nome, novo_tipo, nova_area, nova_localizacao)

        elif op == "4":
            nome = ler_texto_obrigatorio("Nome a remover: ")
            self.sistema.remover_entidade(nome)

    def _ler_competencias_acao(self, acao: Acao) -> None:
        """Lê competências desejadas da ação (até 6, nível mínimo 1..5)."""
        print("\nCompetências desejadas da ação (até 6).")
        print("Deixe vazio para terminar.")
        while len(acao.competencias_desejadas) < 6:
            nome = input("Competência desejada: ").strip()
            if not nome:
                break
            if nome in acao.competencias_desejadas:
                print("Competência já adicionada.")
                continue
            nivel = ler_inteiro_intervalo("Nível mínimo (1-5): ", 1, 5)
            if acao.adicionar_competencia(nome, nivel):
                print("Competência adicionada.")
            else:
                print("Não foi possível adicionar a competência.")

    def _ler_ods_acao(self, acao: Acao) -> None:
        """Lê ODS da ação (obrigatório 1..3)."""
        print("\nODS associados à ação (obrigatório entre 1 e 3).")
        while True:
            ods = ler_ods_ou_vazio("ODS (1-17): ")
            if ods is None:
                if len(acao.ods_associados) >= 1:
                    break
                print("É obrigatório indicar pelo menos 1 ODS.")
                continue
            if acao.adicionar_ods(ods):
                print("ODS adicionado.")
            else:
                print("ODS inválido, repetido ou limite atingido (máx. 3).")

    def menu_crud_acoes(self):
        """Executa operações CRUD de ações."""
        print("\n[AÇÕES] 1:Adicionar | 2:Consultar | 3:Atualizar Estado | 4:Remover | 0:Voltar")
        op = ler_opcao("Escolha: ", ["0", "1", "2", "3", "4"])

        if op == "1":
            tit = ler_texto_obrigatorio("Título: ")
            ent = ler_texto_obrigatorio("Entidade Promotora: ")
            area = ler_texto_obrigatorio("Área da ação: ")
            data = ler_data_hora_iso_ou_vazio("Data/Hora (YYYY-MM-DD HH:MM): ")
            if not data:
                print("Data/Hora é obrigatória.")
                return

            dur = ler_inteiro_intervalo("Duração (horas): ", 1)
            vag = ler_inteiro_intervalo("Vagas: ", 0)
            loc = ler_opcao(
                "Localização (campus/externo/online): ",
                ["campus", "externo", "online"],
            )
            estado = ler_opcao(
                "Estado (planeada/concluída/cancelada): ",
                ["planeada", "concluída", "cancelada"],
            )
            impacto = ler_inteiro_intervalo("Métrica de impacto (0-100): ", 0, 100)

            acao = Acao(tit, ent, data, dur, vag, loc, area)
            acao.estado = estado
            acao.metrica_impacto = float(impacto)

            self._ler_competencias_acao(acao)
            self._ler_ods_acao(acao)
            self.sistema.adicionar_acao(acao)

        elif op == "2":
            tit = ler_texto_obrigatorio("Título a consultar: ")
            acao = self.sistema.consultar_acao(tit)
            if acao:
                print(
                    f"Encontrada: {acao.titulo} - Estado: {acao.estado} - Vagas: {acao.vagas}"
                )
                print(f"Competências desejadas: {acao.competencias_desejadas}")
                print(f"ODS associados: {acao.ods_associados}")
            else:
                print("Não encontrada.")

        elif op == "3":
            tit = ler_texto_obrigatorio("Título a atualizar: ")
            est = ler_opcao(
                "Novo estado (planeada/concluída/cancelada): ",
                ["planeada", "concluída", "cancelada"],
            )
            self.sistema.atualizar_estado_acao(tit, est)

        elif op == "4":
            tit = ler_texto_obrigatorio("Título a remover: ")
            self.sistema.remover_acao(tit)

    def menu_inscricoes(self):
        """Processa a fila de inscrições de uma ação (RF02)."""
        titulo_acao = ler_texto_obrigatorio("\nTítulo da ação para processar fila: ")
        decisao = ler_opcao("Aprovar (A) ou Rejeitar (R)? ", ["A", "R"]).strip().upper()
        self.sistema.processar_inscricao_na_acao(titulo_acao, decisao == "A")

    def menu_pesquisas(self):
        """Executa pesquisas e listagens (RF03)."""
        print("\n--- PESQUISAS E LISTAGENS ---")
        print("1. Listar Voluntários por Prefixo (O(n) - Insertion Sort)")
        print("2. Pesquisar e Ordenar Ações (O(n log n) - Merge Sort)")
        print("0. Voltar")

        op = ler_opcao("Opção: ", ["0", "1", "2"])

        if op == "1":
            prefixo = ler_texto_obrigatorio("Prefixo do nome: ")
            self.sistema.listar_voluntarios_prefixo(prefixo)

        elif op == "2":
            print("\n--- Filtros de Ação ---")
            print("(Dica: Prima ENTER sem escrever nada para ignorar um filtro)")

            entidade = input("Entidade Promotora: ").strip()
            area = input("Área: ").strip()
            data_inicio = ler_data_hora_iso_ou_vazio("Data início (YYYY-MM-DD HH:MM): ")
            data_fim = ler_data_hora_iso_ou_vazio("Data fim (YYYY-MM-DD HH:MM): ")

            vagas_input = input("Vagas mínimas: ").strip()
            vagas_min = int(vagas_input) if vagas_input.isdigit() else None

            ods = ler_ods_ou_vazio("ODS específico (1-17): ")

            filtros = {
                "entidade": entidade,
                "area": area,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "vagas_min": vagas_min,
                "ods": ods,
            }

            print("\nOrdenar resultados por:")
            print("1. Data e Hora")
            print("2. Métrica de Impacto")
            escolha = ler_opcao("Escolha (1/2): ", ["1", "2"]).strip()

            atributo = "metrica_impacto" if escolha == "2" else "data_hora"
            self.sistema.pesquisar_e_listar_acoes(filtros, ordenar_por=atributo)