from sistema.gestor import SistemaVoluntariado
from sistema.modelos import Voluntario, Entidade, Acao

class MenuTerminal:
    def __init__(self, sistema: SistemaVoluntariado):
        self.sistema = sistema

    def mostrar_menu_principal(self):
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
        print("\n[VOLUNTÁRIOS] 1:Adicionar | 2:Consultar | 3:Atualizar | 4:Remover | 0:Voltar")
        op = input("Escolha: ").strip()
        
        if op == "1":
            nome = input("Nome: ")
            curso = input("Curso: ")
            faculdade = input("Faculdade: ")
            vinculo = input("Vínculo (estudante/docente/tecnico): ").lower()
            if vinculo in ["estudante", "docente", "tecnico"]:
                self.sistema.adicionar_voluntario(Voluntario(nome, curso, faculdade, vinculo))
            else:
                print("Vínculo inválido.")
        elif op == "2":
            nome = input("Nome a consultar: ")
            v = self.sistema.consultar_voluntario(nome)
            print(f"Encontrado: {v.nome} - {v.curso}" if v else "Não encontrado.")
        elif op == "3":
            nome = input("Nome a atualizar: ")
            novo_curso = input("Novo curso: ")
            self.sistema.atualizar_voluntario(nome, novo_curso)
        elif op == "4":
            nome = input("Nome a remover: ")
            self.sistema.remover_voluntario(nome)

    def menu_crud_entidades(self):
        print("\n[ENTIDADES] 1:Adicionar | 2:Consultar | 3:Remover | 0:Voltar")
        op = input("Escolha: ").strip()
        
        if op == "1":
            nome = input("Nome: ")
            tipo = input("Tipo: ")
            area = input("Área: ")
            loc = input("Localização: ")
            self.sistema.adicionar_entidade(Entidade(nome, tipo, area, loc))
        elif op == "2":
            nome = input("Nome a consultar: ")
            e = self.sistema.consultar_entidade(nome)
            print(f"Encontrada: {e.nome} - {e.tipo}" if e else "Não encontrada.")
        elif op == "3":
            nome = input("Nome a remover: ")
            self.sistema.remover_entidade(nome)

    def menu_crud_acoes(self):
        print("\n[AÇÕES] 1:Adicionar | 2:Consultar | 3:Atualizar Estado | 4:Remover | 0:Voltar")
        op = input("Escolha: ").strip()
        
        if op == "1":
            tit = input("Título: ")
            ent = input("Entidade Promotora: ")
            area = input("Área da ação: ")
            data = input("Data/Hora (YYYY-MM-DD HH:MM): ")
            try:
                dur = int(input("Duração (horas): "))
                vag = int(input("Vagas: "))
                loc = input("Localização: ")
                self.sistema.adicionar_acao(Acao(tit, ent, data, dur, vag, loc, area))
            except ValueError:
                print("Erro: Duração e vagas devem ser números inteiros (OR06).")
        elif op == "2":
            tit = input("Título a consultar: ")
            a = self.sistema.consultar_acao(tit)
            print(f"Encontrada: {a.titulo} - Estado: {a.estado} - Vagas: {a.vagas}" if a else "Não encontrada.")
        elif op == "3":
            tit = input("Título a atualizar: ")
            est = input("Novo estado (planeada/concluída/cancelada): ")
            self.sistema.atualizar_estado_acao(tit, est)
        elif op == "4":
            tit = input("Título a remover: ")
            self.sistema.remover_acao(tit)

    # ==========================================
    # MÉTODOS MANTIDOS DOS OUTROS REQUISITOS
    # ==========================================
    def menu_inscricoes(self):
        titulo_acao = input("\nTítulo da ação para processar fila: ")
        decisao = input("Aprovar (A) ou Rejeitar (R)? ").strip().upper()
        if decisao in ['A', 'R']:
            self.sistema.processar_inscricao_na_acao(titulo_acao, decisao == 'A')
        else:
            print("Decisão inválida.")

    def menu_pesquisas(self):
        print("\n--- PESQUISAS E LISTAGENS ---")
        print("1. Listar Voluntários por Prefixo (O(n) - Insertion Sort)")
        print("2. Pesquisar e Ordenar Ações (O(n log n) - Shell Sort)")
        print("0. Voltar")
        
        op = input("Opção: ").strip()
        
        if op == "1":
            prefixo = input("Prefixo do nome: ")
            self.sistema.listar_voluntarios_prefixo(prefixo)
            
        elif op == "2":
            print("\n--- Filtros de Ação ---")
            print("(Dica: Prima ENTER sem escrever nada para ignorar um filtro)")
            
            entidade = input("Entidade Promotora: ").strip()
            area = input("Área: ").strip()
            data_inicio = input("Data início (YYYY-MM-DD HH:MM): ").strip()
            data_fim = input("Data fim (YYYY-MM-DD HH:MM): ").strip()
            
            vagas_input = input("Vagas mínimas: ").strip()
            # Converte para inteiro se o utilizador digitou números, senão fica None
            vagas_min = int(vagas_input) if vagas_input.isdigit() else None
            
            ods_input = input("ODS específico (1-17): ").strip()
            ods = int(ods_input) if ods_input.isdigit() else None
            if ods is not None and (ods < 1 or ods > 17):
                print("ODS inválido. Use valores entre 1 e 17.")
                return
            
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
            escolha = input("Escolha (1/2): ").strip()
            
            atributo = "metrica_impacto" if escolha == "2" else "data_hora"
            
            # Chama a função no gestor passando os filtros e o critério de ordenação
            self.sistema.pesquisar_e_listar_acoes(filtros, ordenar_por=atributo)
