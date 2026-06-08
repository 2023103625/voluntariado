"""
Módulo de interface terminal principal.

Este módulo implementa a camada interface (OR03), expondo menus
baseados em terminal para interagir com todos os requisitos funcionais da aplicação.
"""

from typing import List, Any
from sistema.gestor import SistemaVoluntariado
from sistema.modelos import Voluntario, Entidade, Acao
from interface.inputs import (
    ler_data_hora_iso_ou_vazio,
    ler_ods_ou_vazio,
    ler_opcao,
    ler_texto_obrigatorio,
)


class MenuTerminal:
    """
    Interface terminal principal da aplicação.

    Gere o ciclo de vida do programa, a navegação entre ecrãs e a
    interação com a camada de negócio (Gestor).
    """

    def __init__(self, sistema: SistemaVoluntariado) -> None:
        """
        Inicializa o menu principal.

        :param sistema: Instância central do Gestor do Sistema de Voluntariado.
        :type sistema: SistemaVoluntariado
        :return: Nada.
        :rtype: None
        """
        self.sistema: SistemaVoluntariado = sistema

    @staticmethod
    def _imprimir_titulo(titulo: str) -> None:
        """
        Imprime um título formatado para melhorar a legibilidade no terminal.

        :param titulo: Texto do título a exibir.
        :type titulo: str
        :return: Nada.
        :rtype: None
        """
        largura = 62
        print("\n" + "╔" + "═" * largura + "╗")
        print(f"║{titulo.center(largura)}║")
        print("╚" + "═" * largura + "╝")

    @staticmethod
    def _imprimir_opcoes(opcoes: List[str]) -> None:
        """
        Imprime um bloco de opções numeradas e alinhadas.

        :param opcoes: Lista de strings contendo as opções a exibir.
        :type opcoes: List[str]
        :return: Nada.
        :rtype: None
        """
        for opcao in opcoes:
            print(f"  • {opcao}")

    @staticmethod
    def _imprimir_tabela(headers: List[str], rows: List[List[Any]]) -> None:
        """
        Desenha uma tabela em formato texto baseada nas larguras das colunas.

        :param headers: Títulos das colunas da tabela.
        :type headers: List[str]
        :param rows: Lista de linhas, onde cada linha é uma lista de valores.
        :type rows: List[List[Any]]
        :return: Nada.
        :rtype: None
        """
        if not rows:
            print("(sem dados)")
            return
            
        larguras = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                larguras[i] = max(larguras[i], len(str(val)))
                
        linha = "+-" + "-+-".join("-" * l for l in larguras) + "-+"
        print(linha)
        
        print("| " + " | ".join(h.ljust(larguras[i]) for i, h in enumerate(headers)) + " |")
        print(linha)
        
        for row in rows:
            print("| " + " | ".join(str(v).ljust(larguras[i]) for i, v in enumerate(row)) + " |")
        print(linha)

    def mostrar_menu_principal(self) -> None:
        """
        Mostra o menu principal e processa opções até o utilizador decidir sair.
        """
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
                    "9. Gestão da Rede de Entidades (Grafos - RF14 a RF16)",
                    "0. Guardar e Sair",
                ]
            )

            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1": self.menu_gestao_geral()
            elif opcao == "2": self.menu_inscricoes()
            elif opcao == "3": self.menu_pesquisas()
            elif opcao == "4": self.menu_dashboards()
            elif opcao == "5": self.menu_exportar_relatorios()  
            elif opcao == "6": self.menu_equipas()
            elif opcao == "7": self.menu_impacto()
            elif opcao == "8": self.menu_priorizacao()
            elif opcao == "9": self.menu_rede_entidades()
            elif opcao == "0":
                print("\nA guardar os dados e a fechar o sistema. Até logo!")
                break
            else:
                print("Opção inválida.")
    
    def menu_dashboards(self) -> None:
        """
        Menu interativo para escolha do Dashboard pretendido.

        :return: Nada.
        :rtype: None
        """
        self._imprimir_titulo("DASHBOARDS E ESTATÍSTICAS")
        self._imprimir_opcoes(
            [
                "1. Visão de Ações e Impacto ODS (Dashboard V1 - RF04)",
                "2. Visão Demográfica e Panorama de Candidaturas (Dashboard V2 - RF09)",
                "0. Voltar",
            ]
        )
        
        op = ler_opcao("Escolha o Dashboard que pretende visualizar: ", ["0", "1", "2"])
        
        if op == "1":
            self.sistema.gerar_dashboard()
        elif op == "2":
            self.sistema.gerar_dashboard_v2()
        elif op == "0":
            return
            
        input("\nPrima ENTER para continuar.")
    
    def menu_exportar_relatorios(self) -> None:
        """
        Menu interativo para escolha do formato de exportação de dados (RF05).

        :return: Nada.
        :rtype: None
        """
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

    def menu_gestao_geral(self) -> None:
        """
        Mostra submenu de gestão CRUD (RF01).

        :return: Nada.
        :rtype: None
        """
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

    # =========================================================================
    # FUNÇÕES DE LEITURA (COM EARLY EXIT INTEGRADO)
    # =========================================================================

    def _ler_competencias_voluntario(self, voluntario: Voluntario) -> bool:
        """
        Lê iterativamente as competências do voluntário.

        :param voluntario: Objeto voluntário a atualizar.
        :type voluntario: Voluntario
        :return: True se concluiu com sucesso, False se o utilizador abortou.
        :rtype: bool
        """
        print("\nCompetências do voluntário (até 8).")
        while len(voluntario.competencias) < 8:
            nome = input("Competência (ENTER avança, '0' cancela operação): ").strip()
            if nome == "0": return False
            if not nome: break
            
            if nome in voluntario.competencias:
                print("Competência já adicionada.")
                continue
            
            nivel_str = input("Nível (1-5) ou '0' para cancelar operação: ").strip()
            if nivel_str == "0": return False
            if not nivel_str.isdigit() or not (1 <= int(nivel_str) <= 5):
                print("Nível inválido.")
                continue
                
            if voluntario.adicionar_competencia(nome, int(nivel_str)):
                print("Competência adicionada.")
        return True

    def _ler_interesses_voluntario(self, voluntario: Voluntario) -> bool:
        """
        Lê iterativamente as tags de interesse do voluntário.

        :param voluntario: Objeto voluntário a atualizar.
        :type voluntario: Voluntario
        :return: True se concluiu com sucesso, False se o utilizador abortou.
        :rtype: bool
        """
        print("\nInteresses/tags do voluntário (até 6).")
        while len(voluntario.interesses) < 6:
            tag = input("Tag de interesse (ENTER avança, '0' cancela operação): ").strip()
            if tag == "0": return False
            if not tag: break
            if voluntario.adicionar_interesse(tag):
                print("Tag adicionada.")
            else:
                print("Tag inválida, repetida ou limite atingido.")
        return True

    def _ler_ods_voluntario(self, voluntario: Voluntario) -> bool:
        """
        Lê iterativamente os ODS de interesse do voluntário.

        :param voluntario: Objeto voluntário a atualizar.
        :type voluntario: Voluntario
        :return: True se concluiu com sucesso, False se o utilizador abortou.
        :rtype: bool
        """
        print("\nODS de interesse do voluntário (máx. 3).")
        self._imprimir_tabela(
            ["ods_id", "ods_nome"],
            [[ods_id, ods_nome] for ods_id, ods_nome in self.sistema.ods_catalogo.items()],
        )
        while len(voluntario.ods_interesse) < 3:
            ods_str = input("ODS (1-17) [ENTER avança, '0' cancela operação]: ").strip()
            if ods_str == "0": return False
            if not ods_str: break
            if not ods_str.isdigit():
                print("Entrada inválida.")
                continue
                
            if voluntario.adicionar_ods_interesse(int(ods_str)):
                print("ODS adicionado.")
            else:
                print("ODS inválido, repetido ou limite atingido.")
        return True

    def _ler_tags_entidade(self, entidade: Entidade) -> bool:
        """
        Lê iterativamente as tags da entidade promotora.

        :param entidade: Objeto entidade a atualizar.
        :type entidade: Entidade
        :return: True se concluiu com sucesso, False se o utilizador abortou.
        :rtype: bool
        """
        print("\nTags da entidade (até 6).")
        while len(entidade.tags) < 6:
            tag = input("Tag (ENTER avança, '0' cancela operação): ").strip()
            if tag == "0": return False
            if not tag: break
            if entidade.adicionar_tag(tag):
                print("Tag adicionada.")
            else:
                print("Tag inválida, repetida ou limite atingido.")
        return True

    def _ler_ods_entidade(self, entidade: Entidade) -> bool:
        """
        Lê iterativamente os ODS principais da entidade promotora.

        :param entidade: Objeto entidade a atualizar.
        :type entidade: Entidade
        :return: True se concluiu com sucesso, False se o utilizador abortou.
        :rtype: bool
        """
        print("\nODS principais da entidade (entre 1 e 5 ODS).")
        self._imprimir_tabela(
            ["ods_id", "ods_nome"],
            [[ods_id, ods_nome] for ods_id, ods_nome in self.sistema.ods_catalogo.items()],
        )
        while True:
            ods_str = input("ODS (1-17) [ENTER avança, '0' cancela operação]: ").strip()
            if ods_str == "0": return False
            if not ods_str:
                if len(entidade.ods_foco) >= 1: break
                print("É obrigatório indicar pelo menos 1 ODS.")
                continue
                
            if ods_str.isdigit() and entidade.adicionar_ods_foco(int(ods_str)):
                print("ODS adicionado.")
            else:
                print("ODS inválido, repetido ou limite atingido (máx. 5).")
        return True

    def _ler_competencias_acao(self, acao: Acao) -> bool:
        """
        Lê iterativamente as competências exigidas para uma ação.

        :param acao: Objeto ação a atualizar.
        :type acao: Acao
        :return: True se concluiu com sucesso, False se o utilizador abortou.
        :rtype: bool
        """
        print("\nCompetências desejadas da ação (até 6).")
        while len(acao.competencias_desejadas) < 6:
            nome = input("Competência desejada (ENTER avança, '0' cancela operação): ").strip()
            if nome == "0": return False
            if not nome: break
            
            if nome in acao.competencias_desejadas:
                print("Competência já adicionada.")
                continue
                
            nivel_str = input("Nível mínimo (1-5) ou '0' para cancelar operação: ").strip()
            if nivel_str == "0": return False
            if not nivel_str.isdigit() or not (1 <= int(nivel_str) <= 5):
                print("Nível inválido.")
                continue
                
            if acao.adicionar_competencia(nome, int(nivel_str)):
                print("Competência adicionada.")
        return True

    def _ler_ods_acao(self, acao: Acao) -> bool:
        """
        Lê iterativamente os ODS associados a uma ação.

        :param acao: Objeto ação a atualizar.
        :type acao: Acao
        :return: True se concluiu com sucesso, False se o utilizador abortou.
        :rtype: bool
        """
        print("\nODS associados à ação (obrigatório entre 1 e 3).")
        self._imprimir_tabela(
            ["ods_id", "ods_nome"],
            [[ods_id, ods_nome] for ods_id, ods_nome in self.sistema.ods_catalogo.items()],
        )
        while True:
            ods_str = input("ODS (1-17) [ENTER avança, '0' cancela operação]: ").strip()
            if ods_str == "0": return False
            if not ods_str:
                if len(acao.ods_associados) >= 1: break
                print("É obrigatório indicar pelo menos 1 ODS.")
                continue
                
            if ods_str.isdigit() and acao.adicionar_ods(int(ods_str)):
                print("ODS adicionado.")
            else:
                print("ODS inválido, repetido ou limite atingido (máx. 3).")
        return True

    # =========================================================
    # MENUS CRUD (OPERAÇÕES DE GESTÃO)
    # =========================================================

    def menu_crud_voluntarios(self) -> None:
        """
        Gere as operações de Criação, Leitura, Atualização e Remoção de Voluntários.

        :return: Nada.
        :rtype: None
        """
        self._imprimir_titulo("VOLUNTÁRIOS")
        self._imprimir_opcoes(
            ["1. Adicionar", "2. Consultar", "3. Atualizar", "4. Remover", "0. Voltar"]
        )
        op = ler_opcao("Escolha: ", ["0", "1", "2", "3", "4"])

        if op == "1":
            nome = ler_texto_obrigatorio("Nome (ou '0' para cancelar): ")
            if nome == "0": return

            curso = ler_texto_obrigatorio("Curso (ou '0' para cancelar): ")
            if curso == "0": return
            
            faculdade = ler_texto_obrigatorio("Faculdade (ou '0' para cancelar): ")
            if faculdade == "0": return
            
            vinculo = ler_opcao(
                "Vínculo (estudante/docente/tecnico) ou '0' para cancelar: ",
                ["estudante", "docente", "tecnico", "0"],
            ).lower()
            if vinculo == "0": return

            ano = None
            if vinculo == "estudante":
                ano_str = input("Ano do estudante (1-8) ou '0' para cancelar: ").strip()
                if ano_str == "0": return
                ano = int(ano_str) if ano_str.isdigit() else 1

            voluntario = Voluntario(nome, curso, faculdade, vinculo, ano)
            
            if not self._ler_competencias_voluntario(voluntario): return
            if not self._ler_interesses_voluntario(voluntario): return
            if not self._ler_ods_voluntario(voluntario): return
            
            self.sistema.adicionar_voluntario(voluntario)

        elif op == "2":
            termo = input("Nome a pesquisar (vazio para todos, ou '0' para cancelar): ").strip()
            if termo == "0": return
            
            if not termo:
                resultados = list(self.sistema.voluntarios.values())
            else:
                v_exato = self.sistema.consultar_voluntario(termo)
                resultados = [v_exato] if v_exato else self.sistema.pesquisar_voluntarios(termo)
            
            self._imprimir_tabela(
                ["voluntario_id", "nome", "curso", "faculdade", "vinculo_institucional", "ano"],
                [[getattr(v, "voluntario_id", ""), v.nome, v.curso, v.faculdade, v.vinculo, v.ano or "-"] for v in resultados if v],
            )

        elif op == "3":
            self._imprimir_tabela(
                ["voluntario_id", "nome", "curso", "faculdade", "vinculo_institucional", "ano"],
                [[getattr(v, "voluntario_id", ""), v.nome, v.curso, v.faculdade, v.vinculo, v.ano or "-"] for v in self.sistema.voluntarios.values()],
            )
            nome = ler_texto_obrigatorio("Nome a atualizar (ou '0' para cancelar): ")
            if nome == "0": return

            voluntario = self.sistema.consultar_voluntario(nome)
            if not voluntario:
                print("Voluntário não encontrado.")
                return
            
            print(f"\n--- ATUALIZAR DADOS BASE ---")
            novos = {}
            novo_nome = input(f"Nome atual ({voluntario.nome}) -> Novo (ENTER mantém, '0' cancela): ").strip()
            if novo_nome == "0": return
            if novo_nome: novos["nome"] = novo_nome
            
            novo_curso = input(f"Curso atual ({voluntario.curso}) -> Novo (ENTER mantém, '0' cancela): ").strip()
            if novo_curso == "0": return
            if novo_curso: novos["curso"] = novo_curso
            
            nova_faculdade = input(f"Faculdade atual ({voluntario.faculdade}) -> Novo (ENTER mantém, '0' cancela): ").strip()
            if nova_faculdade == "0": return
            if nova_faculdade: novos["faculdade"] = nova_faculdade
            
            novo_vinculo = input(f"Vínculo ({voluntario.vinculo}) -> Novo (estudante/docente/tecnico, ENTER mantém, '0' cancela): ").strip().lower()
            if novo_vinculo == "0": return
            if novo_vinculo in ["estudante", "docente", "tecnico"]: 
                novos["vinculo"] = novo_vinculo
            
            vinculo_final = novos.get("vinculo", voluntario.vinculo)
            if vinculo_final == "estudante":
                ano_atual = voluntario.ano if voluntario.ano else "N/A"
                ano_txt = input(f"Ano ({ano_atual}) -> Novo (1-8, ENTER mantém, '0' cancela): ").strip()
                if ano_txt == "0": return
                if ano_txt.isdigit(): novos["ano"] = int(ano_txt)
            else:
                novos["ano"] = None 
                
            self.sistema.atualizar_voluntario_completo(nome, novos)

            print("\n--- ATUALIZAR PERFIL (COMPETÊNCIAS, TAGS E ODS) ---")
            
            print(f"Competências atuais: {voluntario.competencias}")
            if ler_opcao("Deseja redefinir as competências? (S/N): ", ["S", "N"]).upper() == "S":
                bkp_comp = dict(voluntario.competencias)
                voluntario.competencias.clear()
                if not self._ler_competencias_voluntario(voluntario):
                    voluntario.competencias = bkp_comp
                    print("\nOperação abortada. Dados antigos restaurados.")
                    return
                
            print(f"\nInteresses atuais: {voluntario.interesses}")
            if ler_opcao("Deseja redefinir os interesses/tags? (S/N): ", ["S", "N"]).upper() == "S":
                bkp_int = set(voluntario.interesses)
                voluntario.interesses.clear()
                if not self._ler_interesses_voluntario(voluntario):
                    voluntario.interesses = bkp_int
                    print("\nOperação abortada. Dados antigos restaurados.")
                    return
                
            print(f"\nODS atuais: {voluntario.ods_interesse}")
            if ler_opcao("Deseja redefinir os ODS de interesse? (S/N): ", ["S", "N"]).upper() == "S":
                bkp_ods = set(voluntario.ods_interesse)
                voluntario.ods_interesse.clear()
                if not self._ler_ods_voluntario(voluntario):
                    voluntario.ods_interesse = bkp_ods
                    print("\nOperação abortada. Dados antigos restaurados.")
                    return

            print("\n[SUCESSO] Registo do voluntário totalmente atualizado!")

        elif op == "4":
            self._imprimir_tabela(
                ["voluntario_id", "nome", "curso", "faculdade", "vinculo_institucional", "ano"],
                [[getattr(v, "voluntario_id", ""), v.nome, v.curso, v.faculdade, v.vinculo, v.ano or "-"] for v in self.sistema.voluntarios.values()],
            )
            nome = ler_texto_obrigatorio("Nome a remover (ou '0' para cancelar): ")
            if nome == "0": return

            voluntario = self.sistema.consultar_voluntario(nome)
            if not voluntario:
                print("Voluntário não encontrado.")
                return
            print(f"A remover: {voluntario.__dict__}")
            if ler_opcao("Confirma remoção? (S/N): ", ["S", "N"]) == "S":
                self.sistema.remover_voluntario(nome)

    def menu_crud_entidades(self) -> None:
        """
        Gere as operações de Criação, Leitura, Atualização e Remoção de Entidades.

        :return: Nada.
        :rtype: None
        """
        self._imprimir_titulo("ENTIDADES")
        self._imprimir_opcoes(
            ["1. Adicionar", "2. Consultar", "3. Atualizar", "4. Remover", "0. Voltar"]
        )
        op = ler_opcao("Escolha: ", ["0", "1", "2", "3", "4"])

        if op == "1":
            nome = ler_texto_obrigatorio("Nome (ou '0' para cancelar): ")
            if nome == "0": return

            tipo = ler_opcao(
                "Tipo (núcleo/associação/serviço/ong parceira) ou '0' para cancelar: ",
                ["núcleo", "associação", "serviço", "ong parceira", "0"],
            )
            if tipo == "0": return
            
            area = ler_texto_obrigatorio("Área de intervenção (ou '0' para cancelar): ")
            if area == "0": return
            
            loc = ler_texto_obrigatorio("Localização (ou '0' para cancelar): ")
            if loc == "0": return
            
            url = input("URL (opcional, ou '0' para cancelar): ").strip()
            if url == "0": return
            url_final = url if url else None

            entidade = Entidade(nome, tipo, area, loc, url_final)
            
            if not self._ler_tags_entidade(entidade): return
            if not self._ler_ods_entidade(entidade): return
            
            self.sistema.adicionar_entidade(entidade)

        elif op == "2":
            cabecalhos = ["ID da Entidade", "Nome"]
            dados_lista = [[getattr(e, "entidade_id", ""), e.nome or "-"] for e in self.sistema.entidades.values()]
            
            print("\n--- LISTA DE ENTIDADES PARCEIRAS ---")
            self._imprimir_tabela(cabecalhos, dados_lista)
            
            nome = ler_texto_obrigatorio("\nNome a consultar (ou '0' para cancelar): ")
            if nome == "0": return

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
                [[getattr(e, "entidade_id", ""), e.nome, e.tipo, e.area, e.localizacao, e.url or "-"] for e in self.sistema.entidades.values()]
            )
            nome = ler_texto_obrigatorio("Nome da entidade a atualizar (ou '0' para cancelar): ")
            if nome == "0": return

            entidade = self.sistema.consultar_entidade(nome)
            if not entidade:
                print("Entidade não encontrada.")
                return
            
            print(f"\n--- ATUALIZAR DADOS BASE ---")
            novos = {}
            for campo, label in [("nome", "Nome"), ("tipo", "Tipo"), ("area", "Área"), ("localizacao", "Localização"), ("url", "URL")]:
                val = input(f"{label} atual ({getattr(entidade, campo)}) -> Novo (ENTER mantém, '0' cancela): ").strip()
                if val == "0": return
                if val: novos[campo] = val
                
            self.sistema.atualizar_entidade_completo(nome, novos)
            
            print("\n--- ATUALIZAR PERFIL (TAGS E ODS) ---")
            print(f"Tags atuais: {entidade.tags}")
            if ler_opcao("Deseja redefinir as Tags? (S/N): ", ["S", "N"]).upper() == "S":
                bkp_tags = set(entidade.tags)
                entidade.tags.clear()
                if not self._ler_tags_entidade(entidade):
                    entidade.tags = bkp_tags
                    print("\nOperação abortada. Dados antigos restaurados.")
                    return
                
            print(f"\nODS atuais: {entidade.ods_foco}")
            if ler_opcao("Deseja redefinir os ODS? (S/N): ", ["S", "N"]).upper() == "S":
                bkp_ods_ent = set(entidade.ods_foco)
                entidade.ods_foco.clear()
                if not self._ler_ods_entidade(entidade):
                    entidade.ods_foco = bkp_ods_ent
                    print("\nOperação abortada. Dados antigos restaurados.")
                    return
                    
            print("\n[SUCESSO] Registo da entidade totalmente atualizado!")

        elif op == "4":
            self._imprimir_tabela(
                ["entidade_id", "nome", "tipo", "area_intervencao", "localizacao", "url"], 
                [[getattr(e, "entidade_id", ""), e.nome, e.tipo, e.area, e.localizacao, e.url or "-"] for e in self.sistema.entidades.values()]
            )
            nome = ler_texto_obrigatorio("Nome a remover (ou '0' para cancelar): ")
            if nome == "0": return

            entidade = self.sistema.consultar_entidade(nome)
            if not entidade:
                print("Entidade não encontrada.")
                return
            print(f"A remover: {entidade.__dict__}")
            if ler_opcao("Confirma remoção? (S/N): ", ["S", "N"]) == "S":
                self.sistema.remover_entidade(nome)

    def menu_crud_acoes(self) -> None:
        """Gere as operações de Criação, Leitura, Atualização e Remoção de Ações."""
        self._imprimir_titulo("AÇÕES")
        self._imprimir_opcoes(["1. Adicionar", "2. Consultar", "3. Atualizar Dados", "4. Remover", "0. Voltar"])
        op = ler_opcao("Escolha: ", ["0", "1", "2", "3", "4"])

        if op == "1":
            tit = ler_texto_obrigatorio("Título (ou '0' para cancelar): ")
            if tit == "0": return
            
            print("\nEntidades registadas no sistema:")
            for e in self.sistema.entidades.values():
                print(f"- {e.nome}")
                
            entidades_parceiras = []
            print("\nIndique as Entidades Parceiras (pressione ENTER com o campo vazio para terminar):")
            while True:
                ent = input(f"Entidade {len(entidades_parceiras) + 1} (ou '0' para cancelar): ").strip()
                if ent == "0": return
                if not ent:
                    if len(entidades_parceiras) >= 1: break
                    print("A ação exige pelo menos uma entidade promotora!")
                    continue
                    
                if self.sistema.consultar_entidade(ent):
                    if ent not in entidades_parceiras:
                        entidades_parceiras.append(ent)
                        print(f"'{ent}' associada à ação.")
                    else:
                        print("Entidade já adicionada.")
                else:
                    print("Entidade não existe no sistema. Valide o nome e tente novamente.")
            
            area = ler_texto_obrigatorio("Área da ação (ou '0' para cancelar): ")
            if area == "0": return
            
            data = ler_data_hora_iso_ou_vazio("Data/Hora (YYYY-MM-DD HH:MM) ou ENTER para cancelar: ")
            if not data: return

            dur_str = input("Duração em horas (ou '0' para cancelar): ").strip()
            if dur_str == "0": return
            dur = int(dur_str) if dur_str.isdigit() else 1
            
            vag_str = input("Vagas (>=0) ou '-1' para cancelar: ").strip()
            if vag_str == "-1": return
            vag = int(vag_str) if vag_str.lstrip('-').isdigit() else 0
            
            loc = ler_opcao("Localização (campus/externo/online) ou '0' para cancelar: ", ["campus", "externo", "online", "0"])
            if loc == "0": return
            
            estado = ler_opcao("Estado (planeada/concluída/cancelada) ou '0' para cancelar: ", ["planeada", "concluída", "cancelada", "0"])
            if estado == "0": return
            
            imp_str = input("Métrica impacto (0-100) ou '-1' para cancelar: ").strip()
            if imp_str == "-1": return
            impacto = float(imp_str) if imp_str.replace('.', '', 1).isdigit() else 0.0

            acao = Acao(tit, entidades_parceiras, data, dur, vag, loc, area)
            acao.estado = estado
            acao.metrica_impacto = impacto

            if not self._ler_competencias_acao(acao): return
            if not self._ler_ods_acao(acao): return
            self.sistema.adicionar_acao(acao)

        elif op == "2":
            cabecalhos = ["Título"]
            dados_tabela = [[acao.titulo] for acao in self.sistema.acoes.values()]
            
            print("\n--- LISTA DE AÇÕES DISPONÍVEIS ---")
            self._imprimir_tabela(cabecalhos, dados_tabela)
            
            tit = ler_texto_obrigatorio("\nTítulo a consultar (ou '0' para cancelar): ")
            if tit == "0": return

            acao_encontrada = self.sistema.consultar_acao(tit)
            
            if acao_encontrada:
                print(f"\n--- DETALHES DA AÇÃO: {acao_encontrada.titulo.upper()} ---")
                
                cabecalhos_detalhes = ["Campo", "Detalhe"]
                ods_str = ", ".join(str(o) for o in acao_encontrada.ods_associados) if acao_encontrada.ods_associados else "Nenhum"
                comps_str = ", ".join(f"{c} (Nível {n})" for c, n in acao_encontrada.competencias_desejadas.items()) if acao_encontrada.competencias_desejadas else "Nenhuma"
                entidades_str = ", ".join(acao_encontrada.entidades) if acao_encontrada.entidades else "Nenhuma"
                
                dados_detalhes = [
                    ["Título", acao_encontrada.titulo],
                    ["Entidade(s) Promotora(s)", entidades_str],
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
                print("\nAção não encontrada.")

        elif op == "3":
            self._imprimir_tabela(
                ["titulo", "entidades", "area", "data_hora", "vagas", "estado"], 
                [[a.titulo, ", ".join(a.entidades)[:20]+"...", a.area, a.data_hora, a.vagas, a.estado] for a in self.sistema.acoes.values()]
            )
            tit = ler_texto_obrigatorio("Título a atualizar (ou '0' para cancelar): ")
            if tit == "0": return

            acao = self.sistema.consultar_acao(tit)
            if not acao:
                print("Ação não encontrada.")
                return
            
            print(f"\n--- ATUALIZAR DADOS BASE ---")
            novos = {}
            for campo, label in [("titulo","Título"), ("area","Área"), ("data_hora","Data/Hora"), ("localizacao","Localização"), ("estado","Estado")]:
                val = input(f"{label} atual ({getattr(acao, campo)}) -> Novo (ENTER mantém, '0' cancela): ").strip()
                if val == "0": return
                if val: novos[campo] = val
                
            for campo, label in [("duracao","Duração horas"), ("vagas","Vagas"), ("metrica_impacto","Métrica impacto")]:
                val = input(f"{label} atual ({getattr(acao, campo)}) -> Novo (ENTER mantém, '0' cancela): ").strip()
                if val == "0": return
                if val: novos[campo] = int(val) if campo != "metrica_impacto" else float(val)
                
            self.sistema.atualizar_acao_completo(tit, novos)

            print("\n--- ATUALIZAR PERFIL (ENTIDADES, COMPETÊNCIAS E ODS) ---")
            print(f"Entidades parceiras atuais: {', '.join(acao.entidades)}")
            if ler_opcao("Deseja redefinir as Entidades? (S/N): ", ["S", "N"]).upper() == "S":
                entidades_backup = set(acao.entidades)
                acao.entidades.clear()
                while True:
                    ent = input("Entidade parceira (ENTER para terminar, '0' cancela): ").strip()
                    if ent == "0":
                        acao.entidades = entidades_backup
                        print("Operação abortada. Entidades antigas restauradas.")
                        return
                    if not ent:
                        if len(acao.entidades) >= 1: break
                        print("Precisa de pelo menos uma entidade!")
                        continue
                    if self.sistema.consultar_entidade(ent):
                        acao.entidades.add(ent)
                    else:
                        print("Entidade não existe no sistema.")

            print(f"Competências atuais: {acao.competencias_desejadas}")
            if ler_opcao("Deseja redefinir as Competências Desejadas? (S/N): ", ["S", "N"]).upper() == "S":
                bkp_comp = dict(acao.competencias_desejadas)
                acao.competencias_desejadas.clear()
                if not self._ler_competencias_acao(acao):
                    acao.competencias_desejadas = bkp_comp
                    return
                
            print(f"\nODS atuais: {acao.ods_associados}")
            if ler_opcao("Deseja redefinir os ODS Associados? (S/N): ", ["S", "N"]).upper() == "S":
                bkp_ods = set(acao.ods_associados)
                acao.ods_associados.clear()
                if not self._ler_ods_acao(acao):
                    acao.ods_associados = bkp_ods
                    return
                    
            print("\n[SUCESSO] Registo da ação totalmente atualizado!")

        elif op == "4":
            tit = ler_texto_obrigatorio("Título a remover (ou '0' para cancelar): ")
            if tit == "0": return
            if ler_opcao("Confirma remoção? (S/N): ", ["S", "N"]) == "S":
                self.sistema.remover_acao(tit)

    def menu_inscricoes(self) -> None:
        """
        Processa iterativamente a fila de inscrições (FIFO) de uma ação (RF02).

        :return: Nada.
        :rtype: None
        """
        pendentes = self.sistema.listar_acoes_com_fila_pendente()
        
        if not pendentes:
            print("\nNão existem ações com inscrições pendentes para avaliar no momento.")
            input("Prima ENTER para voltar.")
            return

        self._imprimir_tabela(
            ["acao_id", "titulo", "pendentes"], 
            [[getattr(a, "acao_id", ""), a.titulo, len(a.fila_inscricoes)] for a in pendentes]
        )
        
        titulo_acao = ler_texto_obrigatorio("\nTítulo da ação para processar fila (ou '0' para Voltar): ")
        if titulo_acao == "0":
            return
        
        prox = self.sistema.espreitar_proxima_inscricao(titulo_acao)
        if prox:
            print(f"\nPróxima inscrição: voluntário={prox.voluntario}, ação={prox.acao}, data_hora_inscricao={prox.data_hora_inscricao}")
            
            decisao = ler_opcao("Aprovar (A) ou Rejeitar (R)? (ou '0' para cancelar): ", ["A", "R", "0"]).strip().upper()
            if decisao == "0": return
            
            self.sistema.processar_inscricao_na_acao(titulo_acao, decisao == "A")
        else:
            print("\nAção não encontrada ou sem inscrições na fila.")

    def menu_pesquisas(self) -> None:
        """
        Executa o menu de pesquisas, listagens e ordenações avançadas (RF03).

        :return: Nada.
        :rtype: None
        """
        print("\n--- PESQUISAS E LISTAGENS ---")
        print("1. Listar Voluntários por Prefixo (O(n) - Insertion Sort)")
        print("2. Pesquisar e Ordenar Ações (O(n log n) - Merge Sort)")
        print("0. Voltar")

        op = ler_opcao("Opção: ", ["0", "1", "2"])

        if op == "1":
            prefixo = ler_texto_obrigatorio("Prefixo do nome (ou '0' para Voltar): ")
            if prefixo == "0": return
            self.sistema.listar_voluntarios_prefixo(prefixo)

        elif op == "2":
            self._imprimir_tabela(
                ["titulo", "entidades_promotoras", "area", "data_hora", "vagas", "ods_associados"], 
                [[a.titulo, ", ".join(a.entidades), a.area, a.data_hora, a.vagas, ",".join(str(o) for o in a.ods_associados)] for a in self.sistema.acoes.values()]
            )
            print("\n--- Filtros de Ação ---")
            print("(Dica: Prima ENTER sem escrever nada para ignorar um filtro)")

            entidade = input("Entidade Promotora (ou '0' para Voltar): ").strip()
            if entidade == "0": return

            area = input("Área (ou '0' para Voltar): ").strip()
            if area == "0": return
            
            data_inicio = ler_data_hora_iso_ou_vazio("Data início (YYYY-MM-DD HH:MM) ou ENTER para ignorar: ")
            data_fim = ler_data_hora_iso_ou_vazio("Data fim (YYYY-MM-DD HH:MM) ou ENTER para ignorar: ")

            vagas_input = input("Vagas mínimas (ou '0' para Voltar): ").strip()
            if vagas_input == "0": return
            vagas_min = int(vagas_input) if vagas_input.isdigit() else None

            ods = ler_ods_ou_vazio("ODS específico (1-17) ou ENTER para ignorar: ")

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
            print("0. Cancelar pesquisa")
            escolha = ler_opcao("Escolha: ", ["0", "1", "2"]).strip()
            if escolha == "0": return

            atributo = "metrica_impacto" if escolha == "2" else "data_hora"
            self.sistema.pesquisar_e_listar_acoes(filtros, ordenar_por=atributo)
            input("\nPrima ENTER para continuar.")

    def menu_equipas(self) -> None:
        """
        Mostra o menu de Formação de Equipas com suporte a Undo usando Pilhas (RF06).

        :return: Nada.
        :rtype: None
        """
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
            self._imprimir_tabela(["Título da Ação"], [[a.titulo] for a in self.sistema.acoes.values()])
            
            titulo_acao = ler_texto_obrigatorio("\nDigite o Título da Ação que pretende gerir (ou '0' para Voltar): ")
            if titulo_acao == "0":
                continue
            
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

            elif op == "2":
                acao = self.sistema.consultar_acao(titulo_acao)
                if not acao:
                    print("\nAção não encontrada.")
                    continue

                # 1. DICIONÁRIO DE TRADUÇÃO (Eficiência O(1))
                mapa_ods = self.sistema.ods_catalogo

                while True:
                    print(f"\n--- AVALIAÇÃO DE PERFIS: {acao.titulo.upper()} ---")
                    cabecalhos = ["Nome", "Apto?", "ODS Partilhados", "Competências Partilhadas", "Interesse na Área"]
                    dados = []
                    
                    for v in self.sistema.voluntarios.values():
                        if v.nome in acao.equipa:
                            continue 
                            
                        ods_comum = v.ods_interesse.intersection(acao.ods_associados)
                        comps_comum = set(v.competencias.keys()).intersection(set(acao.competencias_desejadas.keys()))
                        interesses_vol = {i.lower() for i in v.interesses}
                        interesse_na_area = acao.area.lower() in interesses_vol
                        
                        # Está apto se tiver pelo menos um critério em comum (ODS, Competências ou Interesse na área)
                        apto = bool(ods_comum or comps_comum or interesse_na_area)
                        nomes_ods_comum = [mapa_ods.get(o, f"ODS {o}") for o in ods_comum]
                        
                        ods_str = ", ".join(nomes_ods_comum) if nomes_ods_comum else "-"
                        comps_str = ", ".join(comps_comum) if comps_comum else "-"
                        ints_str = acao.area.title() if interesse_na_area else "-"
                        
                        if apto:
                            dados.append([v.nome, "SIM", ods_str, comps_str, ints_str])
                        else:
                            dados.append([v.nome, "NÃO", "-", "-", "-"])
                            
                    self._imprimir_tabela(cabecalhos, dados)
                    
                    voluntario_nome = ler_texto_obrigatorio("\nDigite o Nome a adicionar (ou '0' para Voltar): ")
                    if voluntario_nome == "0":
                        break 
                        
                    sucesso, mensagem = self.sistema.adicionar_voluntario_equipa(titulo_acao, voluntario_nome)
                    if sucesso:
                        print(f"\n[SUCESSO] {mensagem}")
                    else:
                        print(f"\n[ERRO] {mensagem}")
                        
                    continuar = ler_opcao("\nDeseja adicionar mais alguém? (S/N): ", ["S", "N"]).upper()
                    if continuar == "N":
                        break

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
                
                voluntario_nome = ler_texto_obrigatorio("\nDigite o Nome do Voluntário a remover (ou '0' para Voltar): ")
                if voluntario_nome == "0":
                    continue
                    
                sucesso, mensagem = self.sistema.remover_voluntario_equipa(titulo_acao, voluntario_nome)
                if sucesso:
                    print(f"\n[SUCESSO] {mensagem}")
                else:
                    print(f"\n[ERRO] {mensagem}")

            elif op == "4":
                sucesso, mensagem = self.sistema.desfazer_alteracao_equipa(titulo_acao)
                if sucesso:
                    print(f"\n[UNDO] {mensagem}")
                else:
                    print(f"\n[ERRO] {mensagem}")
                    
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

    def menu_impacto(self) -> None:
        """
        Menu dedicado à consulta de Ações organizadas pelo seu impacto através da BST (RF07).

        :return: Nada.
        :rtype: None
        """
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
                ordem = ler_opcao("Ordem Crescente (C) ou Decrescente (D)? (ou 'V' para Voltar) ", ["C", "D", "V"]).strip().upper()
                if ordem == "V": continue
                
                crescente = (ordem == "C")
                acoes = self.sistema.consultar_acoes_por_impacto_ordem(crescente=crescente)
                
                print(f"\n--- AÇÕES ORDENADAS POR IMPACTO ---")
                cabecalhos = ["Título", "Entidade(s)", "Impacto"]
                dados = [[a.titulo, ", ".join(a.entidades), a.metrica_impacto] for a in acoes]
                self._imprimir_tabela(cabecalhos, dados)

            elif op == "2":
                try:
                    valor_str = input("Digite o valor exato do impacto ou 'V' para Voltar: ").strip()
                    if valor_str.upper() == "V": continue
                    
                    impacto_alvo = float(valor_str)
                    
                    acoes = self.sistema.consultar_acoes_impacto_exato(impacto_alvo)
                    print(f"\n--- AÇÕES COM IMPACTO EXATO A {impacto_alvo} ---")
                    cabecalhos = ["Título", "Entidade(s)", "Impacto"]
                    dados = [[a.titulo, ", ".join(a.entidades), a.metrica_impacto] for a in acoes]
                    self._imprimir_tabela(cabecalhos, dados)
                except ValueError:
                    print("\n[ERRO] Valor inválido! Por favor introduza um número válido.")

            elif op == "3":
                try:
                    min_str = input("Digite o Impacto Mínimo (ou 'V' para Voltar): ").strip()
                    if min_str.upper() == "V": continue
                    
                    max_str = input("Digite o Impacto Máximo: ").strip()
                    min_imp = float(min_str)
                    max_imp = float(max_str)
                    
                    if min_imp > max_imp:
                        print("\n[ERRO] O valor mínimo não pode ser superior ao valor máximo.")
                        continue
                        
                    acoes = self.sistema.consultar_acoes_por_impacto_intervalo(min_imp, max_imp)
                    print(f"\n--- AÇÕES NO INTERVALO [{min_imp} - {max_imp}] ---")
                    cabecalhos = ["Título", "Entidade(s)", "Impacto"]
                    dados = [[a.titulo, ", ".join(a.entidades), a.metrica_impacto] for a in acoes]
                    self._imprimir_tabela(cabecalhos, dados)
                except ValueError:
                    print("\n[ERRO] Valor inválido! Por favor introduza números válidos.")

            elif op == "4":
                menores, maiores = self.sistema.consultar_acoes_impacto_extremos()
                
                print("\n--- AÇÃO(ÕES) COM MENOR IMPACTO ---")
                self._imprimir_tabela(["Título", "Entidade(s)", "Impacto"], [[a.titulo, ", ".join(a.entidades), a.metrica_impacto] for a in menores])
                
                print("\n--- AÇÃO(ÕES) COM MAIOR IMPACTO ---")
                self._imprimir_tabela(["Título", "Entidade(s)", "Impacto"], [[a.titulo, ", ".join(a.entidades), a.metrica_impacto] for a in maiores])

    def menu_priorizacao(self) -> None:
        """
        Menu para extrair e listar candidaturas ordenadas por prioridade via Max-Heap (RF08).

        :return: Nada.
        :rtype: None
        """
        while True:
            self._imprimir_titulo("PRIORIZAÇÃO DE CANDIDATURAS (HEAP - RF08)")
            
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
            titulo_acao = input("\nDigite o Título da Ação para ver a prioridade (ou '0' para Voltar): ").strip()
            
            if titulo_acao == "0":
                break
                
            acao = self.sistema.consultar_acao(titulo_acao)
            if not acao:
                print("\nAção não encontrada.")
                continue
                
            candidaturas_ordenadas = self.sistema.gerar_candidaturas_ordenadas_heapsort(titulo_acao)
            
            if not candidaturas_ordenadas:
                print("\nNão existem candidaturas pendentes nesta ação.")
                continue
                
            print(f"\n--- CANDIDATURAS ORDENADAS POR PRIORIDADE: {acao.titulo.upper()} ---")
            print("(Critério matemático: +2 pts por ODS em comum, +1 pt por Competência em comum)")
            
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
            
            top_inscricao, top_pontos = candidaturas_ordenadas[0]
            print(f"\nO candidato mais adequado é '{top_inscricao.voluntario}' com {top_pontos} pontos!")
            
            input("\nPrima ENTER para continuar.")
    

    # =========================================================
    # MENU REDE DE ENTIDADES (GRAFOS - RF14, 15, 16)
    # =========================================================

    def menu_rede_entidades(self) -> None:
        """
        Menu dedicado à gestão e visualização da Rede de Entidades via Grafos.
        Cobre os requisitos RF14 (Gestão), RF15 (Caminho/Centralidade) e RF16 (Visualização).
        """
        # Sincroniza o grafo com as ações logo à entrada do menu
        self.sistema.reconstruir_rede_entidades()

        while True:
            self._imprimir_titulo("REDE DE ENTIDADES (GRAFOS)")
            self._imprimir_opcoes(
                [
                    "1. Consultar Ligações da Rede (Sincronizadas por Ações)",
                    "2. Adicionar/Remover Local na Rede",
                    "3. Adicionar/Remover Ligação (Aresta)",
                    "4. Calcular Caminho Mais Curto entre Entidades (RF15)",
                    "5. Ver Ranking de Centralidade de Proximidade (RF15)",
                    "6. Visualizar Grafo Graficamente (NetworkX - RF16)",
                    "0. Voltar",
                ]
            )
            op = ler_opcao("Escolha uma opção: ", ["0", "1", "2", "3", "4", "5", "6"])

            grafo = self.sistema.rede_entidades

            if op == "0":
                break

            elif op == "1":
                print("\n--- MATRIZ DE LIGAÇÕES DA REDE ---")
                dados = []
                for no, vizinhos in grafo.adjacencias.items():
                    if not vizinhos:
                        dados.append([no.title(), "Isolada", "-"])
                    else:
                        conexoes_lista = []
                        acoes_comum_lista = []
                        
                        for viz, peso in vizinhos.items():
                            conexoes_lista.append(f"{viz.title()} (peso {peso})")
                            
                            # Procurar os títulos das ações em comum entre 'no' e 'viz' 
                            acoes_partilhadas = []
                            for acao in self.sistema.acoes.values():
                                entidades_acao_lower = {e.lower() for e in acao.entidades}
                                if no.lower() in entidades_acao_lower and viz.lower() in entidades_acao_lower:
                                    acoes_partilhadas.append(acao.titulo)
                                    
                            if acoes_partilhadas:
                                # Formata o texto: Com Entidade B: Ação 1, Ação 2
                                acoes_comum_lista.append(f"Com {viz.title()}: {', '.join(acoes_partilhadas)}")
                            else:
                                # Caso a ligação tenha sido criada manualmente sem ações no sistema
                                acoes_comum_lista.append(f"Com {viz.title()}: (Ligação Manual)")
                                
                        dados.append([
                            no.title(), 
                            " \n ".join(conexoes_lista), 
                            " \n ".join(acoes_comum_lista)
                        ])
                
                self._imprimir_tabela(["Entidade (Nó)", "Ligações (Arestas e Pesos)", "Ações em Comum (Títulos)"], dados)
                input("\nPrima ENTER para continuar.")

            elif op == "2":
                sub_op = ler_opcao("Pretende Adicionar (A) ou Remover (R) um nó? (ou '0' para cancelar): ", ["A", "R", "0"]).upper()
                if sub_op == "0": continue
                
                nome = input("Nome do local/entidade: ").strip()
                if sub_op == "A":
                    if grafo.adicionar_entidade(nome.lower()):
                        print(f"[SUCESSO] O nó '{nome}' foi adicionado à rede.")
                    else:
                        print(f"[ERRO] O nó '{nome}' já existe.")
                elif sub_op == "R":
                    if grafo.remover_entidade(nome.lower()):
                        print(f"[SUCESSO] O nó '{nome}' e as suas arestas foram removidas.")
                    else:
                        print(f"[ERRO] O nó '{nome}' não foi encontrado.")

            elif op == "3":
                sub_op = ler_opcao("Pretende Adicionar (A) ou Remover (R) uma parceria/ligação? (ou '0' para cancelar): ", ["A", "R", "0"]).upper()
                if sub_op == "0": continue
                
                ent1 = input("Nome da Entidade 1: ").strip().lower()
                ent2 = input("Nome da Entidade 2: ").strip().lower()
                
                obj_ent1 = self.sistema.consultar_entidade(ent1)
                obj_ent2 = self.sistema.consultar_entidade(ent2)
                
                if not obj_ent1 or not obj_ent2:
                    print("\n[ERRO] Uma ou ambas as entidades não existem no sistema. Registe-as primeiro no Menu 1.")
                    continue
                
                if sub_op == "A":
                    print("\n--- AÇÕES DISPONÍVEIS PARA SERVIR DE LIGAÇÃO ---")
                    dados_acoes = [[a.titulo, ", ".join(a.entidades)] for a in self.sistema.acoes.values()]
                    self._imprimir_tabela(["Título da Ação", "Entidades Parceiras Atuais"], dados_acoes)
                    
                    tit_acao = ler_texto_obrigatorio("\nDigite o Título da Ação que unirá estas entidades (ou '0' para cancelar): ")
                    if tit_acao == "0": continue
                    
                    acao = self.sistema.consultar_acao(tit_acao)
                    if not acao:
                        print("\n[ERRO] Ação não encontrada.")
                        continue
                        
                    # Adiciona as entidades à Ação real e reconstrói o grafo!
                    acao.entidades.add(obj_ent1.nome) 
                    acao.entidades.add(obj_ent2.nome)
                    self.sistema.reconstruir_rede_entidades()
                    
                    print(f"\n[SUCESSO] Ligação criada! '{obj_ent1.nome}' e '{obj_ent2.nome}' são parceiras na ação '{acao.titulo}'.")
                    
                elif sub_op == "R":
                    acoes_comuns = [a for a in self.sistema.acoes.values() if ent1 in {e.lower() for e in a.entidades} and ent2 in {e.lower() for e in a.entidades}]
                            
                    if not acoes_comuns:
                        print(f"\n[ERRO] Não existem ações partilhadas entre as duas. Não há ligação a remover.")
                        continue
                        
                    print("\n--- AÇÕES EM COMUM (LIGAÇÕES ATUAIS) ---")
                    dados_acoes = [[a.titulo, ", ".join(a.entidades)] for a in acoes_comuns]
                    self._imprimir_tabela(["Título da Ação", "Entidades Parceiras Atuais"], dados_acoes)
                    
                    tit_acao = ler_texto_obrigatorio("\nDigite o Título da Ação comum para quebrar a ligação (ou '0' para cancelar): ")
                    if tit_acao == "0": continue
                    
                    acao = self.sistema.consultar_acao(tit_acao)
                    if not acao or acao not in acoes_comuns:
                        print("\n[ERRO] Ação inválida ou não partilhada.")
                        continue
                        
                    print(f"\nPara quebrar a parceria na ação '{acao.titulo}', quem deve ser removido?")
                    print(f"1. Remover '{obj_ent1.nome}'\n2. Remover '{obj_ent2.nome}'\n3. Remover Ambas")
                    
                    op_rem = ler_opcao("Escolha: ", ["1", "2", "3", "0"])
                    if op_rem == "0": continue
                    
                    entidades_para_manter = set()
                    for e in acao.entidades:
                        e_low = e.lower()
                        if op_rem == "1" and e_low == ent1: continue
                        if op_rem == "2" and e_low == ent2: continue
                        if op_rem == "3" and (e_low == ent1 or e_low == ent2): continue
                        entidades_para_manter.add(e)
                        
                    acao.entidades = entidades_para_manter
                    self.sistema.reconstruir_rede_entidades()
                    print(f"\n[SUCESSO] A ligação foi desfeita. A rede foi atualizada!")

            elif op == "4":
                print("\n--- DESCOBRIR CAMINHO MAIS CURTO (BFS) ---")
                origem = input("Entidade de Origem: ").strip()
                destino = input("Entidade de Destino: ").strip()
                
                caminho = self.sistema.pesquisar_caminho_curto_entidades(origem, destino)
                
                if caminho:
                    passos = " -> ".join([no.title() for no in caminho])
                    print(f"\n[SUCESSO] Caminho encontrado! ({len(caminho)-1} saltos)")
                    print(f"Trajeto: {passos}")
                else:
                    print("\n[AVISO] Não foi encontrado nenhum caminho possível entre essas entidades.")
                
                input("\nPrima ENTER para continuar.")

            elif op == "5":
                print("\n--- RANKING DE CENTRALIDADE (PROXIMIDADE) ---")
                centralidades = self.sistema.calcular_centralidade_rede()
                
                if not centralidades:
                    print("Rede vazia.")
                    continue
                    
                dados = [[f"{i+1}º", ent, f"{cent:.4f}"] for i, (ent, cent) in enumerate(centralidades)]
                self._imprimir_tabela(["Posição", "Entidade", "Grau de Proximidade (Inverso Dist.)"], dados)
                input("\nPrima ENTER para continuar.")

            elif op == "6":
                print("\n[A INICIAR O MOTOR NETWORKX E MATPLOTLIB...]")
                print("Por favor verifique se a janela do gráfico abriu (pode estar minimizada).")
                self.sistema.visualizar_rede_parceiros()