import os
import time
import matplotlib.pyplot as plt
from typing import List, Optional, Dict, Any
from sistema.modelos import Voluntario, Entidade, Acao, Inscricao
from sistema.algoritmos.insertion_sort import ordenar_voluntarios_nome
from sistema.algoritmos.shell_sort import shell_sort_acoes
from sistema.base_dados import BaseDados

class SistemaVoluntariado:
    """Classe principal que gere todo o programa de voluntariado."""

    def __init__(self):
        self.voluntarios: List[Voluntario] = []
        self.entidades: List[Entidade] = []
        self.acoes: List[Acao] = []

    # ==========================================
    # OR02 - LEITURA E ESCRITA DE DADOS (JSON)
    # ==========================================
    
    def carregar_sistema(self, caminho_json: str) -> None:
        """Carrega os dados iniciais do JSON para as listas de objetos (OR02)."""
        dados = BaseDados.carregar_dados(caminho_json)

        if not dados:
            print("Iniciando o sistema com a base de dados vazia.")
            return

        self.voluntarios = [self._desserializar_voluntario(v) for v in dados.get("voluntarios", [])]
        self.entidades = [self._desserializar_entidade(e) for e in dados.get("entidades", [])]
        self.acoes = [self._desserializar_acao(a) for a in dados.get("acoes", [])]
        print("Base de dados JSON encontrada e carregada com sucesso.")

    def guardar_sistema(self, caminho_json: str) -> None:
        """Guarda as listas de objetos de volta no JSON (OR02)."""
        dados_exportar = {
            "voluntarios": [self._serializar_voluntario(v) for v in self.voluntarios],
            "entidades": [self._serializar_entidade(e) for e in self.entidades],
            "acoes": [self._serializar_acao(a) for a in self.acoes]
        }
        BaseDados.guardar_dados(caminho_json, dados_exportar)

    def _serializar_voluntario(self, voluntario: Voluntario) -> Dict[str, Any]:
        """Converte um objeto Voluntario para dicionário JSON-serializável."""
        return {
            "nome": voluntario.nome,
            "curso": voluntario.curso,
            "faculdade": voluntario.faculdade,
            "vinculo": voluntario.vinculo,
            "ano": voluntario.ano,
            "competencias": voluntario.competencias,
            "interesses": voluntario.interesses,
            "ods_interesse": voluntario.ods_interesse,
        }

    def _serializar_entidade(self, entidade: Entidade) -> Dict[str, Any]:
        """Converte um objeto Entidade para dicionário JSON-serializável."""
        return {
            "nome": entidade.nome,
            "tipo": entidade.tipo,
            "area": entidade.area,
            "localizacao": entidade.localizacao,
            "url": entidade.url,
            "tags": entidade.tags,
            "ods_foco": entidade.ods_foco,
        }

    def _serializar_acao(self, acao: Acao) -> Dict[str, Any]:
        """Converte um objeto Acao para dicionário JSON-serializável."""
        return {
            "titulo": acao.titulo,
            "entidade": acao.entidade,
            "area": acao.area,
            "data_hora": acao.data_hora,
            "duracao": acao.duracao,
            "vagas": acao.vagas,
            "localizacao": acao.localizacao,
            "estado": acao.estado,
            "metrica_impacto": acao.metrica_impacto,
            "competencias_desejadas": acao.competencias_desejadas,
            "ods_associados": acao.ods_associados,
            "inscricoes_aprovadas": [
                {
                    "voluntario": inscricao.voluntario,
                    "acao": inscricao.acao,
                    "data_hora_inscricao": inscricao.data_hora_inscricao,
                    "estado": inscricao.estado,
                }
                for inscricao in acao.inscricoes_aprovadas
            ],
        }

    def _desserializar_voluntario(self, dados: Dict[str, Any]) -> Voluntario:
        """Converte um dicionário para objeto Voluntario."""
        voluntario = Voluntario(
            nome=dados.get("nome", ""),
            curso=dados.get("curso", ""),
            faculdade=dados.get("faculdade", ""),
            vinculo=dados.get("vinculo", ""),
            ano=dados.get("ano"),
        )
        voluntario.competencias = dados.get("competencias", {})
        voluntario.interesses = dados.get("interesses", [])
        voluntario.ods_interesse = dados.get("ods_interesse", [])
        return voluntario

    def _desserializar_entidade(self, dados: Dict[str, Any]) -> Entidade:
        """Converte um dicionário para objeto Entidade."""
        entidade = Entidade(
            nome=dados.get("nome", ""),
            tipo=dados.get("tipo", ""),
            area=dados.get("area", ""),
            localizacao=dados.get("localizacao", ""),
            url=dados.get("url"),
        )
        entidade.tags = dados.get("tags", [])
        entidade.ods_foco = dados.get("ods_foco", [])
        return entidade

    def _desserializar_acao(self, dados: Dict[str, Any]) -> Acao:
        """Converte um dicionário para objeto Acao."""
        acao = Acao(
            titulo=dados.get("titulo", ""),
            entidade=dados.get("entidade", ""),
            data_hora=dados.get("data_hora", ""),
            duracao=dados.get("duracao", 0),
            vagas=dados.get("vagas", 0),
            localizacao=dados.get("localizacao", ""),
            area=dados.get("area", ""),
        )
        acao.estado = dados.get("estado", "planeada")
        acao.metrica_impacto = dados.get("metrica_impacto", 0.0)
        acao.competencias_desejadas = dados.get("competencias_desejadas", {})
        acao.ods_associados = dados.get("ods_associados", [])
        for item in dados.get("inscricoes_aprovadas", []):
            inscricao = Inscricao(
                voluntario=item.get("voluntario", ""),
                acao=item.get("acao", acao.titulo),
                data_hora_inscricao=item.get("data_hora_inscricao", ""),
            )
            inscricao.atualizar_estado(item.get("estado", "aprovada"))
            acao.inscricoes_aprovadas.append(inscricao)
        return acao

    # ==========================================
    # RF01 - GESTÃO DE VOLUNTÁRIOS
    # ==========================================
    def adicionar_voluntario(self, voluntario: Voluntario) -> None:
        if self.consultar_voluntario(voluntario.nome):
            print(f"Erro: O voluntário '{voluntario.nome}' já existe.")
        else:
            self.voluntarios.append(voluntario)
            print("Voluntário adicionado com sucesso.")

    def consultar_voluntario(self, nome: str) -> Optional[Voluntario]:
        return next((v for v in self.voluntarios if v.nome.lower() == nome.lower()), None)

    def remover_voluntario(self, nome: str) -> bool:
        voluntario = self.consultar_voluntario(nome)
        if voluntario:
            self.voluntarios.remove(voluntario)
            print(f"Voluntário '{nome}' removido.")
            return True
        print("Voluntário não encontrado.")
        return False

    def atualizar_voluntario(self, nome: str, novo_curso: str = None) -> bool:
        """Exemplo de atualização: permite alterar o curso de um voluntário."""
        voluntario = self.consultar_voluntario(nome)
        if voluntario:
            if novo_curso:
                voluntario.curso = novo_curso
                print(f"Curso de '{nome}' atualizado para {novo_curso}.")
            return True
        print("Voluntário não encontrado.")
        return False

    # ==========================================
    # RF01 - GESTÃO DE ENTIDADES
    # ==========================================
    def adicionar_entidade(self, entidade: Entidade) -> None:
        if self.consultar_entidade(entidade.nome):
            print(f"Erro: A entidade '{entidade.nome}' já existe.")
        else:
            self.entidades.append(entidade)
            print("Entidade adicionada com sucesso.")

    def consultar_entidade(self, nome: str) -> Optional[Entidade]:
        return next((e for e in self.entidades if e.nome.lower() == nome.lower()), None)

    def remover_entidade(self, nome: str) -> bool:
        entidade = self.consultar_entidade(nome)
        if entidade:
            self.entidades.remove(entidade)
            print(f"Entidade '{nome}' removida.")
            return True
        print("Entidade não encontrada.")
        return False

    # ==========================================
    # RF01 - GESTÃO DE AÇÕES
    # ==========================================
    def adicionar_acao(self, acao: Acao) -> None:
        if self.consultar_acao(acao.titulo):
            print(f"Erro: A ação '{acao.titulo}' já existe.")
        else:
            self.acoes.append(acao)
            print("Ação adicionada com sucesso.")

    def consultar_acao(self, titulo: str) -> Optional[Acao]:
        return next((a for a in self.acoes if a.titulo.lower() == titulo.lower()), None)

    def remover_acao(self, titulo: str) -> bool:
        acao = self.consultar_acao(titulo)
        if acao:
            self.acoes.remove(acao)
            print(f"Ação '{titulo}' removida.")
            return True
        print("Ação não encontrada.")
        return False

    def atualizar_estado_acao(self, titulo: str, novo_estado: str) -> bool:
        """Atualiza o estado da ação (planeada, concluída, cancelada)."""
        acao = self.consultar_acao(titulo)
        estados_validos = ["planeada", "concluída", "cancelada"]
        if acao and novo_estado.lower() in estados_validos:
            acao.estado = novo_estado.lower()
            print(f"Estado da ação '{titulo}' atualizado para {novo_estado}.")
            return True
        print("Ação não encontrada ou estado inválido.")
        return False

    # ==========================================
    # RESTANTES REQUISITOS (MANTIDOS INTACTOS)
    # ==========================================
    def processar_inscricao_na_acao(self, titulo_acao: str, aprovada: bool) -> None:
        acao = self.consultar_acao(titulo_acao)
        if not acao:
            print("Ação não encontrada.")
            return
        inscricao = acao.fila_inscricoes.dequeue()
        if not inscricao:
            print("Fila vazia.")
            return
        if aprovada and acao.vagas > 0:
            inscricao.atualizar_estado("aprovada")
            acao.vagas -= 1 
            acao.inscricoes_aprovadas.append(inscricao)
            print(f"Aprovada. Vagas restantes: {acao.vagas}")
        elif aprovada:
            inscricao.atualizar_estado("lista de espera")
            print("Sem vagas! Lista de espera.")
        else:
            inscricao.atualizar_estado("rejeitada")
            print("Rejeitada.")

    def listar_voluntarios_prefixo(self, prefixo: str) -> None:
        resultados = [v for v in self.voluntarios if v.nome.lower().startswith(prefixo.lower())]
        ordenar_voluntarios_nome(resultados)
        for v in resultados:
            print(
                f"- {v.nome} | Curso: {v.curso} | Faculdade: {v.faculdade} "
                f"| Competências: {v.competencias} | Tags: {v.interesses} | ODS: {v.ods_interesse}"
            )

    # ==========================================
    # RF03 (ii) - PESQUISA E LISTAGEM DE AÇÕES
    # ==========================================
    
    def pesquisar_e_listar_acoes(self, filtros: dict, ordenar_por: str = "data_hora") -> None:
        """
        Filtra as ações com base num dicionário de critérios e ordena o 
        resultado final usando o algoritmo Shell Sort (O(n log n)).
        """
        # Começamos com uma cópia de todas as ações
        resultados = self.acoes.copy()

        # 1. Filtro por Entidade (se o texto digitado existir no nome da entidade)
        if filtros.get("entidade"):
            resultados = [a for a in resultados if filtros["entidade"].lower() in a.entidade.lower()]

        # 2. Filtro por Área
        if filtros.get("area"):
            resultados = [a for a in resultados if filtros["area"].lower() in a.area.lower()]

        # 3. Filtro por Intervalo de Datas (strings no formato YYYY-MM-DD HH:MM)
        data_inicio = filtros.get("data_inicio")
        data_fim = filtros.get("data_fim")
        if data_inicio:
            resultados = [a for a in resultados if a.data_hora >= data_inicio]
        if data_fim:
            resultados = [a for a in resultados if a.data_hora <= data_fim]
            
        # 4. Filtro por Vagas Mínimas
        if filtros.get("vagas_min") is not None:
            resultados = [a for a in resultados if a.vagas >= filtros["vagas_min"]]
            
        # 5. Filtro por ODS Associado
        if filtros.get("ods") is not None:
            resultados = [a for a in resultados if filtros["ods"] in a.ods_associados]

        # Se após os filtros a lista ficar vazia...
        if not resultados:
            print("\nNenhuma ação encontrada com os filtros especificados.")
            return

        # Por fim, ordena os resultados filtrados usando o teu algoritmo
        shell_sort_acoes(resultados, ordenar_por)

        # Imprime os resultados
        print(f"\n--- Resultados da Pesquisa ({len(resultados)} encontradas) ---")
        for a in resultados:
            print(f"[{getattr(a, ordenar_por)}] {a.titulo} (Entidade: {a.entidade}) - Vagas: {a.vagas}")

    def gerar_dashboard(self) -> None:
        """
        Gera os indicadores textuais (incluindo o Top 5) e os gráficos obrigatórios.
        """
        acoes_por_ods = {i: 0 for i in range(1, 18)}
        horas_por_ods = {i: 0 for i in range(1, 18)}
        
        # Dicionário para somar as horas de cada voluntário: {"Nome do Voluntário": 10}
        horas_por_voluntario = {}

        for acao in self.acoes:
            for ods in acao.ods_associados:
                acoes_por_ods[ods] += 1
                
            # Só contabilizamos horas se a ação já estiver concluída!
            if acao.estado.lower() == "concluída":
                for ods in acao.ods_associados:
                    horas_por_ods[ods] += acao.duracao
                    
                # Vamos a cada inscrição aprovada desta ação dar as horas ao voluntário
                for inscricao in getattr(acao, 'inscricoes_aprovadas', []):
                    nome_vol = inscricao.voluntario
                    if nome_vol not in horas_por_voluntario:
                        horas_por_voluntario[nome_vol] = 0
                    horas_por_voluntario[nome_vol] += acao.duracao

        # --- Impressão no Terminal ---
        print("\n" + "="*50)
        print("   DASHBOARD E ESTATÍSTICAS DO PROGRAMA   ")
        print("="*50)
        
        print("\n[AÇÕES POR ODS - TOP 3]")
        # Ordena o dicionário de ODS de forma decrescente
        top_ods = sorted(acoes_por_ods.items(), key=lambda x: x[1], reverse=True)[:3]
        for ods, contagem in top_ods:
            if contagem > 0:
                print(f" - ODS {ods}: {contagem} ações")

        print("\n[TOP 5 VOLUNTÁRIOS POR HORAS]")
        # Ordena o dicionário de voluntários de forma decrescente e apanha os 5 primeiros
        top_voluntarios = sorted(horas_por_voluntario.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_voluntarios:
            for i, (nome, horas) in enumerate(top_voluntarios, 1):
                print(f" {i}º Lugar: {nome} - {horas} horas totais")
        else:
            print(" -> Nenhum voluntário tem horas registadas em ações concluídas.")
        print("="*50)

        # Chama a função que já tinhas para desenhar os gráficos do matplotlib
        self._desenhar_graficos(acoes_por_ods, horas_por_ods)

    def _desenhar_graficos(self, acoes_ods: dict, horas_ods: dict) -> None:
        if not sum(acoes_ods.values()):
            print("Sem dados.")
            return
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        ax1.bar([f"ODS {k}" for k, v in acoes_ods.items() if v > 0], [v for v in acoes_ods.values() if v > 0], color='skyblue')
        ax1.set_title('Ações por ODS')
        ax2.bar([f"ODS {k}" for k, v in horas_ods.items() if v > 0], [v for v in horas_ods.values() if v > 0], color='lightgreen')
        ax2.set_title('Horas por ODS')
        plt.tight_layout()
        plt.show()

    # ==========================================
    # RF05 - REQUISITO OPCIONAL (Exportar Relatório)
    # ==========================================
    
    def exportar_relatorio(self) -> None:
        """
        Gera um ficheiro TXT com o resumo do programa, incluindo os dados
        do Dashboard. Cumpre o RF05 utilizando os módulos 'os' e 'time'.
        """
        if not self.acoes:
            print("Não há dados suficientes para gerar um relatório.")
            return

        # 1. Recalcular as estatísticas (igual ao Dashboard)
        acoes_por_ods = {i: 0 for i in range(1, 18)}
        horas_por_voluntario = {}

        for acao in self.acoes:
            for ods in acao.ods_associados:
                acoes_por_ods[ods] += 1
                
            if acao.estado.lower() == "concluída":
                for inscricao in getattr(acao, 'inscricoes_aprovadas', []):
                    nome_vol = inscricao.voluntario
                    # Se o voluntário já lá estiver, soma; se não, começa em 0 e soma a duração
                    horas_por_voluntario[nome_vol] = horas_por_voluntario.get(nome_vol, 0) + acao.duracao

        top_ods = sorted(acoes_por_ods.items(), key=lambda x: x[1], reverse=True)[:3]
        top_voluntarios = sorted(horas_por_voluntario.items(), key=lambda x: x[1], reverse=True)[:5]

        # 2. Criar a pasta "relatorios" se ela não existir
        os.makedirs("relatorios", exist_ok=True)
        
        # 3. Gerar um nome único para o ficheiro baseado na data e hora
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nome_ficheiro = os.path.join("relatorios", f"relatorio_oficial_{timestamp}.txt")

        # 4. Escrever os dados no ficheiro TXT
        try:
            with open(nome_ficheiro, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write(" RELATÓRIO OFICIAL DO PROGRAMA DE VOLUNTARIADO \n")
                f.write("=" * 50 + "\n")
                f.write(f"Data de Geração: {time.strftime('%d/%m/%Y %H:%M:%S')}\n\n")

                f.write("--- RESUMO GERAL ---\n")
                f.write(f"Total de Voluntários Registados: {len(self.voluntarios)}\n")
                f.write(f"Total de Entidades Parceiras: {len(self.entidades)}\n")
                f.write(f"Total de Ações Registadas: {len(self.acoes)}\n\n")

                f.write("--- TOP 3 ODS MAIS ATIVOS ---\n")
                for ods, contagem in top_ods:
                    if contagem > 0:
                        f.write(f" -> ODS {ods}: {contagem} ações\n")

                f.write("\n--- TOP 5 VOLUNTÁRIOS (POR HORAS) ---\n")
                if top_voluntarios:
                    for i, (nome, horas) in enumerate(top_voluntarios, 1):
                        f.write(f" {i}º Lugar: {nome} - {horas}h totais\n")
                else:
                    f.write(" -> Nenhum voluntário tem horas registadas em ações concluídas.\n")

                f.write("\n" + "=" * 50 + "\n")
                f.write("Relatório gerado automaticamente pelo Sistema.\n")

            print(f"\n Sucesso! Relatório exportado com sucesso para a pasta 'relatorios'.")
            print(f" Nome do ficheiro: {nome_ficheiro}")
            
        except Exception as e:
            print(f"Erro ao guardar o relatório: {e}")