-import sys
 from sistema.gestor import SistemaVoluntariado
 from sistema.modelos import Voluntario, Entidade, Acao
 
 class MenuTerminal:
     def __init__(self, sistema: SistemaVoluntariado):
         self.sistema = sistema
 
     def mostrar_menu_principal(self):
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
@@ -88,99 +87,107 @@ class MenuTerminal:
     def menu_crud_entidades(self):
         print("\n[ENTIDADES] 1:Adicionar | 2:Consultar | 3:Remover | 0:Voltar")
         op = input("Escolha: ").strip()
         
         if op == "1":
             nome = input("Nome: ")
             tipo = input("Tipo: ")
             area = input("Área: ")
             loc = input("Localização: ")
             self.sistema.adicionar_entidade(Entidade(nome, tipo, area, loc))
         elif op == "2":
             nome = input("Nome a consultar: ")
             e = self.sistema.consultar_entidade(nome)
             print(f"Encontrada: {e.nome} - {e.tipo}" if e else "Não encontrada.")
         elif op == "3":
             nome = input("Nome a remover: ")
             self.sistema.remover_entidade(nome)
 
     def menu_crud_acoes(self):
         print("\n[AÇÕES] 1:Adicionar | 2:Consultar | 3:Atualizar Estado | 4:Remover | 0:Voltar")
         op = input("Escolha: ").strip()
         
         if op == "1":
             tit = input("Título: ")
             ent = input("Entidade Promotora: ")
+            area = input("Área da ação: ")
             data = input("Data/Hora (YYYY-MM-DD HH:MM): ")
             try:
                 dur = int(input("Duração (horas): "))
                 vag = int(input("Vagas: "))
                 loc = input("Localização: ")
-                self.sistema.adicionar_acao(Acao(tit, ent, data, dur, vag, loc))
+                self.sistema.adicionar_acao(Acao(tit, ent, data, dur, vag, loc, area))
             except ValueError:
                 print("Erro: Duração e vagas devem ser números inteiros (OR06).")
         elif op == "2":
             tit = input("Título a consultar: ")
             a = self.sistema.consultar_acao(tit)
             print(f"Encontrada: {a.titulo} - Estado: {a.estado} - Vagas: {a.vagas}" if a else "Não encontrada.")
         elif op == "3":
             tit = input("Título a atualizar: ")
             est = input("Novo estado (planeada/concluída/cancelada): ")
             self.sistema.atualizar_estado_acao(tit, est)
         elif op == "4":
             tit = input("Título a remover: ")
             self.sistema.remover_acao(tit)
 
     # ==========================================
     # MÉTODOS MANTIDOS DOS OUTROS REQUISITOS
     # ==========================================
     def menu_inscricoes(self):
         titulo_acao = input("\nTítulo da ação para processar fila: ")
         decisao = input("Aprovar (A) ou Rejeitar (R)? ").strip().upper()
         if decisao in ['A', 'R']:
             self.sistema.processar_inscricao_na_acao(titulo_acao, decisao == 'A')
         else:
             print("Decisão inválida.")
 
     def menu_pesquisas(self):
         print("\n--- PESQUISAS E LISTAGENS ---")
         print("1. Listar Voluntários por Prefixo (O(n) - Insertion Sort)")
         print("2. Pesquisar e Ordenar Ações (O(n log n) - Shell Sort)")
         print("0. Voltar")
         
         op = input("Opção: ").strip()
         
         if op == "1":
             prefixo = input("Prefixo do nome: ")
             self.sistema.listar_voluntarios_prefixo(prefixo)
             
         elif op == "2":
             print("\n--- Filtros de Ação ---")
             print("(Dica: Prima ENTER sem escrever nada para ignorar um filtro)")
             
             entidade = input("Entidade Promotora: ").strip()
-            data = input("Data (ex: 2025-10 ou apenas 2025): ").strip()
+            area = input("Área: ").strip()
+            data_inicio = input("Data início (YYYY-MM-DD HH:MM): ").strip()
+            data_fim = input("Data fim (YYYY-MM-DD HH:MM): ").strip()
             
             vagas_input = input("Vagas mínimas: ").strip()
             # Converte para inteiro se o utilizador digitou números, senão fica None
             vagas_min = int(vagas_input) if vagas_input.isdigit() else None
             
             ods_input = input("ODS específico (1-17): ").strip()
             ods = int(ods_input) if ods_input.isdigit() else None
+            if ods is not None and (ods < 1 or ods > 17):
+                print("ODS inválido. Use valores entre 1 e 17.")
+                return
             
             # Constrói o dicionário de filtros
             filtros = {
                 "entidade": entidade,
-                "data": data,
+                "area": area,
+                "data_inicio": data_inicio,
+                "data_fim": data_fim,
                 "vagas_min": vagas_min,
                 "ods": ods
             }
             
             print("\nOrdenar resultados por:")
             print("1. Data e Hora")
             print("2. Métrica de Impacto")
             escolha = input("Escolha (1/2): ").strip()
             
             atributo = "metrica_impacto" if escolha == "2" else "data_hora"
             
             # Chama a função no gestor passando os filtros e o critério de ordenação
-            self.sistema.pesquisar_e_listar_acoes(filtros, ordenar_por=atributo)
\ No newline at end of file
+            self.sistema.pesquisar_e_listar_acoes(filtros, ordenar_por=atributo)
