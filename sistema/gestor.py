import os
import time
import matplotlib.pyplot as plt
from typing import List, Optional, Dict, Any
from sistema.modelos import Voluntario, Entidade, Acao, Inscricao
from sistema.algoritmos.insertion_sort import ordenar_voluntarios_nome
from sistema.algoritmos.merge_sort import merge_sort_acoes
from sistema.base_dados import BaseDados

class SistemaVoluntariado:
    """Classe principal que gere todo o programa de voluntariado."""

    def __init__(self):
        self.voluntarios: List[Voluntario] = []
        self.entidades: List[Entidade] = []
        self.acoes: List[Acao] = []
        self.ods_catalogo: List[Dict[str, Any]] = []
        self.inscricoes: List[Inscricao] = []
        self.presencas: List[Dict[str, Any]] = []

    # ==========================================
    # OR02 - LEITURA E ESCRITA DE DADOS (JSON)
    # ==========================================
    
    def carregar_sistema(self, caminho_json: str) -> None:
        """Carrega os dados iniciais para as listas de objetos (OR02)."""
        if os.path.isdir(caminho_json):
            dados = self._carregar_de_pasta_json(caminho_json)
        else:
            dados = BaseDados.carregar_dados(caminho_json)

            # Fallback: se dataset_completo estiver vazio/incompleto,
            # tenta reconstruir a partir dos ficheiros separados.
            pasta = os.path.dirname(caminho_json)
            if (
                os.path.basename(caminho_json) == "dataset_completo.json"
                and (
                    not dados.get("acoes")
                    or not dados.get("voluntarios")
                    or not dados.get("entidades")
                )
            ):
                dados_pasta = self._carregar_de_pasta_json(pasta)
                if dados_pasta.get("voluntarios") or dados_pasta.get("entidades") or dados_pasta.get("acoes"):
                    dados = dados_pasta

        if not dados:
            print("Iniciando o sistema com a base de dados vazia.")
            return

        self.voluntarios = [self._desserializar_voluntario(v) for v in dados.get("voluntarios", [])]
        self.entidades = [self._desserializar_entidade(e) for e in dados.get("entidades", [])]
        self.acoes = [self._desserializar_acao(a) for a in dados.get("acoes", [])]
        self.ods_catalogo = dados.get("ods_catalogo", [])
        self.presencas = dados.get("presencas", [])
        self.inscricoes = []
        self._reconstruir_inscricoes(dados.get("inscricoes", []))
        print("Base de dados JSON encontrada e carregada com sucesso.")

    def guardar_sistema(self, caminho_json: str) -> None:
        """Guarda as listas de objetos de volta no JSON (OR02)."""
        dados_exportar = {
            "voluntarios": [self._serializar_voluntario(v) for v in self.voluntarios],
            "entidades": [self._serializar_entidade(e) for e in self.entidades],
            "acoes": [self._serializar_acao(a) for a in self.acoes],
            "ods_catalogo": self.ods_catalogo,
            "inscricoes": [self._serializar_inscricao(i) for i in self.inscricoes],
            "presencas": self.presencas,
        }
        if os.path.isdir(caminho_json):
            self._guardar_em_pasta_json(caminho_json, dados_exportar)
            return
        BaseDados.guardar_dados(caminho_json, dados_exportar)

    def _carregar_de_pasta_json(self, pasta_json: str) -> Dict[str, Any]:
        """Carrega dados dos ficheiros JSON separados na pasta de dados."""
        voluntarios = BaseDados.carregar_dados(os.path.join(pasta_json, "voluntarios.json"))
        entidades = BaseDados.carregar_dados(os.path.join(pasta_json, "entidades.json"))
        acoes = BaseDados.carregar_dados(os.path.join(pasta_json, "acoes.json"))
        ods_catalogo = BaseDados.carregar_dados(os.path.join(pasta_json, "ods_catalogo.json"))
        inscricoes = BaseDados.carregar_dados(os.path.join(pasta_json, "inscricoes.json"))
        presencas = BaseDados.carregar_dados(os.path.join(pasta_json, "presencas.json"))

        if not isinstance(voluntarios, list):
            voluntarios = []
        if not isinstance(entidades, list):
            entidades = []
        if not isinstance(acoes, list):
            acoes = []
        if not isinstance(ods_catalogo, list):
            ods_catalogo = []
        if not isinstance(inscricoes, list):
            inscricoes = []
        if not isinstance(presencas, list):
            presencas = []

        return {
            "voluntarios": voluntarios,
            "entidades": entidades,
            "acoes": acoes,
            "ods_catalogo": ods_catalogo,
            "inscricoes": inscricoes,
            "presencas": presencas,
        }

    def _guardar_em_pasta_json(self, pasta_json: str, dados_exportar: Dict[str, Any]) -> None:
        """Guarda dados nos ficheiros JSON individuais e no consolidado."""
        BaseDados.guardar_dados(os.path.join(pasta_json, "voluntarios.json"), dados_exportar["voluntarios"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "entidades.json"), dados_exportar["entidades"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "acoes.json"), dados_exportar["acoes"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "ods_catalogo.json"), dados_exportar["ods_catalogo"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "inscricoes.json"), dados_exportar["inscricoes"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "presencas.json"), dados_exportar["presencas"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "dataset_completo.json"), dados_exportar)

    def _serializar_voluntario(self, voluntario: Voluntario) -> Dict[str, Any]:
        """Converte um objeto Voluntario para dicionário JSON-serializável."""
        return {
            "voluntario_id": getattr(voluntario, "voluntario_id", None),
            "nome": voluntario.nome,
            "curso": voluntario.curso,
            "faculdade": voluntario.faculdade,
            "vinculo_institucional": voluntario.vinculo,
            "ano": voluntario.ano,
            "competencias": [
                {"competencia": nome, "nivel": nivel}
                for nome, nivel in voluntario.competencias.items()
            ],
            "interesses": voluntario.interesses,
            "ods_interesse": voluntario.ods_interesse,
        }

    def _serializar_entidade(self, entidade: Entidade) -> Dict[str, Any]:
        """Converte um objeto Entidade para dicionário JSON-serializável."""
        return {
            "entidade_id": getattr(entidade, "entidade_id", None),
            "nome": entidade.nome,
            "tipo": entidade.tipo,
            "area_intervencao": entidade.area,
            "localizacao": entidade.localizacao,
            "url": entidade.url,
            "tags": entidade.tags,
            "ods_principais": [{"ods_id": ods} for ods in entidade.ods_foco],
        }

    def _serializar_acao(self, acao: Acao) -> Dict[str, Any]:
        """Converte um objeto Acao para dicionário JSON-serializável."""
        return {
            "acao_id": getattr(acao, "acao_id", None),
            "titulo": acao.titulo,
            "entidade_id": getattr(acao, "entidade_id", None),
            "entidade_nome": acao.entidade,
            "area": acao.area,
            "data_hora": acao.data_hora,
            "duracao_horas": acao.duracao,
            "vagas": acao.vagas,
            "localizacao": acao.localizacao,
            "estado": acao.estado,
            "metrica_impacto": acao.metrica_impacto,
            "competencias_desejadas": [
                {"competencia": nome, "nivel_minimo": nivel}
                for nome, nivel in acao.competencias_desejadas.items()
            ],
            "ods_associados": [{"ods_id": ods} for ods in acao.ods_associados],
        }

    def _serializar_inscricao(self, inscricao: Inscricao) -> Dict[str, Any]:
        """Converte uma inscrição para dicionário serializável."""
        return {
            "inscricao_id": getattr(inscricao, "inscricao_id", None),
            "voluntario_id": getattr(inscricao, "voluntario_id", None),
            "acao_id": getattr(inscricao, "acao_id", None),
            "data_hora_inscricao": inscricao.data_hora_inscricao,
            "estado": inscricao.estado,
        }

    def _desserializar_voluntario(self, dados: Dict[str, Any]) -> Voluntario:
        """Converte um dicionário para objeto Voluntario."""
        voluntario = Voluntario(
            nome=dados.get("nome", ""),
            curso=dados.get("curso", ""),
            faculdade=dados.get("faculdade", ""),
            vinculo=dados.get("vinculo_institucional", dados.get("vinculo", "")),
            ano=dados.get("ano"),
        )
        voluntario.voluntario_id = dados.get("voluntario_id")
        competencias = dados.get("competencias", {})
        if isinstance(competencias, list):
            voluntario.competencias = {
                c.get("competencia", ""): c.get("nivel", 0) for c in competencias
            }
        else:
            voluntario.competencias = competencias
        voluntario.interesses = dados.get("interesses", [])
        voluntario.ods_interesse = dados.get("ods_interesse", [])
        return voluntario

    def _desserializar_entidade(self, dados: Dict[str, Any]) -> Entidade:
        """Converte um dicionário para objeto Entidade."""
        entidade = Entidade(
            nome=dados.get("nome", ""),
            tipo=dados.get("tipo", ""),
            area=dados.get("area_intervencao", dados.get("area", "")),
            localizacao=dados.get("localizacao", ""),
            url=dados.get("url"),
        )
        entidade.entidade_id = dados.get("entidade_id")
        entidade.tags = dados.get("tags", [])
        ods_principais = dados.get("ods_principais", dados.get("ods_foco", []))
        if ods_principais and isinstance(ods_principais[0], dict):
            entidade.ods_foco = [item.get("ods_id") for item in ods_principais if item.get("ods_id")]
        else:
            entidade.ods_foco = ods_principais
        return entidade

    def _desserializar_acao(self, dados: Dict[str, Any]) -> Acao:
        """Converte um dicionário para objeto Acao."""
        acao = Acao(
            titulo=dados.get("titulo", ""),
            entidade=dados.get("entidade_nome", dados.get("entidade", "")),
            data_hora=dados.get("data_hora", ""),
            duracao=dados.get("duracao_horas", dados.get("duracao", 0)),
            vagas=dados.get("vagas", 0),
            localizacao=dados.get("localizacao", ""),
            area=dados.get("area", ""),
        )
        acao.acao_id = dados.get("acao_id")
        acao.entidade_id = dados.get("entidade_id")
        acao.estado = dados.get("estado", "planeada")
        acao.metrica_impacto = dados.get("metrica_impacto", 0.0)
        comp = dados.get("competencias_desejadas", {})
        if isinstance(comp, list):
            acao.competencias_desejadas = {
                c.get("competencia", ""): c.get("nivel_minimo", 0) for c in comp
            }
        else:
            acao.competencias_desejadas = comp
        ods = dados.get("ods_associados", [])
        if ods and isinstance(ods[0], dict):
            acao.ods_associados = [item.get("ods_id") for item in ods if item.get("ods_id")]
        else:
            acao.ods_associados = ods
        return acao

    def _reconstruir_inscricoes(self, inscricoes_dados: List[Dict[str, Any]]) -> None:
        """Reconstrói inscrições e liga-as às ações corretas (fila/aprovadas)."""
        voluntarios_por_id = {
            getattr(v, "voluntario_id", None): v for v in self.voluntarios if getattr(v, "voluntario_id", None)
        }
        acoes_por_id = {
            getattr(a, "acao_id", None): a for a in self.acoes if getattr(a, "acao_id", None)
        }

        for item in inscricoes_dados:
            voluntario_id = item.get("voluntario_id")
            acao_id = item.get("acao_id")
            acao = acoes_por_id.get(acao_id)
            voluntario = voluntarios_por_id.get(voluntario_id)
            if not acao:
                continue

            nome_voluntario = voluntario.nome if voluntario else voluntario_id
            inscricao = Inscricao(
                voluntario=nome_voluntario,
                acao=acao.titulo,
                data_hora_inscricao=item.get("data_hora_inscricao", ""),
            )
            inscricao.inscricao_id = item.get("inscricao_id")
            inscricao.voluntario_id = voluntario_id
            inscricao.acao_id = acao_id
            inscricao.atualizar_estado(item.get("estado", "pendente"))
            self.inscricoes.append(inscricao)

            if inscricao.estado == "pendente":
                acao.fila_inscricoes.enqueue(inscricao)
            elif inscricao.estado == "aprovada":
                acao.inscricoes_aprovadas.append(inscricao)

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
        resultado final usando o algoritmo Merge Sort (O(n log n)).
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

        # Por fim, ordena os resultados filtrados usando o algoritmo
        merge_sort_acoes(resultados, ordenar_por)

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