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
        """Inicializa o menu com uma instância do sistema.

        :param sistema: Sistema de voluntariado em execução.
        """
        self.sistema = sistema

    def mostrar_menu_principal(self):
        """Mostra o menu principal e processa a opção escolhida."""
        while True:
            print("\n" + "="*50)
            print("   SISTEMA DE VOLUNTARIADO UNIVERSITÁRIO (AED)   ")
            print("="*50)
            print("1. Gestão do Programa (CRUD)")
            print("2. Processar Inscrições (Filas)")
            print("3. Pesquisas e Listagens")
            print("4. Dashboard e Estatísticas (Gráficos)")
            print("5. Exportar Relatório TXT (RF05)")
            print("0. Guardar e Sair")
            print("="*50)

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

    # ==========================================
    # SUBMENUS DE GESTÃO (RF01)
    # ==========================================
    def menu_gestao_geral(self):
        """Mostra submenu de gestão (RF01)."""
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
            if vinculo in ["estudante", "docente", "tecnico"]:
                self.sistema.adicionar_voluntario(Voluntario(nome, curso, faculdade, vinculo))
            else:
                print("Vínculo inválido.")
        elif op == "2":
            nome = ler_texto_obrigatorio("Nome a consultar: ")
            v = self.sistema.consultar_voluntario(nome)
            print(f"Encontrado: {v.nome} - {v.curso}" if v else "Não encontrado.")
        elif op == "3":
            nome = ler_texto_obrigatorio("Nome a atualizar: ")
            novo_curso = ler_texto_obrigatorio("Novo curso: ")
            self.sistema.atualizar_voluntario(nome, novo_curso)
        elif op == "4":
            nome = ler_texto_obrigatorio("Nome a remover: ")
            self.sistema.remover_voluntario(nome)

    def menu_crud_entidades(self):
        """Executa operações CRUD de entidades."""
        print("\n[ENTIDADES] 1:Adicionar | 2:Consultar | 3:Remover | 0:Voltar")
        op = ler_opcao("Escolha: ", ["0", "1", "2", "3"])
        
        if op == "1":
            nome = ler_texto_obrigatorio("Nome: ")
            tipo = ler_texto_obrigatorio("Tipo: ")
            area = ler_texto_obrigatorio("Área: ")
            loc = ler_texto_obrigatorio("Localização: ")
            self.sistema.adicionar_entidade(Entidade(nome, tipo, area, loc))
        elif op == "2":
            nome = ler_texto_obrigatorio("Nome a consultar: ")
            e = self.sistema.consultar_entidade(nome)
            print(f"Encontrada: {e.nome} - {e.tipo}" if e else "Não encontrada.")
        elif op == "3":
            nome = ler_texto_obrigatorio("Nome a remover: ")
            self.sistema.remover_entidade(nome)

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
            self.sistema.adicionar_acao(Acao(tit, ent, data, dur, vag, loc, area))
        elif op == "2":
            tit = ler_texto_obrigatorio("Título a consultar: ")
            a = self.sistema.consultar_acao(tit)
            print(f"Encontrada: {a.titulo} - Estado: {a.estado} - Vagas: {a.vagas}" if a else "Não encontrada.")
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

    # ==========================================
    # MÉTODOS MANTIDOS DOS OUTROS REQUISITOS
    # ==========================================
    def menu_inscricoes(self):
        """Processa fila de inscrições de uma ação (RF02)."""
        titulo_acao = ler_texto_obrigatorio("\nTítulo da ação para processar fila: ")
        decisao = ler_opcao("Aprovar (A) ou Rejeitar (R)? ", ["A", "R"]).strip().upper()
        if decisao in ['A', 'R']:
            self.sistema.processar_inscricao_na_acao(titulo_acao, decisao == 'A')
        else:
            print("Decisão inválida.")

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
            
            # Constrói o dicionário de filtros
            filtros = {
                "entidade": entidade,
                "area": area,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "vagas_min": vagas_min,
                "ods": ods
            }
            
            print("\nOrdenar resultados por:")
            print("1. Data e Hora")
            print("2. Métrica de Impacto")
            escolha = ler_opcao("Escolha (1/2): ", ["1", "2"]).strip()
            
            atributo = "metrica_impacto" if escolha == "2" else "data_hora"
            
            # Chama a função no gestor passando os filtros e o critério de ordenação
            self.sistema.pesquisar_e_listar_acoes(filtros, ordenar_por=atributo)