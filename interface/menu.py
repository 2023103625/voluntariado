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

    @staticmethod
    def _imprimir_titulo(titulo: str) -> None:
        """Imprime um título formatado para melhorar a legibilidade no terminal."""
        largura = 62
        print("\n" + "╔" + "═" * largura + "╗")
        print(f"║{titulo.center(largura)}║")
        print("╚" + "═" * largura + "╝")

    @staticmethod
    def _imprimir_opcoes(opcoes: list[str]) -> None:
        """Imprime um bloco de opções numeradas/alinhadas."""
        for opcao in opcoes:
            print(f"  • {opcao}")

    @staticmethod
    def _imprimir_tabela(headers: list[str], rows: list[list[object]]) -> None:
        """Desenha uma tabela em formato texto baseada nas larguras das colunas."""
        if not rows:
            print("(sem dados)")
            return
            
        # Calcula a largura necessária para cada coluna
        larguras = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                larguras[i] = max(larguras[i], len(str(val)))
                
        # Constrói o separador da tabela (ex: +---+-------+)
        linha = "+-" + "-+-".join("-" * l for l in larguras) + "-+"
        print(linha)
        
        # Imprime o cabeçalho
        print("| " + " | ".join(h.ljust(larguras[i]) for i, h in enumerate(headers)) + " |")
        print(linha)
        
        # Imprime os dados linha a linha
        for row in rows:
            print("| " + " | ".join(str(v).ljust(larguras[i]) for i, v in enumerate(row)) + " |")
        print(linha)

    def mostrar_menu_principal(self):
        """Mostra o menu principal e processa opções até sair."""
        while True:
            self._imprimir_titulo("SISTEMA DE VOLUNTARIADO UNIVERSITÁRIO (AED)")
            self._imprimir_opcoes(
                [
                    "1. Gestão do Programa (CRUD)",
                    "2. Processar Inscrições (Filas)",
                    "3. Pesquisas e Listagens",
                    "4. Dashboard e Estatísticas (Gráficos)",
                    "5. Exportar Relatórios (PDF / CSV - RF05)",  
                    "6. Formação de Equipas (RF06)",
                    "7. Consulta de Ações por Impacto (RF07)",
                    "8. Priorizar Candidaturas (Max-Heap - RF08)",
                    "0. Guardar e Sair",
                ]
            )

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
                self.menu_exportar_relatorios()  
            elif opcao == "6":
                self.menu_equipas()
            elif opcao == "7":
                self.menu_impacto()
            elif opcao == "8":
                self.menu_priorizacao()
            elif opcao == "0":
                print("\nA guardar os dados e a fechar o sistema. Até logo!")
                break
            else:
                print("Opção inválida.")
    
    def menu_exportar_relatorios(self):
        """Menu interativo para escolha do formato de exportação (RF05)."""
        self._imprimir_titulo("EXPORTAR RELATÓRIOS (RF05)")
        self._imprimir_opcoes(
            [
                "1. Exportar Resumo Visual (PDF)",
                "2. Exportar Dados Tabulares (CSV Excel)",
                "3. Exportar Ambos (PDF + CSV)",
                "0. Voltar",
            ]
        )
        
        op = ler_opcao("Escolha o formato pretendido: ", ["0", "1", "2", "3"])
        
        if op == "1":
            self.sistema.exportar_relatorio()
        elif op == "2":
            self.sistema.exportar_relatorio_csv()
        elif op == "3":
            self.sistema.exportar_relatorio()
            self.sistema.exportar_relatorio_csv()
        elif op == "0":
            return
            
        input("\nPrima ENTER para continuar.")

    def menu_gestao_geral(self):
        """Mostra submenu de gestão CRUD (RF01)."""
        while True:
            self._imprimir_titulo("GESTÃO DO PROGRAMA")
            self._imprimir_opcoes(
                [
                    "1. Gerir Voluntários",
                    "2. Gerir Entidades",
                    "3. Gerir Ações",
                    "0. Voltar",
                ]
            )
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
        self._imprimir_tabela(
            ["ods_id", "ods_nome"],
            [[o.get("ods_id"), o.get("ods_nome")] for o in self.sistema.ods_catalogo],
        )
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
        self._imprimir_titulo("VOLUNTÁRIOS")
        self._imprimir_opcoes(
            ["1. Adicionar", "2. Consultar", "3. Atualizar", "4. Remover", "0. Voltar"]
        )
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
            termo = input("Nome completo, primeiro/último nome (vazio para todos): ").strip()
            if not termo:
                resultados = self.sistema.voluntarios
            else:
                v_exato = self.sistema.consultar_voluntario(termo)
                resultados = [v_exato] if v_exato else self.sistema.pesquisar_voluntarios(termo)
            
            self._imprimir_tabela(
                ["voluntario_id", "nome", "curso", "faculdade", "vinculo_institucional", "ano"],
                [[getattr(v, "voluntario_id", ""), v.nome, v.curso, v.faculdade, v.vinculo, v.ano or "-"] for v in resultados],
            )

        elif op == "3":
            self._imprimir_tabela(
                ["voluntario_id", "nome", "curso", "faculdade", "vinculo_institucional", "ano"],
                [[getattr(v, "voluntario_id", ""), v.nome, v.curso, v.faculdade, v.vinculo, v.ano or "-"] for v in self.sistema.voluntarios],
            )
            nome = ler_texto_obrigatorio("Nome a atualizar: ")
            voluntario = self.sistema.consultar_voluntario(nome)
            if not voluntario:
                print("Voluntário não encontrado.")
                return
            
            print(f"Atual: {voluntario.__dict__}")
            novos = {}
            novo_nome = input("Nome (ENTER mantém): ").strip()
            if novo_nome: novos["nome"] = novo_nome
            
            novo_curso = input("Curso (ENTER mantém): ").strip()
            if novo_curso: novos["curso"] = novo_curso
            
            nova_faculdade = input("Faculdade (ENTER mantém): ").strip()
            if nova_faculdade: novos["faculdade"] = nova_faculdade
            
            novo_vinculo = input("Vínculo (estudante/docente/tecnico, ENTER mantém): ").strip().lower()
            if novo_vinculo: novos["vinculo"] = novo_vinculo
            
            if (novo_vinculo or voluntario.vinculo) == "estudante":
                ano_txt = input("Ano (1-8, ENTER mantém): ").strip()
                if ano_txt.isdigit(): novos["ano"] = int(ano_txt)
                
            self.sistema.atualizar_voluntario_completo(nome, novos)

        elif op == "4":
            self._imprimir_tabela(
                ["voluntario_id", "nome", "curso", "faculdade", "vinculo_institucional", "ano"],
                [[getattr(v, "voluntario_id", ""), v.nome, v.curso, v.faculdade, v.vinculo, v.ano or "-"] for v in self.sistema.voluntarios],
            )
            nome = ler_texto_obrigatorio("Nome a remover: ")
            voluntario = self.sistema.consultar_voluntario(nome)
            if not voluntario:
                print("Voluntário não encontrado.")
                return
            print(f"A remover: {voluntario.__dict__}")
            if ler_opcao("Confirma remoção? (S/N): ", ["S", "N"]) == "S":
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
        self._imprimir_tabela(
            ["ods_id", "ods_nome"], 
            [[o.get("ods_id"), o.get("ods_nome")] for o in self.sistema.ods_catalogo]
        )
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
        self._imprimir_titulo("ENTIDADES")
        self._imprimir_opcoes(
            ["1. Adicionar", "2. Consultar", "3. Atualizar", "4. Remover", "0. Voltar"]
        )
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
            cabecalhos = ["ID da Entidade", "Nome"]
            dados_lista = [[getattr(e, "entidade_id", ""), e.nome or "-"] for e in self.sistema.entidades]
            
            print("\n--- LISTA DE ENTIDADES PARCEIRAS ---")
            self._imprimir_tabela(cabecalhos, dados_lista)
            
            nome = ler_texto_obrigatorio("\nNome a consultar: ")
            entidade = self.sistema.consultar_entidade(nome)
            
            if entidade:
                print(f"\n--- DETALHES DA ENTIDADE: {entidade.nome.upper()} ---")
                
                cabecalhos_detalhes = ["Campo", "Detalhe"]
                tags_str = ", ".join(entidade.tags) if entidade.tags else "Nenhuma"
                ods_str = ", ".join(str(o) for o in entidade.ods_foco) if entidade.ods_foco else "Nenhum"
                url_str = entidade.url if entidade.url else "Não definido"
                
                dados_detalhes = [
                    ["ID", getattr(entidade, "entidade_id", "Não atribuído")],
                    ["Nome", entidade.nome],
                    ["Tipo", entidade.tipo.capitalize()],
                    ["Área de Intervenção", entidade.area],
                    ["Localização", entidade.localizacao],
                    ["URL Institucional", url_str],
                    ["Tags", tags_str],
                    ["ODS Principais", ods_str]
                ]
                
                self._imprimir_tabela(cabecalhos_detalhes, dados_detalhes)
            else:
                print("\nEntidade não encontrada. Verifique se escreveu o nome corretamente.")

        elif op == "3":
            self._imprimir_tabela(
                ["entidade_id", "nome", "tipo", "area_intervencao", "localizacao", "url"], 
                [[getattr(e, "entidade_id", ""), e.nome, e.tipo, e.area, e.localizacao, e.url or "-"] for e in self.sistema.entidades]
            )
            nome = ler_texto_obrigatorio("Nome da entidade a atualizar: ")
            entidade = self.sistema.consultar_entidade(nome)
            if not entidade:
                print("Entidade não encontrada.")
                return
            
            print(f"Atual: {entidade.__dict__}")
            novos = {}
            for campo, label in [("nome", "Nome"), ("tipo", "Tipo"), ("area", "Área"), ("localizacao", "Localização"), ("url", "URL")]:
                val = input(f"{label} (ENTER mantém): ").strip()
                if val: novos[campo] = val
            self.sistema.atualizar_entidade_completo(nome, novos)

        elif op == "4":
            self._imprimir_tabela(
                ["entidade_id", "nome", "tipo", "area_intervencao", "localizacao", "url"], 
                [[getattr(e, "entidade_id", ""), e.nome, e.tipo, e.area, e.localizacao, e.url or "-"] for e in self.sistema.entidades]
            )
            nome = ler_texto_obrigatorio("Nome a remover: ")
            entidade = self.sistema.consultar_entidade(nome)
            if not entidade:
                print("Entidade não encontrada.")
                return
            print(f"A remover: {entidade.__dict__}")
            if ler_opcao("Confirma remoção? (S/N): ", ["S", "N"]) == "S":
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
        self._imprimir_tabela(
            ["ods_id", "ods_nome"], 
            [[o.get("ods_id"), o.get("ods_nome")] for o in self.sistema.ods_catalogo]
        )
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
        self._imprimir_titulo("AÇÕES")
        self._imprimir_opcoes(
            ["1. Adicionar", "2. Consultar", "3. Atualizar Estado", "4. Remover", "0. Voltar"]
        )
        op = ler_opcao("Escolha: ", ["0", "1", "2", "3", "4"])

        if op == "1":
            tit = ler_texto_obrigatorio("Título: ")
            
            print("Entidades existentes:")
            for e in self.sistema.entidades:
                print(f"- {e.nome}")
                
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
            cabecalhos = ["Título"]
            dados_tabela = [[acao.titulo] for acao in self.sistema.acoes]
            
            print("\n--- LISTA DE AÇÕES DISPONÍVEIS ---")
            self._imprimir_tabela(cabecalhos, dados_tabela)
            
            tit = ler_texto_obrigatorio("\nTítulo a consultar: ")
            acao_encontrada = self.sistema.consultar_acao(tit)
            
            if acao_encontrada:
                print(f"\n--- DETALHES DA AÇÃO: {acao_encontrada.titulo.upper()} ---")
                
                cabecalhos_detalhes = ["Campo", "Detalhe"]
                ods_str = ", ".join(str(o) for o in acao_encontrada.ods_associados) if acao_encontrada.ods_associados else "Nenhum"
                comps_str = ", ".join(f"{c} (Nível {n})" for c, n in acao_encontrada.competencias_desejadas.items()) if acao_encontrada.competencias_desejadas else "Nenhuma"
                
                dados_detalhes = [
                    ["Título", acao_encontrada.titulo],
                    ["Entidade Promotora", acao_encontrada.entidade],
                    ["Área Temática", acao_encontrada.area],
                    ["Data e Hora", acao_encontrada.data_hora],
                    ["Duração", f"{acao_encontrada.duracao} horas"],
                    ["Vagas Disponíveis", str(acao_encontrada.vagas)],
                    ["Localização", acao_encontrada.localizacao],
                    ["Estado", acao_encontrada.estado.capitalize()],
                    ["Métrica de Impacto", str(acao_encontrada.metrica_impacto)],
                    ["ODS Associados", ods_str],
                    ["Competências Desejadas", comps_str]
                ]
                
                self._imprimir_tabela(cabecalhos_detalhes, dados_detalhes)
            else:
                print("\nAção não encontrada. Verifique se escreveu o título corretamente.")

        elif op == "3":
            self._imprimir_tabela(
                ["acao_id","titulo","entidade_id","entidade_nome","area","data_hora","duracao_horas","localizacao","vagas","estado","metrica_impacto"], 
                [[getattr(a,"acao_id",""), getattr(a,"titulo",""), getattr(a,"entidade_id",""), a.entidade, a.area, a.data_hora, a.duracao, a.localizacao, a.vagas, a.estado, a.metrica_impacto] for a in self.sistema.acoes]
            )
            tit = ler_texto_obrigatorio("Título a atualizar: ")
            acao = self.sistema.consultar_acao(tit)
            if not acao:
                print("Ação não encontrada.")
                return
            
            print(f"Atual: {acao.__dict__}")
            novos = {}
            for campo, label in [("titulo","Título"),("entidade","Entidade"),("area","Área"),("data_hora","Data/Hora"),("localizacao","Localização"),("estado","Estado")]:
                val = input(f"{label} (ENTER mantém): ").strip()
                if val: novos[campo] = val
                
            for campo, label in [("duracao","Duração horas"),("vagas","Vagas"),("metrica_impacto","Métrica impacto")]:
                val = input(f"{label} (ENTER mantém): ").strip()
                if val: novos[campo] = int(val) if campo != "metrica_impacto" else float(val)
                
            self.sistema.atualizar_acao_completo(tit, novos)

        elif op == "4":
            self._imprimir_tabela(
                ["acao_id","titulo","entidade_id","entidade_nome","area","data_hora","duracao_horas","localizacao","vagas","estado","metrica_impacto"], 
                [[getattr(a,"acao_id",""), getattr(a,"titulo",""), getattr(a,"entidade_id",""), a.entidade, a.area, a.data_hora, a.duracao, a.localizacao, a.vagas, a.estado, a.metrica_impacto] for a in self.sistema.acoes]
            )
            tit = ler_texto_obrigatorio("Título a remover: ")
            acao = self.sistema.consultar_acao(tit)
            if not acao:
                print("Ação não encontrada.")
                return
                
            print(f"A remover: {acao.__dict__}")
            if ler_opcao("Confirma remoção? (S/N): ", ["S", "N"]) == "S":
                self.sistema.remover_acao(tit)

    def menu_inscricoes(self):
        """Processa a fila de inscrições de uma ação (RF02)."""
        pendentes = self.sistema.listar_acoes_com_fila_pendente()
        
        # Se não houver pendentes, avisamos logo o utilizador e evitamos pedir dados
        if not pendentes:
            print("\nNão existem ações com inscrições pendentes para avaliar no momento.")
            input("Prima ENTER para voltar.")
            return

        self._imprimir_tabela(
            ["acao_id", "titulo", "pendentes"], 
            [[getattr(a, "acao_id", ""), a.titulo, len(a.fila_inscricoes)] for a in pendentes]
        )
        
        # instrução de '0' para voltar
        titulo_acao = ler_texto_obrigatorio("\nTítulo da ação para processar fila (ou '0' para Voltar): ")
        
        # interrompe a função e volta ao menu principal
        if titulo_acao == "0":
            return
        
        prox = self.sistema.espreitar_proxima_inscricao(titulo_acao)
        if prox:
            print(f"\nPróxima inscrição: voluntário={prox.voluntario}, ação={prox.acao}, data_hora_inscricao={prox.data_hora_inscricao}")
            
            decisao = ler_opcao("Aprovar (A) ou Rejeitar (R)? ", ["A", "R"]).strip().upper()
            self.sistema.processar_inscricao_na_acao(titulo_acao, decisao == "A")
        else:
            print("\nAção não encontrada ou sem inscrições na fila.")

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
            self._imprimir_tabela(
                ["titulo", "entidade_nome", "area", "data_hora", "vagas", "ods_associados"], 
                [[a.titulo, a.entidade, a.area, a.data_hora, a.vagas, ",".join(str(o) for o in a.ods_associados)] for a in self.sistema.acoes]
            )
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

    # ==================================
    # RF06 - MENU DE FORMAÇÃO DE EQUIPAS
    # ==================================
    
    def menu_equipas(self):
        """Mostra o menu de Formação de Equipas com suporte a Undo (RF06)."""
        while True:
            self._imprimir_titulo("FORMAÇÃO DE EQUIPAS (RF06)")
            self._imprimir_opcoes(
                [
                    "1. Consultar Equipa de uma Ação",
                    "2. Adicionar Voluntário à Equipa",
                    "3. Remover Voluntário da Equipa",
                    "4. Desfazer Última Alteração (Undo)",
                    "5. Consultar Histórico de Alterações",
                    "0. Voltar",
                ]
            )
            op = ler_opcao("Escolha uma opção: ", ["0", "1", "2", "3", "4", "5"])

            if op == "0":
                break

            print("\n--- AÇÕES DISPONÍVEIS ---")
            self._imprimir_tabela(["Título da Ação"], [[a.titulo] for a in self.sistema.acoes])
            
            titulo_acao = ler_texto_obrigatorio("\nDigite o Título da Ação que pretende gerir: ")
            
            # Opção 1: Consultar a Equipa
            if op == "1":
                acao = self.sistema.consultar_acao(titulo_acao)
                if acao:
                    print(f"\n--- EQUIPA ATUAL: {acao.titulo.upper()} ---")
                    if not acao.equipa:
                        print("A equipa ainda não tem voluntários alocados.")
                    else:
                        self._imprimir_tabela(["Nome do Voluntário"], [[vol] for vol in acao.equipa])
                else:
                    print("\nAção não encontrada.")

            # Opção 2: Adicionar Voluntário (Com Avaliação de Perfil)
            elif op == "2":
                acao = self.sistema.consultar_acao(titulo_acao)
                if not acao:
                    print("\nAção não encontrada.")
                    continue

                # 1. CRIAR O DICIONÁRIO DE TRADUÇÃO: Pega no catálogo e associa {ID: Nome}
                mapa_ods = {ods["ods_id"]: ods["ods_nome"] for ods in self.sistema.ods_catalogo}

                # Ciclo para adicionar múltiplos voluntários
                while True:
                    print(f"\n--- AVALIAÇÃO DE PERFIS: {acao.titulo.upper()} ---")
                    cabecalhos = ["Nome", "Apto?", "ODS Partilhados", "Competências Partilhadas"]
                    dados = []
                    
                    for v in self.sistema.voluntarios:
                        if v.nome in acao.equipa:
                            continue 
                            
                        # Descobrir especificamente o que partilham 
                        ods_comum = v.ods_interesse.intersection(acao.ods_associados)
                        comps_comum = set(v.competencias.keys()).intersection(set(acao.competencias_desejadas.keys()))
                        
                        apto = bool(ods_comum or comps_comum)
                        
                        # 2. TRADUZIR OS NÚMEROS: Para cada ID em comum, vamos buscar o Nome ao mapa
                        nomes_ods_comum = [mapa_ods.get(o, f"ODS {o}") for o in ods_comum]
                        
                        # Formatar para a tabela (unir a lista com vírgulas)
                        ods_str = ", ".join(nomes_ods_comum) if nomes_ods_comum else "-"
                        comps_str = ", ".join(comps_comum) if comps_comum else "-"
                        
                        if apto:
                            dados.append([v.nome, "✅ SIM", ods_str, comps_str])
                        else:
                            dados.append([v.nome, "❌ NÃO", "-", "-"])
                            
                    self._imprimir_tabela(cabecalhos, dados)
                    
                    voluntario_nome = ler_texto_obrigatorio("\nDigite o Nome a adicionar (ou '0' para Voltar): ")
                    if voluntario_nome == "0":
                        break # Sai do ciclo e volta ao menu de equipas
                        
                    sucesso, mensagem = self.sistema.adicionar_voluntario_equipa(titulo_acao, voluntario_nome)
                    if sucesso:
                        print(f"\n[SUCESSO] {mensagem}")
                    else:
                        print(f"\n[ERRO] {mensagem}")
                        
                    continuar = ler_opcao("\nDeseja adicionar mais alguém? (S/N): ", ["S", "N"]).upper()
                    if continuar == "N":
                        break

            # Opção 3: Remover Voluntário
            elif op == "3":
                acao = self.sistema.consultar_acao(titulo_acao)
                if not acao:
                    print("\nAção não encontrada.")
                    continue
                    
                print(f"\n--- EQUIPA ATUAL: {acao.titulo.upper()} ---")
                if not acao.equipa:
                    print("A equipa já está vazia. Não há ninguém para remover.")
                    continue
                    
                self._imprimir_tabela(["Nome do Voluntário"], [[vol] for vol in acao.equipa])
                
                voluntario_nome = ler_texto_obrigatorio("\nDigite o Nome do Voluntário a remover: ")
                sucesso, mensagem = self.sistema.remover_voluntario_equipa(titulo_acao, voluntario_nome)
                if sucesso:
                    print(f"\n[SUCESSO] {mensagem}")
                else:
                    print(f"\n[ERRO] {mensagem}")

            # Opção 4: Desfazer Alteração (Undo)
            elif op == "4":
                sucesso, mensagem = self.sistema.desfazer_alteracao_equipa(titulo_acao)
                if sucesso:
                    print(f"\n[UNDO] {mensagem}")
                else:
                    print(f"\n[ERRO] {mensagem}")
                    
            # Opção 5: Ver Histórico da Pilha
            elif op == "5":
                acao = self.sistema.consultar_acao(titulo_acao)
                if not acao:
                    print("\nAção não encontrada.")
                    continue
                    
                historico = acao.historico_equipa.para_lista()
                
                if not historico:
                    print("\nAinda não foram registadas alterações na equipa durante esta sessão.")
                    continue
                    
                print(f"\n--- HISTÓRICO DE ALTERAÇÕES (PILHA): {acao.titulo.upper()} ---")
                cabecalhos = ["Data/Hora", "Tipo de Alteração", "Equipa Após Alteração"]
                dados = []
                
                for reg in historico:
                    membros_str = ", ".join(reg["estado_novo"]) if reg["estado_novo"] else "[Equipa Vazia]"
                    dados.append([reg["data_hora"], reg["tipo"], membros_str])
                    
                self._imprimir_tabela(cabecalhos, dados)

    # ==========================================
    # RF07 - MENU DE PESQUISA POR IMPACTO (BST)
    # ==========================================
    def menu_impacto(self):
        """Menu dedicado à consulta de Ações organizadas pelo seu impacto (RF07)."""
        while True:
            self._imprimir_titulo("PESQUISA POR IMPACTO (BST - RF07)")
            self._imprimir_opcoes(
                [
                    "1. Listar todas as Ações (Crescente ou Decrescente)",
                    "2. Pesquisar Ações por Impacto Exato",
                    "3. Consultar Ações num Intervalo de Impacto",
                    "4. Descobrir Ações com Maior e Menor Impacto",
                    "0. Voltar",
                ]
            )
            op = ler_opcao("Escolha uma opção: ", ["0", "1", "2", "3", "4"])

            if op == "0":
                break

            elif op == "1":
                ordem = ler_opcao("Ordem Crescente (C) ou Decrescente (D)? ", ["C", "D"]).strip().upper()
                crescente = (ordem == "C")
                acoes = self.sistema.consultar_acoes_por_impacto_ordem(crescente=crescente)
                
                print(f"\n--- AÇÕES ORDENADAS POR IMPACTO ---")
                cabecalhos = ["Título", "Entidade", "Impacto"]
                dados = [[a.titulo, a.entidade, a.metrica_impacto] for a in acoes]
                self._imprimir_tabela(cabecalhos, dados)

            elif op == "2":
                try:
                    valor_str = input("Digite o valor exato do impacto (ex: 80.5): ").strip()
                    impacto_alvo = float(valor_str)
                    
                    acoes = self.sistema.consultar_acoes_impacto_exato(impacto_alvo)
                    print(f"\n--- AÇÕES COM IMPACTO EXATO A {impacto_alvo} ---")
                    cabecalhos = ["Título", "Entidade", "Impacto"]
                    dados = [[a.titulo, a.entidade, a.metrica_impacto] for a in acoes]
                    self._imprimir_tabela(cabecalhos, dados)
                except ValueError:
                    print("\n[ERRO] Valor inválido! Por favor introduza um número válido.")

            elif op == "3":
                try:
                    min_str = input("Digite o Impacto Mínimo: ").strip()
                    max_str = input("Digite o Impacto Máximo: ").strip()
                    min_imp = float(min_str)
                    max_imp = float(max_str)
                    
                    if min_imp > max_imp:
                        print("\n[ERRO] O valor mínimo não pode ser superior ao valor máximo.")
                        continue
                        
                    acoes = self.sistema.consultar_acoes_por_impacto_intervalo(min_imp, max_imp)
                    print(f"\n--- AÇÕES NO INTERVALO [{min_imp} - {max_imp}] ---")
                    cabecalhos = ["Título", "Entidade", "Impacto"]
                    dados = [[a.titulo, a.entidade, a.metrica_impacto] for a in acoes]
                    self._imprimir_tabela(cabecalhos, dados)
                except ValueError:
                    print("\n[ERRO] Valor inválido! Por favor introduza números válidos.")

            elif op == "4":
                menores, maiores = self.sistema.consultar_acoes_impacto_extremos()
                
                print("\n--- AÇÃO(ÕES) COM MENOR IMPACTO ---")
                self._imprimir_tabela(["Título", "Entidade", "Impacto"], [[a.titulo, a.entidade, a.metrica_impacto] for a in menores])
                
                print("\n--- AÇÃO(ÕES) COM MAIOR IMPACTO ---")
                self._imprimir_tabela(["Título", "Entidade", "Impacto"], [[a.titulo, a.entidade, a.metrica_impacto] for a in maiores])

    # ==================================================
    # RF08 - PRIORIZAÇÃO DE CANDIDATURAS (MAX-HEAP)
    # ==================================================
    def menu_priorizacao(self):
        """Menu para listar as candidaturas ordenadas por prioridade (RF08)."""
        while True:
            self._imprimir_titulo("PRIORIZAÇÃO DE CANDIDATURAS (HEAP - RF08)")
            
            # Vamos mostrar que ações têm candidaturas pendentes
            pendentes = self.sistema.listar_acoes_com_fila_pendente()
            if not pendentes:
                print("\nNão existem ações com inscrições pendentes para avaliar no momento.")
                input("Prima ENTER para voltar.")
                break
                
            self._imprimir_tabela(
                ["Ação", "Nº Inscrições Pendentes"], 
                [[a.titulo, len(a.fila_inscricoes)] for a in pendentes]
            )
            
            print("\n0. Voltar")
            titulo_acao = input("\nDigite o Título da Ação para ver a prioridade (ou 0): ").strip()
            
            if titulo_acao == "0":
                break
                
            acao = self.sistema.consultar_acao(titulo_acao)
            if not acao:
                print("\nAção não encontrada.")
                continue
                
            # Chama o algoritmo Heapsort que construímos!
            candidaturas_ordenadas = self.sistema.gerar_candidaturas_ordenadas_heapsort(titulo_acao)
            
            if not candidaturas_ordenadas:
                print("\nNão existem candidaturas pendentes nesta ação.")
                continue
                
            print(f"\n--- CANDIDATURAS ORDENADAS POR PRIORIDADE: {acao.titulo.upper()} ---")
            print("(Critério matemático: +2 pts por ODS em comum, +1 pt por Competência em comum)")
            
            # Formatar os resultados
            cabecalhos = ["Lugar", "Nome do Voluntário", "Pontuação", "Data da Inscrição"]
            dados = []
            
            for i, (inscricao, pontos) in enumerate(candidaturas_ordenadas, 1):
                dados.append([
                    f"{i}º", 
                    inscricao.voluntario, 
                    f"{pontos} pontos", 
                    inscricao.data_hora_inscricao
                ])
                
            self._imprimir_tabela(cabecalhos, dados)
            
            # Destaque de quem está no topo do Max-Heap
            top_inscricao, top_pontos = candidaturas_ordenadas[0]
            print(f"\nO candidato mais adequado é '{top_inscricao.voluntario}' com {top_pontos} pontos!")
            
            input("\nPrima ENTER para continuar.")