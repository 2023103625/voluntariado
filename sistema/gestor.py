import os
import time
import matplotlib.pyplot as plt
from typing import List, Optional, Dict, Any
from sistema.modelos import Voluntario, Entidade, Acao, Inscricao
from sistema.algoritmos.insertion_sort import ordenar_voluntarios_nome
from sistema.algoritmos.merge_sort import merge_sort_acoes
from sistema.base_dados import BaseDados

class SistemaVoluntariado:
    """Classe principal de orquestração do sistema de voluntariado.

    A classe centraliza:

    - gestão de entidades de domínio (voluntários, entidades, ações, inscrições);
    - persistência JSON (carregar/guardar);
    - operações de negócio dos requisitos funcionais (RF01..RF05).
    """

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

    def _gerar_proximo_id(self, itens: List[Any], atributo_id: str, prefixo: str) -> str:
        """Gera o próximo identificador sequencial com prefixo (ex.: V001)."""
        maior = 0
        for item in itens:
            valor_id = getattr(item, atributo_id, None)
            if not isinstance(valor_id, str):
                continue
            if not valor_id.startswith(prefixo):
                continue
            sufixo = valor_id[len(prefixo):]
            if sufixo.isdigit():
                maior = max(maior, int(sufixo))
        return f"{prefixo}{maior + 1:03d}"

    # ==========================================
    # RF01 - GESTÃO DE VOLUNTÁRIOS
    # ==========================================
    def adicionar_voluntario(self, voluntario: Voluntario) -> None:
        """Adiciona um voluntário e atribui ID sequencial.

        :param voluntario: Instância de :class:`Voluntario` a registar.
        """
        if self.consultar_voluntario(voluntario.nome):
            print(f"Erro: O voluntário '{voluntario.nome}' já existe.")
        else:
            voluntario.voluntario_id = self._gerar_proximo_id(
                self.voluntarios,
                "voluntario_id",
                "V",
            )
            self.voluntarios.append(voluntario)
            print(f"Voluntário adicionado com sucesso (ID: {voluntario.voluntario_id}).")

    def consultar_voluntario(self, nome: str) -> Optional[Voluntario]:
        return next((v for v in self.voluntarios if v.nome.lower() == nome.lower()), None)

    def pesquisar_voluntarios(self, termo: str) -> List[Voluntario]:
        termo_normalizado = termo.strip().lower()
        if not termo_normalizado:
            return []
        return [v for v in self.voluntarios if termo_normalizado in v.nome.lower().split()]

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

    def atualizar_voluntario_completo(self, nome: str, campos: Dict[str, Any]) -> bool:
        voluntario = self.consultar_voluntario(nome)
        if not voluntario:
            print("Voluntário não encontrado.")
            return False
        for chave, valor in campos.items():
            setattr(voluntario, chave, valor)
        return True

    # ==========================================
    # RF01 - GESTÃO DE ENTIDADES
    # ==========================================
    def adicionar_entidade(self, entidade: Entidade) -> None:
        """Adiciona uma entidade e atribui ID sequencial.

        :param entidade: Instância de :class:`Entidade` a registar.
        """
        if self.consultar_entidade(entidade.nome):
            print(f"Erro: A entidade '{entidade.nome}' já existe.")
        else:
            entidade.entidade_id = self._gerar_proximo_id(
                self.entidades,
                "entidade_id",
                "E",
            )
            self.entidades.append(entidade)
            print(f"Entidade adicionada com sucesso (ID: {entidade.entidade_id}).")

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

    def atualizar_entidade(
        self,
        nome: str,
        novo_tipo: Optional[str] = None,
        nova_area: Optional[str] = None,
        nova_localizacao: Optional[str] = None,
    ) -> bool:
        """Atualiza campos principais de uma entidade.

        :param nome: Nome atual da entidade a atualizar.
        :param novo_tipo: Novo tipo (opcional).
        :param nova_area: Nova área de intervenção (opcional).
        :param nova_localizacao: Nova localização (opcional).
        :return: ``True`` se a entidade existir, ``False`` caso contrário.
        """
        entidade = self.consultar_entidade(nome)
        if not entidade:
            print("Entidade não encontrada.")
            return False

        if novo_tipo:
            entidade.tipo = novo_tipo
        if nova_area:
            entidade.area = nova_area
        if nova_localizacao:
            entidade.localizacao = nova_localizacao
        print(f"Entidade '{nome}' atualizada com sucesso.")
        return True

    def atualizar_entidade_completo(self, nome: str, campos: Dict[str, Any]) -> bool:
        entidade = self.consultar_entidade(nome)
        if not entidade:
            print("Entidade não encontrada.")
            return False
        for chave, valor in campos.items():
            setattr(entidade, chave, valor)
        return True

    # ==========================================
    # RF01 - GESTÃO DE AÇÕES
    # ==========================================
    def adicionar_acao(self, acao: Acao) -> None:
        """Adiciona uma ação e atribui ID sequencial.

        :param acao: Instância de :class:`Acao` a registar.
        """
        if self.consultar_acao(acao.titulo):
            print(f"Erro: A ação '{acao.titulo}' já existe.")
            return

        entidade = self.consultar_entidade(acao.entidade)
        if not entidade:
            print(
                "Erro: A entidade promotora indicada não existe. "
                "Crie/valide a entidade antes de registar a ação."
            )
        else:
            acao.entidade_id = entidade.entidade_id
            acao.acao_id = self._gerar_proximo_id(
                self.acoes,
                "acao_id",
                "A",
            )
            self.acoes.append(acao)
            print(f"Ação adicionada com sucesso (ID: {acao.acao_id}).")

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

    def atualizar_acao_completo(self, titulo: str, campos: Dict[str, Any]) -> bool:
        acao = self.consultar_acao(titulo)
        if not acao:
            print("Ação não encontrada.")
            return False
        if "entidade" in campos:
            entidade = self.consultar_entidade(campos["entidade"])
            if not entidade:
                print("Entidade promotora inválida.")
                return False
            acao.entidade_id = entidade.entidade_id
        for chave, valor in campos.items():
            setattr(acao, chave, valor)
        return True

    def listar_acoes_com_fila_pendente(self) -> List[Acao]:
        """Retorna uma lista de ações que tenham inscrições por processar."""
        return [a for a in self.acoes if not a.fila_inscricoes.is_empty()]

    def espreitar_proxima_inscricao(self, titulo_acao: str) -> Optional[Inscricao]:
        """Mostra a próxima inscrição da fila sem a remover."""
        acao = self.consultar_acao(titulo_acao)
        if not acao or acao.fila_inscricoes.is_empty():
            return None
            
        assert acao.fila_inscricoes._cabeca is not None
        return acao.fila_inscricoes._cabeca.valor

    # ============================================
    # RF02 – Processamento de inscrições nas ações
    # =============================================
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
            print(
                f"Inscrição aprovada: {inscricao.voluntario}. "
                f"Vagas restantes: {acao.vagas}"
            )
        elif aprovada:
            inscricao.atualizar_estado("lista de espera")
            print(f"Sem vagas! {inscricao.voluntario} foi para lista de espera.")
        else:
            inscricao.atualizar_estado("rejeitada")
            print(f"Inscrição rejeitada: {inscricao.voluntario}.")

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

        # Por fim, ordena os resultados filtrados usando o teu algoritmo Merge Sort
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
        """Desenha os gráficos de barras do dashboard com legibilidade melhorada.

        :param acoes_ods: Dicionário ``{ods: total_acoes}``.
        :param horas_ods: Dicionário ``{ods: total_horas}``.
        """
        if not sum(acoes_ods.values()):
            print("Sem dados.")
            return

        labels_acoes = [f"ODS {k}" for k, v in acoes_ods.items() if v > 0]
        valores_acoes = [v for v in acoes_ods.values() if v > 0]

        labels_horas = [f"ODS {k}" for k, v in horas_ods.items() if v > 0]
        valores_horas = [v for v in horas_ods.values() if v > 0]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        barras1 = ax1.bar(labels_acoes, valores_acoes, color='skyblue', edgecolor='black', linewidth=0.6)
        ax1.set_title('N.º de Ações por ODS')
        ax1.set_ylabel('N.º de Ações')
        ax1.grid(axis='y', linestyle='--', alpha=0.35)
        ax1.tick_params(axis='x', labelrotation=35)
        for barra in barras1:
            altura = barra.get_height()
            ax1.text(
                barra.get_x() + barra.get_width() / 2,
                altura + 0.05,
                f"{int(altura)}",
                ha='center',
                va='bottom',
                fontsize=9,
            )

        barras2 = ax2.bar(labels_horas, valores_horas, color='lightgreen', edgecolor='black', linewidth=0.6)
        ax2.set_title('Horas Totais por ODS')
        ax2.set_ylabel('Horas')
        ax2.grid(axis='y', linestyle='--', alpha=0.35)
        ax2.tick_params(axis='x', labelrotation=35)
        for barra in barras2:
            altura = barra.get_height()
            ax2.text(
                barra.get_x() + barra.get_width() / 2,
                altura + 0.05,
                f"{altura:.1f}" if isinstance(altura, float) else f"{altura}",
                ha='center',
                va='bottom',
                fontsize=9,
            )

        fig.subplots_adjust(bottom=0.22, wspace=0.26)
        plt.show()

    # ==========================================
    # RF05 - REQUISITO OPCIONAL (Exportar Relatório)
    # ==========================================
    
    def exportar_relatorio(self) -> None:
        """
        Gera um ficheiro PDF com o resumo do programa e os gráficos do Dashboard,
        com um design profissional usando o matplotlib (coordenadas absolutas).
        """
        if not self.acoes:
            print("Não há dados suficientes para gerar um relatório.")
            return

        # 1. Recalcular as estatísticas (idêntico ao Dashboard)
        acoes_por_ods = {i: 0 for i in range(1, 18)}
        horas_por_ods = {i: 0 for i in range(1, 18)}
        horas_por_voluntario = {}

        for acao in self.acoes:
            for ods in acao.ods_associados:
                acoes_por_ods[ods] += 1
                
            if acao.estado.lower() == "concluída":
                for ods in acao.ods_associados:
                    horas_por_ods[ods] += acao.duracao
                    
                for inscricao in getattr(acao, 'inscricoes_aprovadas', []):
                    nome_vol = inscricao.voluntario
                    horas_por_voluntario[nome_vol] = horas_por_voluntario.get(nome_vol, 0) + acao.duracao

        top_ods = sorted(acoes_por_ods.items(), key=lambda x: x[1], reverse=True)[:3]
        top_voluntarios = sorted(horas_por_voluntario.items(), key=lambda x: x[1], reverse=True)[:5]

        # 2. Setup do ficheiro
        os.makedirs("relatorios", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        data_formatada = time.strftime('%d/%m/%Y %H:%M:%S')
        nome_ficheiro = os.path.join("relatorios", f"relatorio_oficial_{timestamp}.pdf")

        # 3. Desenhar o PDF Profissional com Matplotlib
        try:
            from matplotlib.backends.backend_pdf import PdfPages
            
            # Criar a figura em proporção A4
            fig = plt.figure(figsize=(8.27, 11.69))
            
            # Paleta de Cores
            cor_primaria = '#005b96'
            cor_texto = '#333333'
            
            # --- CABEÇALHO ---
            fig.text(0.5, 0.93, "RELATÓRIO DE VOLUNTARIADO (AED)", ha='center', va='center', 
                     fontsize=18, fontweight='bold', color=cor_primaria)
            fig.text(0.5, 0.90, f"Documento gerado a: {data_formatada}", ha='center', va='center', 
                     fontsize=10, color='gray', style='italic')
            
            # Linha decorativa
            ax_line = fig.add_axes([0.1, 0.88, 0.8, 0.01])
            ax_line.axis('off')
            ax_line.plot([0, 1], [0, 0], color=cor_primaria, lw=2)
            
            # --- RESUMO GERAL ---
            fig.text(0.1, 0.83, "RESUMO GERAL", ha='left', va='center', fontsize=12, fontweight='bold', color=cor_primaria)
            
            fig.text(0.25, 0.77, str(len(self.voluntarios)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
            fig.text(0.25, 0.73, "Voluntários\nRegistados", ha='center', va='top', fontsize=10, color=cor_texto)
            
            fig.text(0.5, 0.77, str(len(self.entidades)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
            fig.text(0.5, 0.73, "Entidades\nParceiras", ha='center', va='top', fontsize=10, color=cor_texto)
            
            fig.text(0.75, 0.77, str(len(self.acoes)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
            fig.text(0.75, 0.73, "Ações\nRegistadas", ha='center', va='top', fontsize=10, color=cor_texto)
            
            # --- GRÁFICOS NO PDF ---
            
            # Gráfico 1: Ações por ODS
            ax1 = fig.add_axes([0.1, 0.45, 0.35, 0.20]) # [esquerda, base, largura, altura]
            
            # ATUALIZAÇÃO: Guardar apenas o número do ODS (ex: "4" em vez de "ODS 4") para poupar espaço
            labels_acoes = [str(k) for k, v in acoes_por_ods.items() if v > 0]
            valores_acoes = [v for v in acoes_por_ods.values() if v > 0]
            
            if labels_acoes:
                barras1 = ax1.bar(labels_acoes, valores_acoes, color='skyblue', edgecolor='black', linewidth=0.5)
                ax1.set_title('N.º de Ações por ODS', fontsize=9, fontweight='bold', color=cor_primaria)
                ax1.set_xlabel('ODS', fontsize=8) # Título do eixo X
                ax1.tick_params(axis='x', labelsize=8) # Rotação removida pois só temos números
                ax1.tick_params(axis='y', labelsize=8)
                ax1.grid(axis='y', linestyle='--', alpha=0.35) # Adiciona grelha horizontal
                
                # ATUALIZAÇÃO: Adicionar o valor numérico exato no topo de cada barra
                for barra in barras1:
                    altura = barra.get_height()
                    ax1.text(barra.get_x() + barra.get_width() / 2, altura + (max(valores_acoes) * 0.02),
                             f"{int(altura)}", ha='center', va='bottom', fontsize=7)
            else:
                ax1.axis('off')
                ax1.text(0.5, 0.5, "Sem dados de ODS", ha='center', va='center', fontsize=9)

            # Gráfico 2: Horas por ODS
            ax2 = fig.add_axes([0.55, 0.45, 0.35, 0.20])
            
            # ATUALIZAÇÃO: Guardar apenas o número do ODS
            labels_horas = [str(k) for k, v in horas_por_ods.items() if v > 0]
            valores_horas = [v for v in horas_por_ods.values() if v > 0]
            
            if labels_horas:
                barras2 = ax2.bar(labels_horas, valores_horas, color='lightgreen', edgecolor='black', linewidth=0.5)
                ax2.set_title('Horas Totais por ODS', fontsize=9, fontweight='bold', color=cor_primaria)
                ax2.set_xlabel('ODS', fontsize=8)
                ax2.tick_params(axis='x', labelsize=8)
                ax2.tick_params(axis='y', labelsize=8)
                ax2.grid(axis='y', linestyle='--', alpha=0.35)
                
                # ATUALIZAÇÃO: Adicionar o valor no topo de cada barra
                for barra in barras2:
                    altura = barra.get_height()
                    texto_altura = f"{altura:.1f}" if isinstance(altura, float) and not altura.is_integer() else f"{int(altura)}"
                    ax2.text(barra.get_x() + barra.get_width() / 2, altura + (max(valores_horas) * 0.02),
                             texto_altura, ha='center', va='bottom', fontsize=7)
            else:
                ax2.axis('off')
                ax2.text(0.5, 0.5, "Sem horas registadas", ha='center', va='center', fontsize=9)

            # --- LISTAGENS (TOP 3 e TOP 5) ---
            fig.text(0.1, 0.33, "TOP 3 ODS MAIS ATIVOS", ha='left', va='center', fontsize=11, fontweight='bold', color=cor_primaria)
            y_pos = 0.29
            if top_ods and top_ods[0][1] > 0:
                for ods, contagem in top_ods:
                    if contagem > 0:
                        fig.text(0.1, y_pos, f"• ODS {ods}: {contagem} ações", ha='left', va='center', fontsize=10, color=cor_texto)
                        y_pos -= 0.03
            else:
                fig.text(0.1, y_pos, "Sem ações registadas.", ha='left', va='center', fontsize=10, color=cor_texto)

            fig.text(0.55, 0.33, "TOP 5 VOLUNTÁRIOS (POR HORAS)", ha='left', va='center', fontsize=11, fontweight='bold', color=cor_primaria)
            y_pos = 0.29
            if top_voluntarios:
                for i, (nome, horas) in enumerate(top_voluntarios, 1):
                    fig.text(0.55, y_pos, f"{i}º Lugar: {nome} - {horas}h totais", ha='left', va='center', fontsize=10, color=cor_texto)
                    y_pos -= 0.03
            else:
                fig.text(0.55, y_pos, "Nenhum voluntário com horas validadas.", ha='left', va='center', fontsize=10, color=cor_texto)

            # --- RODAPÉ ---
            fig.text(0.5, 0.05, "Relatório gerado automaticamente pelo Sistema de Voluntariado (Projeto AED)", 
                     ha='center', va='center', fontsize=8, color='gray')

            # Fechar e Guardar
            with PdfPages(nome_ficheiro) as pdf:
                pdf.savefig(fig)
            plt.close(fig)

            print(f"\n Sucesso! Relatório visual exportado com sucesso para a pasta 'relatorios'.")
            print(f" Nome do ficheiro: {nome_ficheiro}")
            
        except Exception as e:
            print(f"Erro ao guardar o relatório: {e}")