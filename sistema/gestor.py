import os
import time
import csv
import matplotlib.pyplot as plt
from typing import List, Optional, Dict, Any, Tuple
from sistema.modelos import Voluntario, Entidade, Acao, Inscricao
from sistema.algoritmos.insertion_sort import ordenar_voluntarios_nome
from sistema.algoritmos.merge_sort import merge_sort_acoes
from sistema.base_dados import BaseDados
from sistema.estruturas.bst import BST
from sistema.estruturas.heap import MaxHeap

class SistemaVoluntariado:
    """Classe principal de orquestração do sistema de voluntariado.

    A classe centraliza:

    - gestão de entidades de domínio (voluntários, entidades, ações, inscrições);
    - persistência JSON (carregar/guardar);
    - operações de negócio dos requisitos funcionais (RF01..RF09).
    """

    def __init__(self):
        """Inicializa as estruturas de dados centrais do Gestor.
        
        Utilizam-se Listas (List) em vez de Conjuntos (Set) nas coleções 
        principais porque:
        1. Necessito manter a ordem cronológica de inserção.
        2. Necessito aceder aos elementos por índice para os algoritmos de ordenação (Merge Sort e Insertion Sort).
        """
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
            "interesses": list(voluntario.interesses),
            "ods_interesse": list(voluntario.ods_interesse),
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
            "tags": list(entidade.tags),
            "ods_principais": [{"ods_id": ods} for ods in entidade.ods_foco],
        }

    def _serializar_acao(self, acao: Acao) -> Dict[str, Any]:
        """Converte um objeto Acao para dicionário JSON-serializável."""
        
        # 1. Preparar o histórico da pilha para ser guardado no JSON
        historico_formatado = []
        for reg in acao.historico_equipa.para_lista():
            historico_formatado.append({
                # O JSON não suporta Set, logo convertemos para list()
                "estado_anterior": list(reg["estado_anterior"]),
                "estado_novo": list(reg["estado_novo"]),
                "data_hora": reg["data_hora"],
                "tipo": reg["tipo"]
            })
            
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
            "equipa": list(getattr(acao, "equipa", set())),
            "historico_equipa": historico_formatado,
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
        """Converte um dicionário JSON para um objeto Voluntario."""
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
            
        voluntario.interesses = set(dados.get("interesses", []))
        
        ods = dados.get("ods_interesse", [])
        if ods and isinstance(ods[0], dict):
            voluntario.ods_interesse = set(item.get("ods_id") for item in ods if item.get("ods_id"))
        else:
            voluntario.ods_interesse = set(ods)
            
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
        entidade.tags = set(dados.get("tags", []))
        
        ods_principais = dados.get("ods_principais", dados.get("ods_foco", []))
        if ods_principais and isinstance(ods_principais[0], dict):
            entidade.ods_foco = set(item.get("ods_id") for item in ods_principais if item.get("ods_id"))
        else:
            entidade.ods_foco = set(ods_principais)
        return entidade

    def _desserializar_acao(self, dados: Dict[str, Any]) -> Acao:
        """Converte um dicionário JSON para objeto Acao e reconstrói as estruturas complexas."""
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
            acao.ods_associados = set(item.get("ods_id") for item in ods if item.get("ods_id"))
        else:
            acao.ods_associados = set(ods)
            
        acao.equipa = set(dados.get("equipa", []))
        
        # 2. Reconstruir a Pilha (Histórico)
        historico_salvo = dados.get("historico_equipa", [])
        # Como o JSON guardou do [Mais Recente -> Mais Antigo],
        # temos de inverter a lista (reversed) para empurrar primeiro o mais antigo
        # e reconstruir a Pilha perfeitamente!
        for reg in reversed(historico_salvo):
            acao.historico_equipa.push({
                # Reverter as listas de volta para Sets
                "estado_anterior": set(reg.get("estado_anterior", [])),
                "estado_novo": set(reg.get("estado_novo", [])),
                "data_hora": reg.get("data_hora", ""),
                "tipo": reg.get("tipo", "")
            })
            
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
        return [a for a in self.acoes if not a.fila_inscricoes.is_empty()]

    def espreitar_proxima_inscricao(self, titulo_acao: str) -> Optional[Inscricao]:
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
        resultados = self.acoes.copy()

        if filtros.get("entidade"):
            resultados = [a for a in resultados if filtros["entidade"].lower() in a.entidade.lower()]
        if filtros.get("area"):
            resultados = [a for a in resultados if filtros["area"].lower() in a.area.lower()]

        data_inicio = filtros.get("data_inicio")
        data_fim = filtros.get("data_fim")
        if data_inicio:
            resultados = [a for a in resultados if a.data_hora >= data_inicio]
        if data_fim:
            resultados = [a for a in resultados if a.data_hora <= data_fim]
            
        if filtros.get("vagas_min") is not None:
            resultados = [a for a in resultados if a.vagas >= filtros["vagas_min"]]
            
        if filtros.get("ods") is not None:
            resultados = [a for a in resultados if filtros["ods"] in a.ods_associados]

        if not resultados:
            print("\nNenhuma ação encontrada com os filtros especificados.")
            return

        merge_sort_acoes(resultados, ordenar_por)

        print(f"\n--- Resultados da Pesquisa ({len(resultados)} encontradas) ---")
        for a in resultados:
            print(f"[{getattr(a, ordenar_por)}] {a.titulo} (Entidade: {a.entidade}) - Vagas: {a.vagas}")

    def gerar_dashboard(self) -> None:
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
                    if nome_vol not in horas_por_voluntario:
                        horas_por_voluntario[nome_vol] = 0
                    horas_por_voluntario[nome_vol] += acao.duracao

        print("\n" + "="*50)
        print("   DASHBOARD E ESTATÍSTICAS DO PROGRAMA   ")
        print("="*50)
        
        print("\n[AÇÕES POR ODS - TOP 3]")
        top_ods = sorted(acoes_por_ods.items(), key=lambda x: x[1], reverse=True)[:3]
        for ods, contagem in top_ods:
            if contagem > 0:
                print(f" - ODS {ods}: {contagem} ações")

        print("\n[TOP 5 VOLUNTÁRIOS POR HORAS]")
        top_voluntarios = sorted(horas_por_voluntario.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_voluntarios:
            for i, (nome, horas) in enumerate(top_voluntarios, 1):
                print(f" {i}º Lugar: {nome} - {horas} horas totais")
        else:
            print(" -> Nenhum voluntário tem horas registadas em ações concluídas.")
        print("="*50)

        self._desenhar_graficos(acoes_por_ods, horas_por_ods)

    def _desenhar_graficos(self, acoes_ods: dict, horas_ods: dict) -> None:
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

    def exportar_relatorio(self) -> None:
        if not self.acoes:
            print("Não há dados suficientes para gerar um relatório.")
            return

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

        os.makedirs("relatorios", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        data_formatada = time.strftime('%d/%m/%Y %H:%M:%S')
        nome_ficheiro = os.path.join("relatorios", f"relatorio_oficial_{timestamp}.pdf")

        try:
            from matplotlib.backends.backend_pdf import PdfPages
            
            fig = plt.figure(figsize=(8.27, 11.69))
            cor_primaria = '#005b96'
            cor_texto = '#333333'
            
            fig.text(0.5, 0.93, "RELATÓRIO DE VOLUNTARIADO (AED)", ha='center', va='center', 
                     fontsize=18, fontweight='bold', color=cor_primaria)
            fig.text(0.5, 0.90, f"Documento gerado a: {data_formatada}", ha='center', va='center', 
                     fontsize=10, color='gray', style='italic')
            
            ax_line = fig.add_axes([0.1, 0.88, 0.8, 0.01])
            ax_line.axis('off')
            ax_line.plot([0, 1], [0, 0], color=cor_primaria, lw=2)
            
            fig.text(0.1, 0.83, "RESUMO GERAL", ha='left', va='center', fontsize=12, fontweight='bold', color=cor_primaria)
            
            fig.text(0.25, 0.77, str(len(self.voluntarios)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
            fig.text(0.25, 0.73, "Voluntários\nRegistados", ha='center', va='top', fontsize=10, color=cor_texto)
            
            fig.text(0.5, 0.77, str(len(self.entidades)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
            fig.text(0.5, 0.73, "Entidades\nParceiras", ha='center', va='top', fontsize=10, color=cor_texto)
            
            fig.text(0.75, 0.77, str(len(self.acoes)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
            fig.text(0.75, 0.73, "Ações\nRegistadas", ha='center', va='top', fontsize=10, color=cor_texto)
            
            ax1 = fig.add_axes([0.1, 0.45, 0.35, 0.20])
            
            labels_acoes = [str(k) for k, v in acoes_por_ods.items() if v > 0]
            valores_acoes = [v for v in acoes_por_ods.values() if v > 0]
            
            if labels_acoes:
                barras1 = ax1.bar(labels_acoes, valores_acoes, color='skyblue', edgecolor='black', linewidth=0.5)
                ax1.set_title('N.º de Ações por ODS', fontsize=9, fontweight='bold', color=cor_primaria)
                ax1.set_xlabel('ODS', fontsize=8) 
                ax1.tick_params(axis='x', labelsize=8)
                ax1.tick_params(axis='y', labelsize=8)
                ax1.grid(axis='y', linestyle='--', alpha=0.35) 
                
                for barra in barras1:
                    altura = barra.get_height()
                    ax1.text(barra.get_x() + barra.get_width() / 2, altura + (max(valores_acoes) * 0.02),
                             f"{int(altura)}", ha='center', va='bottom', fontsize=7)
            else:
                ax1.axis('off')
                ax1.text(0.5, 0.5, "Sem dados de ODS", ha='center', va='center', fontsize=9)

            ax2 = fig.add_axes([0.55, 0.45, 0.35, 0.20])
            
            labels_horas = [str(k) for k, v in horas_por_ods.items() if v > 0]
            valores_horas = [v for v in horas_por_ods.values() if v > 0]
            
            if labels_horas:
                barras2 = ax2.bar(labels_horas, valores_horas, color='lightgreen', edgecolor='black', linewidth=0.5)
                ax2.set_title('Horas Totais por ODS', fontsize=9, fontweight='bold', color=cor_primaria)
                ax2.set_xlabel('ODS', fontsize=8)
                ax2.tick_params(axis='x', labelsize=8)
                ax2.tick_params(axis='y', labelsize=8)
                ax2.grid(axis='y', linestyle='--', alpha=0.35)
                
                for barra in barras2:
                    altura = barra.get_height()
                    texto_altura = f"{altura:.1f}" if isinstance(altura, float) and not altura.is_integer() else f"{int(altura)}"
                    ax2.text(barra.get_x() + barra.get_width() / 2, altura + (max(valores_horas) * 0.02),
                             texto_altura, ha='center', va='bottom', fontsize=7)
            else:
                ax2.axis('off')
                ax2.text(0.5, 0.5, "Sem horas registadas", ha='center', va='center', fontsize=9)

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

            fig.text(0.5, 0.05, "Relatório gerado automaticamente pelo Sistema de Voluntariado (Projeto AED)", 
                     ha='center', va='center', fontsize=8, color='gray')

            with PdfPages(nome_ficheiro) as pdf:
                pdf.savefig(fig)
            plt.close(fig)

            print(f"\n Sucesso! Relatório visual exportado com sucesso para a pasta 'relatorios'.")
            print(f" Nome do ficheiro: {nome_ficheiro}")
            
        except Exception as e:
            print(f"Erro ao guardar o relatório: {e}")

    def exportar_relatorio_csv(self) -> None:
        """Gera um ficheiro CSV tabular com os dados de todas as Ações (RF05)."""
        if not self.acoes:
            print("Não há dados suficientes para gerar um relatório CSV.")
            return

        os.makedirs("relatorios", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nome_ficheiro = os.path.join("relatorios", f"relatorio_dados_{timestamp}.csv")

        try:
            # O parâmetro newline='' previne linhas em branco extra no Windows
            # O encoding='utf-8-sig' garante que o Excel lê os acentos de português corretamente!
            with open(nome_ficheiro, mode='w', newline='', encoding='utf-8-sig') as ficheiro_csv:
                # Usamos o delimitador ';' que é o padrão para o Excel em português
                writer = csv.writer(ficheiro_csv, delimiter=';')
                
                # 1. Escrever o Cabeçalho da Tabela
                writer.writerow([
                    "ID da Ação", 
                    "Título", 
                    "Entidade Promotora", 
                    "Área Temática", 
                    "Data e Hora", 
                    "Duração (Horas)", 
                    "Vagas Restantes", 
                    "Estado Atual", 
                    "Métrica de Impacto", 
                    "Voluntários Aprovados"
                ])
                
                # 2. Escrever os dados de cada Ação, linha a linha
                for acao in self.acoes:
                    # Quantos voluntários já estão aprovados nesta ação?
                    num_aprovados = len(getattr(acao, 'inscricoes_aprovadas', []))
                    
                    writer.writerow([
                        getattr(acao, "acao_id", ""),
                        acao.titulo,
                        acao.entidade,
                        acao.area,
                        acao.data_hora,
                        acao.duracao,
                        acao.vagas,
                        acao.estado.capitalize(),
                        acao.metrica_impacto,
                        num_aprovados
                    ])
                    
            print(f"\n Sucesso! Dados tabulares exportados com sucesso para CSV.")
            print(f" Nome do ficheiro: {nome_ficheiro}")
            
        except Exception as e:
            print(f"Erro ao guardar o relatório CSV: {e}")

    # ==========================================
    # RF06 - FORMAÇÃO DE EQUIPAS (PILHA / UNDO)
    # ==========================================
    
    def adequacao_voluntario_acao(self, voluntario: Voluntario, acao: Acao) -> bool:
        ods_em_comum = voluntario.ods_interesse.intersection(acao.ods_associados)
        comps_voluntario = set(voluntario.competencias.keys())
        comps_acao = set(acao.competencias_desejadas.keys())
        comps_em_comum = comps_voluntario.intersection(comps_acao)
        
        if ods_em_comum or comps_em_comum:
            return True
        return False

    def adicionar_voluntario_equipa(self, titulo_acao: str, voluntario_nome: str) -> Tuple[bool, str]:
        """Adiciona um voluntário à equipa e regista a ação detalhada na Pilha."""
        acao = self.consultar_acao(titulo_acao)
        voluntario = self.consultar_voluntario(voluntario_nome)
        
        if not acao: return False, "Ação não encontrada."
        if not voluntario: return False, "Voluntário não encontrado."
        if voluntario.nome in acao.equipa: return False, "O voluntário já pertence a esta equipa."
        if not self.adequacao_voluntario_acao(voluntario, acao): return False, "Perfil não se adequa à ação."
            
        # 1. Guardamos o estado antigo antes de alterar
        estado_antigo = set(acao.equipa)
        
        # 2. Fazemos a alteração
        acao.equipa.add(voluntario.nome)
        
        # 3. PUSH: Guardamos o registo na Pilha com o nome específico do voluntário
        agora = time.strftime('%Y-%m-%d %H:%M:%S')
        acao.historico_equipa.push({
            "estado_anterior": estado_antigo,
            "estado_novo": set(acao.equipa),
            "data_hora": agora,
            "tipo": f"Adição: {voluntario.nome}" 
        })
        
        return True, f"{voluntario.nome} foi adicionado à equipa."

    def remover_voluntario_equipa(self, titulo_acao: str, voluntario_nome: str) -> Tuple[bool, str]:
        """Remove um voluntário da equipa e regista a ação detalhada na Pilha."""
        acao = self.consultar_acao(titulo_acao)
        if not acao: return False, "Ação não encontrada."
        if voluntario_nome not in acao.equipa: return False, "O voluntário não pertence a esta equipa."
            
        estado_antigo = set(acao.equipa)
        acao.equipa.remove(voluntario_nome)
        
        agora = time.strftime('%Y-%m-%d %H:%M:%S')
        acao.historico_equipa.push({
            "estado_anterior": estado_antigo,
            "estado_novo": set(acao.equipa),
            "data_hora": agora,
            # --- AQUI ESTÁ A MELHORIA ---
            "tipo": f"Remoção: {voluntario_nome}"
        })
        
        return True, f"{voluntario_nome} foi removido da equipa."

    def desfazer_alteracao_equipa(self, titulo_acao: str) -> Tuple[bool, str]:
        acao = self.consultar_acao(titulo_acao)
        if not acao: return False, "Ação não encontrada."
        if acao.historico_equipa.is_empty(): return False, "Não existem alterações anteriores para desfazer nesta sessão."
            
        # POP: O Undo recupera o registo e restaura apenas o 'estado_anterior'
        registro = acao.historico_equipa.pop()
        acao.equipa = registro["estado_anterior"]
        return True, "A última alteração à equipa foi desfeita com sucesso."
    
    # ==========================================
    # RF07 - CONSULTA DE AÇÕES POR IMPACTO (BST)
    # ==========================================
    
    def _construir_bst_impacto(self) -> BST:
        arvore = BST()
        for acao in self.acoes:
            arvore.inserir(acao.metrica_impacto, acao)
        return arvore

    def consultar_acoes_por_impacto_ordem(self, crescente: bool = True) -> List[Acao]:
        arvore = self._construir_bst_impacto()
        acoes_ordenadas = arvore.listar_em_ordem()
        if not crescente:
            acoes_ordenadas.reverse()
        return acoes_ordenadas

    def consultar_acoes_impacto_exato(self, impacto_alvo: float) -> List[Acao]:
        arvore = self._construir_bst_impacto()
        no_atual = arvore.raiz
        while no_atual is not None:
            if impacto_alvo == no_atual.chave:
                return no_atual.valores
            elif impacto_alvo < no_atual.chave:
                no_atual = no_atual.esquerda
            else:
                no_atual = no_atual.direita
        return []

    def consultar_acoes_impacto_extremos(self) -> Tuple[List[Acao], List[Acao]]:
        arvore = self._construir_bst_impacto()
        if arvore.raiz is None:
            return [], []
            
        no_min = arvore.raiz
        while no_min.esquerda is not None:
            no_min = no_min.esquerda
            
        no_max = arvore.raiz
        while no_max.direita is not None:
            no_max = no_max.direita
            
        return no_min.valores, no_max.valores

    def consultar_acoes_por_impacto_intervalo(self, min_imp: float, max_imp: float) -> List[Acao]:
        arvore = self._construir_bst_impacto()
        resultados = []
        
        def _busca_intervalo(no):
            if no is None:
                return
            if no.chave > min_imp:
                _busca_intervalo(no.esquerda)
            if min_imp <= no.chave <= max_imp:
                resultados.extend(no.valores)
            if no.chave < max_imp:
                _busca_intervalo(no.direita)
                
        _busca_intervalo(arvore.raiz)
        return resultados

    # ==================================================
    # RF08 - PRIORIZAÇÃO DE CANDIDATURAS (MAX-HEAP)
    # ==================================================
    
    def _calcular_pontuacao_compatibilidade(self, voluntario: Voluntario, acao: Acao) -> int:
        """
        Calcula a prioridade de um voluntário para uma ação.
        Critérios:
        - +2 pontos por cada ODS em comum.
        - +1 ponto por cada competência desejada em comum.
        """
        pontos = 0
        
        # 1. Pontuação pelos ODS
        ods_em_comum = voluntario.ods_interesse.intersection(acao.ods_associados)
        pontos += (len(ods_em_comum) * 2)
        
        # 2. Pontuação pelas Competências
        comps_voluntario = set(voluntario.competencias.keys())
        comps_acao = set(acao.competencias_desejadas.keys())
        comps_em_comum = comps_voluntario.intersection(comps_acao)
        pontos += len(comps_em_comum)
        
        return pontos

    def gerar_candidaturas_ordenadas_heapsort(self, titulo_acao: str) -> List[Tuple[Inscricao, int]]:
        """
        Gera a lista de inscrições ordenadas por prioridade usando um Max-Heap e o 
        algoritmo Heapsort. Usa a data/hora real de inscrição como critério absoluto de desempate.
        """
        acao = self.consultar_acao(titulo_acao)
        if not acao or acao.fila_inscricoes.is_empty():
            return []

        heap = MaxHeap()
        inscricoes_pendentes = []

        # 1. Retirar temporariamente da fila FIFO para uma lista
        while not acao.fila_inscricoes.is_empty():
            insc = acao.fila_inscricoes.dequeue()
            if insc:
                inscricoes_pendentes.append(insc)

        # 2.Ordenar fisicamente a lista pela data de inscrição.
        # Assim garantimos que o índice 0 é sempre a data mais antiga (o 1º a chegar) independentemente 
        # da ordem em que os dados estavam guardados no ficheiro JSON!
        inscricoes_pendentes.sort(key=lambda x: x.data_hora_inscricao)

        total_pendentes = len(inscricoes_pendentes)

        # 3. Calcular prioridade de cada inscrição e inserir no Max-Heap
        for i, insc in enumerate(inscricoes_pendentes):
            voluntario = self.consultar_voluntario(insc.voluntario)
            if voluntario:
                pontos_base = self._calcular_pontuacao_compatibilidade(voluntario, acao)
            else:
                pontos_base = 0 
                
            # Como a lista já foi forçada a estar em ordem cronológica real:
            # i = 0 (mais antigo) ganha o maior bónus decimal (ex: + 0.99)
            # i = 1 (2º mais antigo) ganha o segundo maior bónus, etc.
            bonus_antiguidade = (total_pendentes - i) / (total_pendentes + 1)
            
            prioridade_exata = pontos_base + bonus_antiguidade

            heap.inserir(prioridade_exata, insc)

        # 4. O ALGORITMO HEAPSORT: Extrair tudo do Max-Heap para obter a lista final ordenada
        inscricoes_ordenadas = []
        while not heap.is_empty():
            topo = heap._heap[0] 
            insc = topo[1]
            prioridade_exata = topo[0]
            
            # Reverter o truque decimal: Transformar de volta para o inteiro visual
            pontos_limpos = int(prioridade_exata)
            
            inscricoes_ordenadas.append((insc, pontos_limpos))
            heap.extrair_max()

        # 5. Restaurar a fila original (com a ordem cronológica)
        for insc in inscricoes_pendentes:
            acao.fila_inscricoes.enqueue(insc)

        return inscricoes_ordenadas