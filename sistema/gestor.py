"""
Módulo principal de orquestração do Sistema de Voluntariado.

Este módulo implementa a classe `SistemaVoluntariado` (o "Gestor"),
responsável por centralizar o estado das entidades (Voluntários,
Entidades, Ações e Inscrições), garantir a persistência em JSON,
e fornecer a lógica de negócio necessária para satisfazer os
requisitos funcionais (RF01 a RF09).
"""

import os
import time
import networkx as nx
import matplotlib.pyplot as plt

# Apenas os módulos permitidos pelo OR07 são utilizados.
# A exportação CSV é feita com manipulação nativa de texto.

from typing import List, Optional, Dict, Any, Tuple
from sistema.modelos import Voluntario, Entidade, Acao, Inscricao
from sistema.algoritmos.insertion_sort import ordenar_voluntarios_nome
from sistema.algoritmos.merge_sort import merge_sort_acoes
from sistema.algoritmos.heap_sort import heap_sort
from sistema.base_dados import BaseDados
from sistema.estruturas.bst import BST
from sistema.estruturas.grafo import Grafo
from sistema.algoritmos.bfs import caminho_mais_curto_bfs, soma_distancias_geodesicas_bfs


class SistemaVoluntariado:
    """
    Classe principal de orquestração do sistema de voluntariado.

    Centraliza a gestão de entidades de domínio, a persistência de dados
    em formato JSON e a execução das lógicas algorítmicas de negócio.
    """

    def __init__(self) -> None:
        """
        Inicializa as estruturas de dados centrais do Gestor.
        
        As coleções principais utilizam dicionários (Dict) mapeados
        pelo nome/título em minúsculas para garantir a procura em O(1).
        
        :return: Nada.
        :rtype: None
        """
        self.voluntarios: Dict[str, Voluntario] = {}
        self.entidades: Dict[str, Entidade] = {}
        self.acoes: Dict[str, Acao] = {}
        self.ods_catalogo: Dict[int, str] = {}
        self.inscricoes: Dict[str, Inscricao] = {}
        self.presencas: List[Dict[str, Any]] = []
        self.rede_entidades: Grafo = Grafo()

    # ==========================================
    # OR02 - LEITURA E ESCRITA DE DADOS (JSON)
    # ==========================================
    
    def carregar_sistema(self, caminho_json: str) -> None:
        """
        Carrega os dados JSON do disco para a memória do Gestor.

        :param caminho_json: Caminho para a pasta ou ficheiro JSON.
        :type caminho_json: str
        :return: Nada.
        :rtype: None
        """
        if os.path.isdir(caminho_json):
            dados = self._carregar_de_pasta_json(caminho_json)
        else:
            dados = BaseDados.carregar_dados(caminho_json)
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

        for v_data in dados.get("voluntarios", []):
            v = self._desserializar_voluntario(v_data)
            self.voluntarios[v.nome.lower()] = v
            
        for e_data in dados.get("entidades", []):
            e = self._desserializar_entidade(e_data)
            self.entidades[e.nome.lower()] = e
            
        for a_data in dados.get("acoes", []):
            a = self._desserializar_acao(a_data)
            self.acoes[a.titulo.lower()] = a

        catalogo_bruto = dados.get("ods_catalogo", [])
        self.ods_catalogo = {item.get("ods_id"): item.get("ods_nome") for item in catalogo_bruto if item.get("ods_id")}
        
        self.presencas = dados.get("presencas", [])
        self.inscricoes = {}
        self._reconstruir_inscricoes(dados.get("inscricoes", []))
        print("Base de dados JSON encontrada e carregada com sucesso.")

    def guardar_sistema(self, caminho_json: str) -> None:
        """
        Guarda as coleções da memória de volta nos ficheiros JSON.

        :param caminho_json: Caminho para a pasta ou ficheiro de destino.
        :type caminho_json: str
        :return: Nada.
        :rtype: None
        """
        dados_exportar = {
            "voluntarios": [self._serializar_voluntario(v) for v in self.voluntarios.values()],
            "entidades": [self._serializar_entidade(e) for e in self.entidades.values()],
            "acoes": [self._serializar_acao(a) for a in self.acoes.values()],
            "ods_catalogo": [{"ods_id": k, "ods_nome": v} for k, v in self.ods_catalogo.items()],
            "inscricoes": [self._serializar_inscricao(i) for i in self.inscricoes.values()],
            "presencas": self.presencas,
        }
        if os.path.isdir(caminho_json):
            self._guardar_em_pasta_json(caminho_json, dados_exportar)
            return
        BaseDados.guardar_dados(caminho_json, dados_exportar)

    def _carregar_de_pasta_json(self, pasta_json: str) -> Dict[str, Any]:
        """
        Carrega múltiplos ficheiros JSON particionados de uma pasta.

        :param pasta_json: Caminho da pasta.
        :type pasta_json: str
        :return: Dicionário aglomerando todos os dados lidos.
        :rtype: Dict[str, Any]
        """
        voluntarios = BaseDados.carregar_dados(os.path.join(pasta_json, "voluntarios.json"))
        entidades = BaseDados.carregar_dados(os.path.join(pasta_json, "entidades.json"))
        acoes = BaseDados.carregar_dados(os.path.join(pasta_json, "acoes.json"))
        ods_catalogo = BaseDados.carregar_dados(os.path.join(pasta_json, "ods_catalogo.json"))
        inscricoes = BaseDados.carregar_dados(os.path.join(pasta_json, "inscricoes.json"))
        presencas = BaseDados.carregar_dados(os.path.join(pasta_json, "presencas.json"))

        return {
            "voluntarios": voluntarios if isinstance(voluntarios, list) else [],
            "entidades": entidades if isinstance(entidades, list) else [],
            "acoes": acoes if isinstance(acoes, list) else [],
            "ods_catalogo": ods_catalogo if isinstance(ods_catalogo, list) else [],
            "inscricoes": inscricoes if isinstance(inscricoes, list) else [],
            "presencas": presencas if isinstance(presencas, list) else [],
        }

    def _guardar_em_pasta_json(self, pasta_json: str, dados_exportar: Dict[str, Any]) -> None:
        """
        Guarda o dicionário de estado em ficheiros JSON particionados na pasta.

        :param pasta_json: Caminho da pasta alvo.
        :type pasta_json: str
        :param dados_exportar: Dicionário contendo os dados a persistir.
        :type dados_exportar: Dict[str, Any]
        :return: Nada.
        :rtype: None
        """
        BaseDados.guardar_dados(os.path.join(pasta_json, "voluntarios.json"), dados_exportar["voluntarios"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "entidades.json"), dados_exportar["entidades"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "acoes.json"), dados_exportar["acoes"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "ods_catalogo.json"), dados_exportar["ods_catalogo"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "inscricoes.json"), dados_exportar["inscricoes"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "presencas.json"), dados_exportar["presencas"])
        BaseDados.guardar_dados(os.path.join(pasta_json, "dataset_completo.json"), dados_exportar)

    def _serializar_voluntario(self, voluntario: Voluntario) -> Dict[str, Any]:
        """
        Converte um objeto Voluntario num dicionário primitivo.

        :param voluntario: O voluntário a serializar.
        :type voluntario: Voluntario
        :return: Dicionário representando o voluntário.
        :rtype: Dict[str, Any]
        """
        return {
            "voluntario_id": getattr(voluntario, "voluntario_id", None),
            "nome": voluntario.nome,
            "curso": voluntario.curso,
            "faculdade": voluntario.faculdade,
            "vinculo_institucional": voluntario.vinculo,
            "ano": voluntario.ano,
            "competencias": [{"competencia": nome, "nivel": nivel} for nome, nivel in voluntario.competencias.items()],
            "interesses": list(voluntario.interesses),
            "ods_interesse": list(voluntario.ods_interesse),
        }

    def _serializar_entidade(self, entidade: Entidade) -> Dict[str, Any]:
        """
        Converte um objeto Entidade num dicionário primitivo.

        :param entidade: A entidade a serializar.
        :type entidade: Entidade
        :return: Dicionário representando a entidade.
        :rtype: Dict[str, Any]
        """
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
        """
        Converte um objeto Acao num dicionário primitivo (incluindo o seu histórico).

        :param acao: A ação a serializar.
        :type acao: Acao
        :return: Dicionário representando a ação.
        :rtype: Dict[str, Any]
        """
        historico_formatado = []
        for reg in acao.historico_equipa.para_lista():
            historico_formatado.append({
                "estado_anterior": list(reg["estado_anterior"]),
                "estado_novo": list(reg["estado_novo"]),
                "data_hora": reg["data_hora"],
                "tipo": reg["tipo"]
            })
            
        return {
            "acao_id": getattr(acao, "acao_id", None),
            "titulo": acao.titulo,
            "entidades": list(acao.entidades),
            "area": acao.area,
            "data_hora": acao.data_hora,
            "duracao_horas": acao.duracao,
            "vagas": acao.vagas,
            "localizacao": acao.localizacao,
            "estado": acao.estado,
            "metrica_impacto": acao.metrica_impacto,
            "competencias_desejadas": [{"competencia": nome, "nivel_minimo": nivel} for nome, nivel in acao.competencias_desejadas.items()],
            "ods_associados": [{"ods_id": ods} for ods in acao.ods_associados],
            "equipa": list(getattr(acao, "equipa", set())),
            "historico_equipa": historico_formatado,
        }

    def _serializar_inscricao(self, inscricao: Inscricao) -> Dict[str, Any]:
        """
        Converte um objeto Inscricao num dicionário primitivo.

        :param inscricao: A inscrição a serializar.
        :type inscricao: Inscricao
        :return: Dicionário representando a inscrição.
        :rtype: Dict[str, Any]
        """
        return {
            "inscricao_id": getattr(inscricao, "inscricao_id", None),
            "voluntario_id": getattr(inscricao, "voluntario_id", None),
            "acao_id": getattr(inscricao, "acao_id", None),
            "data_hora_inscricao": inscricao.data_hora_inscricao,
            "estado": inscricao.estado,
        }

    def _desserializar_voluntario(self, dados: Dict[str, Any]) -> Voluntario:
        """
        Reconstrói um objeto Voluntario a partir de um dicionário.

        :param dados: Dicionário contendo os dados do voluntário.
        :type dados: Dict[str, Any]
        :return: O objeto Voluntario reconstruído.
        :rtype: Voluntario
        """
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
            voluntario.competencias = {c.get("competencia", ""): c.get("nivel", 0) for c in competencias}
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
        """
        Reconstrói um objeto Entidade a partir de um dicionário.

        :param dados: Dicionário contendo os dados da entidade.
        :type dados: Dict[str, Any]
        :return: O objeto Entidade reconstruído.
        :rtype: Entidade
        """
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
        """
        Reconstrói um objeto Acao e a sua Pilha de histórico a partir de um dicionário.

        :param dados: Dicionário contendo os dados da ação.
        :type dados: Dict[str, Any]
        :return: O objeto Acao reconstruído.
        :rtype: Acao
        """
        # Se for um JSON novo, carrega a lista. Se for JSON antigo, converte a string para lista.
        entidades_carregadas = dados.get("entidades", [])
        if not entidades_carregadas:
            entidade_antiga = dados.get("entidade_nome", dados.get("entidade", ""))
            if entidade_antiga:
                entidades_carregadas = [entidade_antiga]

        acao = Acao(
            titulo=dados.get("titulo", ""),
            entidades=entidades_carregadas, 
            data_hora=dados.get("data_hora", ""),
            duracao=dados.get("duracao_horas", dados.get("duracao", 0)),
            vagas=dados.get("vagas", 0),
            localizacao=dados.get("localizacao", ""),
            area=dados.get("area", ""),
        )
        
        acao.acao_id = dados.get("acao_id")   
        acao.estado = dados.get("estado", "planeada")
        acao.metrica_impacto = float(dados.get("metrica_impacto", 0.0))
        
        comp = dados.get("competencias_desejadas", {})
        if isinstance(comp, list):
            acao.competencias_desejadas = {c.get("competencia", ""): c.get("nivel_minimo", 0) for c in comp}
        else:
            acao.competencias_desejadas = comp
            
        ods = dados.get("ods_associados", [])
        if ods and isinstance(ods[0], dict):
            acao.ods_associados = set(item.get("ods_id") for item in ods if item.get("ods_id"))
        else:
            acao.ods_associados = set(ods)
            
        acao.equipa = set(dados.get("equipa", []))
        
        historico_salvo = dados.get("historico_equipa", [])
        for reg in reversed(historico_salvo):
            acao.historico_equipa.push({
                "estado_anterior": set(reg.get("estado_anterior", [])),
                "estado_novo": set(reg.get("estado_novo", [])),
                "data_hora": reg.get("data_hora", ""),
                "tipo": reg.get("tipo", "")
            })
            
        return acao

    def _reconstruir_inscricoes(self, inscricoes_dados: List[Dict[str, Any]]) -> None:
        """
        Reconstrói os objetos Inscrição e insere-os nas filas/listas corretas das Ações.

        :param inscricoes_dados: Lista de dicionários correspondentes às inscrições.
        :type inscricoes_dados: List[Dict[str, Any]]
        :return: Nada.
        :rtype: None
        """
        voluntarios_por_id = {
            getattr(v, "voluntario_id", None): v for v in self.voluntarios.values() if getattr(v, "voluntario_id", None)
        }
        acoes_por_id = {
            getattr(a, "acao_id", None): a for a in self.acoes.values() if getattr(a, "acao_id", None)
        }

        for item in inscricoes_dados:
            voluntario_id = item.get("voluntario_id")
            acao_id = item.get("acao_id")
            acao = acoes_por_id.get(acao_id)
            voluntario = voluntarios_por_id.get(voluntario_id)
            if not acao:
                continue

            nome_voluntario = voluntario.nome if voluntario else str(voluntario_id)
            inscricao = Inscricao(
                voluntario=nome_voluntario,
                acao=acao.titulo,
                data_hora_inscricao=item.get("data_hora_inscricao", ""),
            )
            inscricao.inscricao_id = item.get("inscricao_id")
            inscricao.voluntario_id = voluntario_id
            inscricao.acao_id = acao_id
            inscricao.atualizar_estado(item.get("estado", "pendente"))
            # Adicionar ao Dicionário usando o ID (se não tiver, criamos um seguro)
            insc_id = inscricao.inscricao_id
            if not insc_id:
                insc_id = f"I{len(self.inscricoes) + 1:04d}"
                inscricao.inscricao_id = insc_id
            self.inscricoes[insc_id] = inscricao

            if inscricao.estado == "pendente":
                acao.fila_inscricoes.enqueue(inscricao)
            elif inscricao.estado == "aprovada":
                acao.inscricoes_aprovadas.append(inscricao)

    def _gerar_proximo_id(self, col: Dict[str, Any], atributo_id: str, prefixo: str) -> str:
        """
        Gera um identificador sequencial baseando-se no maior ID atual da coleção.

        :param col: Dicionário contendo os objetos da coleção.
        :type col: Dict[str, Any]
        :param atributo_id: Nome do atributo que guarda o ID (ex: "acao_id").
        :type atributo_id: str
        :param prefixo: Letra(s) de prefixo para o novo ID (ex: "V", "E", "A").
        :type prefixo: str
        :return: Nova string de ID formatada.
        :rtype: str
        """
        maior = 0
        for item in col.values():
            valor_id = getattr(item, atributo_id, None)
            if not isinstance(valor_id, str) or not valor_id.startswith(prefixo):
                continue
            sufixo = valor_id[len(prefixo):]
            if sufixo.isdigit():
                maior = max(maior, int(sufixo))
        return f"{prefixo}{maior + 1:03d}"

    # ==========================================
    # RF01 - GESTÃO DE VOLUNTÁRIOS
    # ==========================================
    
    def adicionar_voluntario(self, voluntario: Voluntario) -> None:
        """Adiciona um voluntário novo ao sistema."""
        chave = voluntario.nome.lower()
        if chave in self.voluntarios:
            print(f"Erro: O voluntário '{voluntario.nome}' já existe.")
        else:
            voluntario.voluntario_id = self._gerar_proximo_id(self.voluntarios, "voluntario_id", "V")
            self.voluntarios[chave] = voluntario
            print(f"Voluntário adicionado com sucesso (ID: {voluntario.voluntario_id}).")

    def consultar_voluntario(self, nome: str) -> Optional[Voluntario]:
        """Pesquisa exata de um voluntário (Tempo O(1))."""
        return self.voluntarios.get(nome.lower())

    def pesquisar_voluntarios(self, termo: str) -> List[Voluntario]:
        """Pesquisa parcial por um voluntário baseada num termo."""
        termo_normalizado = termo.strip().lower()
        if not termo_normalizado:
            return []
        return [v for v in self.voluntarios.values() if termo_normalizado in v.nome.lower().split()]

    def remover_voluntario(self, nome: str) -> bool:
        """Remove um voluntário do sistema."""
        chave = nome.lower()
        if chave in self.voluntarios:
            del self.voluntarios[chave]
            print(f"Voluntário '{nome}' removido.")
            return True
        print("Voluntário não encontrado.")
        return False

    def atualizar_voluntario_completo(self, nome: str, campos: Dict[str, Any]) -> bool:
        """Atualiza múltiplos campos de um voluntário e reajusta as chaves do dicionário se necessário."""
        chave_atual = nome.lower()
        voluntario = self.voluntarios.get(chave_atual)
        if not voluntario:
            print("Voluntário não encontrado.")
            return False
            
        novo_nome = campos.get("nome")
        if novo_nome and novo_nome.lower() != chave_atual:
            nova_chave = novo_nome.lower()
            if nova_chave in self.voluntarios:
                print("Erro: Já existe um voluntário com esse nome.")
                return False
            del self.voluntarios[chave_atual]
            self.voluntarios[nova_chave] = voluntario

        for chave, valor in campos.items():
            setattr(voluntario, chave, valor)
        return True

    # ==========================================
    # RF01 - GESTÃO DE ENTIDADES
    # ==========================================
    
    def adicionar_entidade(self, entidade: Entidade) -> None:
        """Adiciona uma entidade promotora ao sistema."""
        chave = entidade.nome.lower()
        if chave in self.entidades:
            print(f"Erro: A entidade '{entidade.nome}' já existe.")
        else:
            entidade.entidade_id = self._gerar_proximo_id(self.entidades, "entidade_id", "E")
            self.entidades[chave] = entidade
            print(f"Entidade adicionada com sucesso (ID: {entidade.entidade_id}).")

    def consultar_entidade(self, nome: str) -> Optional[Entidade]:
        """Pesquisa exata de uma entidade (Tempo O(1))."""
        return self.entidades.get(nome.lower())

    def remover_entidade(self, nome: str) -> bool:
        """Remove uma entidade do sistema."""
        chave = nome.lower()
        if chave in self.entidades:
            del self.entidades[chave]
            print(f"Entidade '{nome}' removida.")
            return True
        print("Entidade não encontrada.")
        return False

    def atualizar_entidade_completo(self, nome: str, campos: Dict[str, Any]) -> bool:
        """Atualiza múltiplos campos de uma entidade e reajusta as chaves do dicionário se necessário."""
        chave_atual = nome.lower()
        entidade = self.entidades.get(chave_atual)
        if not entidade:
            print("Entidade não encontrada.")
            return False
            
        novo_nome = campos.get("nome")
        if novo_nome and novo_nome.lower() != chave_atual:
            nova_chave = novo_nome.lower()
            if nova_chave in self.entidades:
                print("Erro: Já existe uma entidade com esse nome.")
                return False
            del self.entidades[chave_atual]
            self.entidades[nova_chave] = entidade

        for chave, valor in campos.items():
            setattr(entidade, chave, valor)
        return True

    # ==========================================
    # RF01 - GESTÃO DE AÇÕES
    # ==========================================
    
    def adicionar_acao(self, acao: Acao) -> None:
        """Adiciona uma ação de voluntariado ao sistema."""
        chave = acao.titulo.lower()
        if chave in self.acoes:
            print(f"Erro: A ação '{acao.titulo}' já existe.")
            return

        entidade = self.consultar_entidade(acao.entidade)
        if not entidade:
            print("Erro: A entidade promotora indicada não existe. Crie/valide a entidade antes de registar a ação.")
        else:
            acao.entidade_id = entidade.entidade_id
            acao.acao_id = self._gerar_proximo_id(self.acoes, "acao_id", "A")
            self.acoes[chave] = acao
            print(f"Ação adicionada com sucesso (ID: {acao.acao_id}).")

    def consultar_acao(self, titulo: str) -> Optional[Acao]:
        """Pesquisa exata de uma ação (Tempo O(1))."""
        return self.acoes.get(titulo.lower())

    def remover_acao(self, titulo: str) -> bool:
        """Remove uma ação do sistema."""
        chave = titulo.lower()
        if chave in self.acoes:
            del self.acoes[chave]
            print(f"Ação '{titulo}' removida.")
            return True
        print("Ação não encontrada.")
        return False

    def atualizar_acao_completo(self, titulo: str, campos: Dict[str, Any]) -> bool:
        """Atualiza múltiplos campos de uma ação e reajusta as chaves do dicionário se necessário."""
        chave_atual = titulo.lower()
        acao = self.acoes.get(chave_atual)
        if not acao:
            print("Ação não encontrada.")
            return False
            
        novo_titulo = campos.get("titulo")
        if novo_titulo and novo_titulo.lower() != chave_atual:
            nova_chave = novo_titulo.lower()
            if nova_chave in self.acoes:
                print("Erro: Já existe uma ação com esse título.")
                return False
            del self.acoes[chave_atual]
            self.acoes[nova_chave] = acao

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
        """Retorna as ações que têm pelo menos uma inscrição por avaliar na Fila."""
        return [a for a in self.acoes.values() if not a.fila_inscricoes.is_empty()]

    def espreitar_proxima_inscricao(self, titulo_acao: str) -> Optional[Inscricao]:
        """Permite visualizar a próxima inscrição na fila de uma ação sem a remover (Peek)."""
        acao = self.consultar_acao(titulo_acao)
        if not acao or acao.fila_inscricoes.is_empty():
            return None
        return acao.fila_inscricoes._cabeca.valor if acao.fila_inscricoes._cabeca else None

    # ============================================
    # RF02 – PROCESSAMENTO DE INSCRIÇÕES (FIFO)
    # ============================================
    
    def processar_inscricao_na_acao(self, titulo_acao: str, aprovada: bool) -> None:
        """
        Lida com a aprovação ou rejeição da primeira inscrição na fila de uma ação.

        :param titulo_acao: O título da ação a avaliar.
        :type titulo_acao: str
        :param aprovada: Se True a inscrição é aprovada, se False é rejeitada.
        :type aprovada: bool
        :return: Nada.
        :rtype: None
        """
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
            print(f"Inscrição aprovada: {inscricao.voluntario}. Vagas restantes: {acao.vagas}")
        elif aprovada:
            inscricao.atualizar_estado("lista de espera")
            print(f"Sem vagas! {inscricao.voluntario} foi para lista de espera.")
        else:
            inscricao.atualizar_estado("rejeitada")
            print(f"Inscrição rejeitada: {inscricao.voluntario}.")
    
    # ==========================================
    # RF03 (i) - PESQUISA E LISTAGEM (INSERTION)
    # ==========================================

    def listar_voluntarios_prefixo(self, prefixo: str) -> None:
        """
        Pesquisa e imprime voluntários com base num prefixo, ordenando-os 
        alfabeticamente via Insertion Sort.

        :param prefixo: String com o prefixo a procurar.
        :type prefixo: str
        :return: Nada.
        :rtype: None
        """
        resultados = [v for v in self.voluntarios.values() if v.nome.lower().startswith(prefixo.lower())]
        ordenar_voluntarios_nome(resultados)
        for v in resultados:
            print(f"- {v.nome} | Curso: {v.curso} | Faculdade: {v.faculdade} | Competências: {v.competencias} | Tags: {v.interesses} | ODS: {v.ods_interesse}")

    # ==========================================
    # RF03 (ii) - PESQUISA E LISTAGEM (MERGE)
    # ==========================================
    
    def pesquisar_e_listar_acoes(self, filtros: Dict[str, Any], ordenar_por: str = "data_hora") -> None:
        """
        Filtra as ações de voluntariado e ordena o resultado usando Merge Sort.

        :param filtros: Dicionário contendo os critérios de filtragem.
        :type filtros: Dict[str, Any]
        :param ordenar_por: Nome do atributo para o Merge Sort processar.
        :type ordenar_por: str
        :return: Nada.
        :rtype: None
        """
        resultados = list(self.acoes.values())

        if filtros.get("entidade"):
            # CORREÇÃO: Procura se o texto inserido existe nalguma das entidades da lista
            resultados = [a for a in resultados if any(filtros["entidade"].lower() in ent.lower() for ent in a.entidades)]
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
            # join() para imprimir todas as entidades parceiras formatadas
            print(f"[{getattr(a, ordenar_por)}] {a.titulo} (Entidades: {', '.join(a.entidades)}) - Vagas: {a.vagas}")

    # ==========================================
    # RF04 – ESTATÍSTICAS E DASHBOARD (V1)
    # ==========================================

    def gerar_dashboard(self) -> None:
        """
        Gera agregações estatísticas do impacto por ODS e desenha gráficos (Dashboard V1).

        :return: Nada.
        :rtype: None
        """
        acoes_por_ods = {i: 0 for i in range(1, 18)}
        horas_por_ods = {i: 0 for i in range(1, 18)}
        horas_por_voluntario = {}

        for acao in self.acoes.values():
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

    def _desenhar_graficos(self, acoes_ods: Dict[int, int], horas_ods: Dict[int, float]) -> None:
        """
        Desenha os gráficos de barras para a versão 1 do Dashboard.

        :param acoes_ods: Dicionário contabilizando ações por cada ODS.
        :type acoes_ods: Dict[int, int]
        :param horas_ods: Dicionário contabilizando horas gastas por ODS.
        :type horas_ods: Dict[int, float]
        :return: Nada.
        :rtype: None
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
            ax1.text(barra.get_x() + barra.get_width() / 2, altura + 0.05, f"{int(altura)}", ha='center', va='bottom', fontsize=9)

        barras2 = ax2.bar(labels_horas, valores_horas, color='lightgreen', edgecolor='black', linewidth=0.6)
        ax2.set_title('Horas Totais por ODS')
        ax2.set_ylabel('Horas')
        ax2.grid(axis='y', linestyle='--', alpha=0.35)
        ax2.tick_params(axis='x', labelrotation=35)
        for barra in barras2:
            altura = barra.get_height()
            texto_altura = f"{altura:.1f}" if isinstance(altura, float) and not altura.is_integer() else f"{int(altura)}"
            ax2.text(barra.get_x() + barra.get_width() / 2, altura + 0.05, texto_altura, ha='center', va='bottom', fontsize=9)

        fig.subplots_adjust(bottom=0.22, wspace=0.26)
        plt.show()

    # ==========================================
    # RF09 – ESTATÍSTICAS E DASHBOARD (V2)
    # ==========================================    

    def gerar_dashboard_v2(self) -> None:
        """
        Gera o Dashboard V2 (RF09) focado na demografia e panorama de candidaturas.

        :return: Nada.
        :rtype: None
        """
        if not self.voluntarios and not self.inscricoes:
            print("\nSem dados suficientes para gerar as estatísticas do Dashboard V2.")
            return

        faculdades_contagem = {}
        for v in self.voluntarios.values():
            faculdades_contagem[v.faculdade] = faculdades_contagem.get(v.faculdade, 0) + 1

        estados_inscricao = {"pendente": 0, "aprovada": 0, "rejeitada": 0, "lista de espera": 0}
        for insc in self.inscricoes.values():
            estado_atual = insc.estado.lower()
            if estado_atual in estados_inscricao:
                estados_inscricao[estado_atual] += 1
            else:
                estados_inscricao[estado_atual] = 1

        print("\n" + "="*50)
        print("   DASHBOARD V2: DEMOGRAFIA E CANDIDATURAS (RF09)   ")
        print("="*50)

        print("\n[VOLUNTÁRIOS POR FACULDADE]")
        faculdades_ord = sorted(faculdades_contagem.items(), key=lambda x: x[1], reverse=True)
        for faculdade, total in faculdades_ord:
            print(f" • {faculdade}: {total} voluntário(s)")

        print("\n[ESTADO GERAL DAS CANDIDATURAS]")
        for estado, total in estados_inscricao.items():
            print(f" • {estado.capitalize()}: {total} candidatura(s)")
        print("="*50)

        self._desenhar_graficos_v2(faculdades_contagem, estados_inscricao)

    def _desenhar_graficos_v2(self, faculdades: Dict[str, int], estados_insc: Dict[str, int]) -> None:
        """
        Desenha os gráficos circulares e de barras para a versão 2 do Dashboard.

        :param faculdades: Dicionário contabilizando alunos por faculdade.
        :type faculdades: Dict[str, int]
        :param estados_insc: Dicionário contabilizando o estado das candidaturas.
        :type estados_insc: Dict[str, int]
        :return: Nada.
        :rtype: None
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        if faculdades:
            labels_fac = list(faculdades.keys())
            valores_fac = list(faculdades.values())
            ax1.pie(valores_fac, labels=labels_fac, autopct='%1.1f%%', startangle=140, 
                    colors=plt.cm.Paired.colors)
            ax1.set_title('Distribuição por Faculdade', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, "Sem dados de Faculdades", ha='center', va='center')
            ax1.axis('off')

        estados_ativos = {k.capitalize(): v for k, v in estados_insc.items() if v > 0}
        
        if estados_ativos:
            labels_est = list(estados_ativos.keys())
            valores_est = list(estados_ativos.values())
            
            cores = []
            for label in labels_est:
                if label == "Aprovada": cores.append('mediumseagreen')
                elif label == "Pendente": cores.append('gold')
                elif label == "Rejeitada": cores.append('tomato')
                else: cores.append('lightskyblue')

            barras = ax2.bar(labels_est, valores_est, color=cores, edgecolor='black', linewidth=0.8)
            
            ax2.set_title('Panorama de Candidaturas', fontweight='bold')
            ax2.set_ylabel('Quantidade')
            ax2.grid(axis='y', linestyle='--', alpha=0.4)
            
            for barra in barras:
                altura = barra.get_height()
                ax2.text(barra.get_x() + barra.get_width() / 2, altura + 0.1, 
                         f"{int(altura)}", ha='center', va='bottom', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, "Sem dados de Inscrições", ha='center', va='center')
            ax2.axis('off')

        fig.subplots_adjust(wspace=0.3)
        plt.show()

    # ==============================================
    # RF05 - REQUISITO OPCIONAL (EXPORTAR RELATÓRIO)
    # ==============================================

    def exportar_relatorio(self) -> None:
        """
        Processa agregações de dados e gera um PDF multipáginas oficial.

        :return: Nada.
        :rtype: None
        """
        if not self.acoes:
            print("Não há dados suficientes para gerar um relatório.")
            return

        acoes_por_ods = {i: 0 for i in range(1, 18)}
        horas_por_ods = {i: 0 for i in range(1, 18)}
        horas_por_voluntario = {}
        faculdades_contagem = {}
        estados_inscricao = {"pendente": 0, "aprovada": 0, "rejeitada": 0, "lista de espera": 0}

        for acao in self.acoes.values():
            for ods in acao.ods_associados:
                acoes_por_ods[ods] += 1
                
            if acao.estado.lower() == "concluída":
                for ods in acao.ods_associados:
                    horas_por_ods[ods] += acao.duracao
                    
                for inscricao in getattr(acao, 'inscricoes_aprovadas', []):
                    nome_vol = inscricao.voluntario
                    horas_por_voluntario[nome_vol] = horas_por_voluntario.get(nome_vol, 0) + acao.duracao

        for v in self.voluntarios.values():
            faculdades_contagem[v.faculdade] = faculdades_contagem.get(v.faculdade, 0) + 1

        for insc in self.inscricoes.values():
            est = insc.estado.lower()
            estados_inscricao[est] = estados_inscricao.get(est, 0) + 1

        top_ods = sorted(acoes_por_ods.items(), key=lambda x: x[1], reverse=True)[:3]
        top_voluntarios = sorted(horas_por_voluntario.items(), key=lambda x: x[1], reverse=True)[:5]

        os.makedirs("relatorios", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        data_formatada = time.strftime('%d/%m/%Y %H:%M:%S')
        nome_ficheiro = os.path.join("relatorios", f"relatorio_oficial_{timestamp}.pdf")

        try:
            from matplotlib.backends.backend_pdf import PdfPages
            
            with PdfPages(nome_ficheiro) as pdf:
                cor_primaria = '#005b96'
                cor_texto = '#333333'

                fig1 = plt.figure(figsize=(8.27, 11.69))
                fig1.text(0.5, 0.93, "RELATÓRIO DE VOLUNTARIADO (AED)", ha='center', va='center', fontsize=18, fontweight='bold', color=cor_primaria)
                fig1.text(0.5, 0.90, f"Documento gerado a: {data_formatada} | Página 1", ha='center', va='center', fontsize=10, color='gray', style='italic')
                
                ax_line1 = fig1.add_axes([0.1, 0.88, 0.8, 0.01])
                ax_line1.axis('off')
                ax_line1.plot([0, 1], [0, 0], color=cor_primaria, lw=2)
                
                fig1.text(0.1, 0.83, "RESUMO GERAL", ha='left', va='center', fontsize=12, fontweight='bold', color=cor_primaria)
                
                fig1.text(0.25, 0.77, str(len(self.voluntarios)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
                fig1.text(0.25, 0.73, "Voluntários\nRegistados", ha='center', va='top', fontsize=10, color=cor_texto)
                
                fig1.text(0.5, 0.77, str(len(self.entidades)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
                fig1.text(0.5, 0.73, "Entidades\nParceiras", ha='center', va='top', fontsize=10, color=cor_texto)
                
                fig1.text(0.75, 0.77, str(len(self.acoes)), ha='center', va='center', fontsize=24, fontweight='bold', color=cor_primaria)
                fig1.text(0.75, 0.73, "Ações\nRegistadas", ha='center', va='top', fontsize=10, color=cor_texto)
                
                ax1 = fig1.add_axes([0.1, 0.45, 0.35, 0.20])
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
                        ax1.text(barra.get_x() + barra.get_width() / 2, altura + (max(valores_acoes) * 0.02), f"{int(altura)}", ha='center', va='bottom', fontsize=7)
                else:
                    ax1.axis('off')
                    ax1.text(0.5, 0.5, "Sem dados de ODS", ha='center', va='center', fontsize=9)

                ax2 = fig1.add_axes([0.55, 0.45, 0.35, 0.20])
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
                        ax2.text(barra.get_x() + barra.get_width() / 2, altura + (max(valores_horas) * 0.02), texto_altura, ha='center', va='bottom', fontsize=7)
                else:
                    ax2.axis('off')
                    ax2.text(0.5, 0.5, "Sem horas registadas", ha='center', va='center', fontsize=9)

                fig1.text(0.1, 0.33, "TOP 3 ODS MAIS ATIVOS", ha='left', va='center', fontsize=11, fontweight='bold', color=cor_primaria)
                y_pos = 0.29
                if top_ods and top_ods[0][1] > 0:
                    for ods, contagem in top_ods:
                        if contagem > 0:
                            fig1.text(0.1, y_pos, f"• ODS {ods}: {contagem} ações", ha='left', va='center', fontsize=10, color=cor_texto)
                            y_pos -= 0.03
                else:
                    fig1.text(0.1, y_pos, "Sem ações registadas.", ha='left', va='center', fontsize=10, color=cor_texto)

                fig1.text(0.55, 0.33, "TOP 5 VOLUNTÁRIOS (POR HORAS)", ha='left', va='center', fontsize=11, fontweight='bold', color=cor_primaria)
                y_pos = 0.29
                if top_voluntarios:
                    for i, (nome, horas) in enumerate(top_voluntarios, 1):
                        fig1.text(0.55, y_pos, f"{i}º Lugar: {nome} - {horas}h totais", ha='left', va='center', fontsize=10, color=cor_texto)
                        y_pos -= 0.03
                else:
                    fig1.text(0.55, y_pos, "Nenhum voluntário com horas validadas.", ha='left', va='center', fontsize=10, color=cor_texto)

                fig1.text(0.5, 0.05, "Relatório gerado pelo Sistema de Voluntariado (Projeto AED)", ha='center', va='center', fontsize=8, color='gray')
                pdf.savefig(fig1)

                fig2 = plt.figure(figsize=(8.27, 11.69))
                
                fig2.text(0.5, 0.93, "ANÁLISE DEMOGRÁFICA E CANDIDATURAS", ha='center', va='center', fontsize=18, fontweight='bold', color=cor_primaria)
                fig2.text(0.5, 0.90, f"Documento gerado a: {data_formatada} | Página 2", ha='center', va='center', fontsize=10, color='gray', style='italic')
                
                ax_line2 = fig2.add_axes([0.1, 0.88, 0.8, 0.01])
                ax_line2.axis('off')
                ax_line2.plot([0, 1], [0, 0], color=cor_primaria, lw=2)

                ax_pie = fig2.add_axes([0.25, 0.55, 0.5, 0.25])
                if faculdades_contagem:
                    ax_pie.pie(faculdades_contagem.values(), labels=faculdades_contagem.keys(), autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
                    ax_pie.set_title("Distribuição por Faculdade", fontweight='bold', color=cor_primaria)
                else:
                    ax_pie.text(0.5, 0.5, "Sem dados de Faculdades", ha='center', va='center')
                    ax_pie.axis('off')

                ax_bar = fig2.add_axes([0.2, 0.15, 0.6, 0.25])
                estados_ativos = {k.capitalize(): v for k, v in estados_inscricao.items() if v > 0}
                if estados_ativos:
                    cores_est = []
                    for label in estados_ativos.keys():
                        if label == "Aprovada": cores_est.append('mediumseagreen')
                        elif label == "Pendente": cores_est.append('gold')
                        elif label == "Rejeitada": cores_est.append('tomato')
                        else: cores_est.append('lightskyblue')

                    barras_est = ax_bar.bar(estados_ativos.keys(), estados_ativos.values(), color=cores_est, edgecolor='black')
                    ax_bar.set_title("Panorama Geral de Candidaturas", fontweight='bold', color=cor_primaria)
                    ax_bar.set_ylabel('Quantidade')
                    ax_bar.grid(axis='y', linestyle='--', alpha=0.3)
                    
                    for barra in barras_est:
                        altura = barra.get_height()
                        ax_bar.text(barra.get_x() + barra.get_width()/2, altura + 0.1, f"{int(altura)}", ha='center', va='bottom')
                else:
                    ax_bar.text(0.5, 0.5, "Sem dados de Inscrições", ha='center', va='center')
                    ax_bar.axis('off')

                fig2.text(0.5, 0.05, "Relatório gerado pelo Sistema de Voluntariado (Projeto AED)", ha='center', va='center', fontsize=8, color='gray')
                pdf.savefig(fig2)

            plt.close('all')
            print(f"\n Sucesso! Relatório visual exportado com sucesso (2 páginas).")
            print(f" Nome do ficheiro: {nome_ficheiro}")
            
        except Exception as e:
            print(f"Erro ao guardar o relatório: {e}")

    def exportar_relatorio_csv(self) -> None:
        """
        Gera um ficheiro CSV tabular com os dados do programa usando manipulação nativa de texto.
        Garante a conformidade com as restrições de bibliotecas do requisito OR07.

        :return: Nada.
        :rtype: None
        """
        if not self.acoes:
            print("Não há dados suficientes para gerar um relatório CSV.")
            return

        os.makedirs("relatorios", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nome_ficheiro = os.path.join("relatorios", f"relatorio_dados_{timestamp}.csv")

        try:
            with open(nome_ficheiro, mode='w', encoding='utf-8-sig') as ficheiro_csv:
                # Escrever cabeçalho com formatação nativa (alterado para plural)
                cabecalhos = [
                    "ID da Ação", "Título", "Entidades Promotoras", "Área Temática", 
                    "Data e Hora", "Duração (Horas)", "Vagas Restantes", 
                    "Estado Atual", "Métrica de Impacto", "Qtd. Aprovados",
                    "Nomes dos Voluntários Aprovados", "Faculdades Envolvidas"
                ]
                ficheiro_csv.write(";".join(cabecalhos) + "\n")
                
                for acao in self.acoes.values():
                    nomes_aprovados = []
                    faculdades_envolvidas = set()
                    
                    for inscricao in getattr(acao, 'inscricoes_aprovadas', []):
                        nomes_aprovados.append(inscricao.voluntario)
                        vol = self.consultar_voluntario(inscricao.voluntario)
                        if vol:
                            faculdades_envolvidas.add(vol.faculdade)
                            
                    str_nomes = ", ".join(nomes_aprovados) if nomes_aprovados else "Nenhum"
                    str_faculdades = ", ".join(faculdades_envolvidas) if faculdades_envolvidas else "-"

                    # Limpar as strings de potenciais "ponto e vírgula" 
                    titulo_limpo = str(acao.titulo).replace(";", ",")
                    
                    # Junta as várias entidades numa única string separada por vírgulas
                    entidade_limpa = ", ".join(acao.entidades).replace(";", ",")
                    
                    area_limpa = str(acao.area).replace(";", ",")
                    
                    linha = [
                        str(getattr(acao, "acao_id", "")),
                        titulo_limpo,
                        entidade_limpa,
                        area_limpa,
                        str(acao.data_hora),
                        str(acao.duracao),
                        str(acao.vagas),
                        str(acao.estado).capitalize(),
                        str(acao.metrica_impacto).replace(".", ","), # Formato numérico europeu Excel
                        str(len(nomes_aprovados)),
                        str_nomes.replace(";", ","),
                        str_faculdades.replace(";", ",")
                    ]
                    
                    ficheiro_csv.write(";".join(linha) + "\n")
                    
            print(f"\n Sucesso! Dados tabulares exportados com sucesso para CSV nativo.")
            print(f" Nome do ficheiro: {nome_ficheiro}")
            
        except Exception as e:
            print(f"Erro ao guardar o relatório CSV nativo: {e}")

    # ====================================================
    # RF06 - FORMAÇÃO DE EQUIPAS PARA AÇÕES (PILHA / UNDO)
    # ====================================================
    
    def adequacao_voluntario_acao(self, voluntario: Voluntario, acao: Acao) -> bool:
        """
        Valida se um voluntário possui perfil adequado para uma ação específica.

        :param voluntario: Objeto voluntário a analisar.
        :type voluntario: Voluntario
        :param acao: Objeto ação pretendida.
        :type acao: Acao
        :return: True se tem competências/ODS/interesses partilhados, False caso contrário.
        :rtype: bool
        """
        ods_em_comum = voluntario.ods_interesse.intersection(acao.ods_associados)
        comps_voluntario = set(voluntario.competencias.keys())
        comps_acao = set(acao.competencias_desejadas.keys())
        comps_em_comum = comps_voluntario.intersection(comps_acao)
        interesses_vol = {i.lower() for i in voluntario.interesses}
        interesse_na_area = acao.area.lower() in interesses_vol
        
        if ods_em_comum or comps_em_comum or interesse_na_area:
            return True
            
        return False

    def adicionar_voluntario_equipa(self, titulo_acao: str, voluntario_nome: str) -> Tuple[bool, str]:
        """
        Gere a adição de um voluntário à equipa de uma ação (com gravação na Pilha).

        :param titulo_acao: O título da ação.
        :type titulo_acao: str
        :param voluntario_nome: Nome do voluntário a adicionar.
        :type voluntario_nome: str
        :return: Um tuplo indicando sucesso/falha e a respetiva mensagem.
        :rtype: Tuple[bool, str]
        """
        acao = self.consultar_acao(titulo_acao)
        voluntario = self.consultar_voluntario(voluntario_nome)
        
        if not acao: return False, "Ação não encontrada."
        if not voluntario: return False, "Voluntário não encontrado."
        if voluntario.nome in acao.equipa: return False, "O voluntário já pertence a esta equipa."
        if not self.adequacao_voluntario_acao(voluntario, acao): return False, "Perfil não se adequa à ação."
            
        estado_antigo = set(acao.equipa)
        acao.equipa.add(voluntario.nome)
        
        agora = time.strftime('%Y-%m-%d %H:%M:%S')
        acao.historico_equipa.push({
            "estado_anterior": estado_antigo,
            "estado_novo": set(acao.equipa),
            "data_hora": agora,
            "tipo": f"Adição: {voluntario.nome}" 
        })
        
        return True, f"{voluntario.nome} foi adicionado à equipa."

    def remover_voluntario_equipa(self, titulo_acao: str, voluntario_nome: str) -> Tuple[bool, str]:
        """
        Gere a remoção de um voluntário de uma equipa (com gravação na Pilha Undo).

        :param titulo_acao: O título da ação.
        :type titulo_acao: str
        :param voluntario_nome: Nome do voluntário a retirar.
        :type voluntario_nome: str
        :return: Um tuplo indicando sucesso/falha e a respetiva mensagem.
        :rtype: Tuple[bool, str]
        """
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
            "tipo": f"Remoção: {voluntario_nome}"
        })
        
        return True, f"{voluntario_nome} foi removido da equipa."

    def desfazer_alteracao_equipa(self, titulo_acao: str) -> Tuple[bool, str]:
        """
        Retrocede o estado da equipa aplicando a função de Undo via Pilha.

        :param titulo_acao: Título da ação a manipular.
        :type titulo_acao: str
        :return: Tuplo indicativo de sucesso/falha da reversão.
        :rtype: Tuple[bool, str]
        """
        acao = self.consultar_acao(titulo_acao)
        if not acao: return False, "Ação não encontrada."
        if acao.historico_equipa.is_empty(): return False, "Não existem alterações anteriores para desfazer nesta sessão."
            
        registro = acao.historico_equipa.pop()
        acao.equipa = registro["estado_anterior"]
        return True, "A última alteração à equipa foi desfeita com sucesso."
    
    # ==========================================
    # RF07 - CONSULTA DE AÇÕES POR IMPACTO (BST)
    # ==========================================
    
    def _construir_bst_impacto(self) -> BST:
        """
        Método utilitário que instaura e preenche a Árvore Binária de Busca (BST) 
        com as ações em vigor.

        :return: A árvore BST preenchida.
        :rtype: BST
        """
        arvore = BST()
        for acao in self.acoes.values():
            arvore.inserir(acao.metrica_impacto, acao)
        return arvore

    def consultar_acoes_por_impacto_ordem(self, crescente: bool = True) -> List[Acao]:
        """
        Retorna a lista completa de ações ordenada pelo seu impacto.

        :param crescente: Se True a ordenação é crescente, se False é decrescente.
        :type crescente: bool
        :return: Lista das ações organizadas.
        :rtype: List[Acao]
        """
        arvore = self._construir_bst_impacto()
        acoes_ordenadas = arvore.listar_em_ordem()
        if not crescente:
            acoes_ordenadas.reverse()
        return acoes_ordenadas

    def consultar_acoes_impacto_exato(self, impacto_alvo: float) -> List[Acao]:
        """
        Utiliza travessia binária para encontrar ações que tenham exato grau de impacto.

        :param impacto_alvo: Valor numérico do impacto a pesquisar.
        :type impacto_alvo: float
        :return: Lista de ações com o valor exigido.
        :rtype: List[Acao]
        """
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
        """
        Devolve o menor e o maior nó (extremos esquerda e direita da BST).

        :return: Um tuplo contendo as ações com menor impacto e as de maior impacto.
        :rtype: Tuple[List[Acao], List[Acao]]
        """
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
        """
        Percorre recursivamente a BST extraindo ações dentro da "Range" exigida.

        :param min_imp: Limite inferior do intervalo pretendido.
        :type min_imp: float
        :param max_imp: Limite superior de impacto.
        :type max_imp: float
        :return: A lista de ações filtrada.
        :rtype: List[Acao]
        """
        arvore = self._construir_bst_impacto()
        resultados: List[Acao] = []
        
        def _busca_intervalo(no: Any) -> None:
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

    # ====================================================================
    # RF08 - PRIORIZAÇÃO DE CANDIDATURAS DE VOLUNTÁRIOS A AÇÕES (MAX-HEAP)
    # ====================================================================
    
    def _calcular_pontuacao_compatibilidade(self, voluntario: Voluntario, acao: Acao) -> int:
        """
        Lógica base da compatibilidade onde ODS em comum contam 2 pontos 
        e competências partilhadas pontuam 1.

        :param voluntario: O voluntário pendente de avaliação.
        :type voluntario: Voluntario
        :param acao: A ação na qual o voluntário quer intervir.
        :type acao: Acao
        :return: Pontos de aptidão/compatibilidade baseados na interseção de ODS/Competências.
        :rtype: int
        """
        pontos = 0
        ods_em_comum = voluntario.ods_interesse.intersection(acao.ods_associados)
        pontos += (len(ods_em_comum) * 2)
        
        comps_voluntario = set(voluntario.competencias.keys())
        comps_acao = set(acao.competencias_desejadas.keys())
        comps_em_comum = comps_voluntario.intersection(comps_acao)
        pontos += len(comps_em_comum)
        
        return pontos

    def gerar_candidaturas_ordenadas_heapsort(self, titulo_acao: str) -> List[Tuple[Inscricao, int]]:
        """
        Aplica a lógica de ponderação de candidaturas, atribuindo desempates baseados em Data 
        e entregando a ordenação em lista ao algoritmo genérico de Heap Sort isolado no Gestor.

        :param titulo_acao: Título da ação com inscrições em Fila pendente.
        :type titulo_acao: str
        :return: Lista das candidaturas estruturada ordenadamente.
        :rtype: List[Tuple[Inscricao, int]]
        """
        acao = self.consultar_acao(titulo_acao)
        if not acao or acao.fila_inscricoes.is_empty():
            return []

        # 1. Esvaziar a fila temporariamente 
        inscricoes_pendentes: List[Inscricao] = []
        while not acao.fila_inscricoes.is_empty():
            insc = acao.fila_inscricoes.dequeue()
            if insc:
                inscricoes_pendentes.append(insc)

        # 2. Ordenar por data para o bónus de antiguidade 
        inscricoes_pendentes.sort(key=lambda x: x.data_hora_inscricao)
        total_pendentes = len(inscricoes_pendentes)

        # 3. Calcular a pontuação com o truque decimal e aglomerar lista 
        elementos_para_ordenar: List[Tuple[float, Inscricao]] = []
        for i, insc in enumerate(inscricoes_pendentes):
            voluntario = self.consultar_voluntario(insc.voluntario)
            if voluntario:
                pontos_base = self._calcular_pontuacao_compatibilidade(voluntario, acao)
            else:
                pontos_base = 0 
                
            bonus_antiguidade = (total_pendentes - i) / (total_pendentes + 1)
            prioridade_exata = float(pontos_base + bonus_antiguidade)
            elementos_para_ordenar.append((prioridade_exata, insc))

        # 4. Extrair no algoritmo abstrato e reconstruir fila
        candidaturas_brutas = heap_sort(elementos_para_ordenar)

        # 5. Limpar os decimais e repor
        inscricoes_ordenadas: List[Tuple[Inscricao, int]] = []
        for prioridade_exata, insc in candidaturas_brutas:
            pontos_limpos = int(prioridade_exata)
            inscricoes_ordenadas.append((insc, pontos_limpos))
            
        for insc in inscricoes_pendentes:
            acao.fila_inscricoes.enqueue(insc)

        return inscricoes_ordenadas
    
    # ====================================================================
    # RF14 - GESTÃO DA REDE DE ENTIDADES (GRAFOS)
    # ====================================================================

    def reconstruir_rede_entidades(self) -> None:
        """
        Reconstrói o grafo do zero. 
        Duas entidades estão ligadas se participarem na mesma ação.
        O peso da ligação é o número de ações que têm em comum.
        
        Nota: Cumpre rigorosamente o OR07 ao não utilizar o módulo itertools.
        """
        self.rede_entidades = Grafo()
        
        # 1. Adicionar todas as entidades válidas como nós do grafo
        for nome_entidade in self.entidades.keys():
            self.rede_entidades.adicionar_entidade(nome_entidade.lower())

        # 2. Iterar sobre todas as ações para criar as ligações
        ligacoes_contagem = {}
        for acao in self.acoes.values():
            # Convertemos as entidades da ação para uma lista indexável
            lista_entidades = list(acao.entidades)
            n = len(lista_entidades)
            
            for i in range(n):
                for j in range(i + 1, n):
                    ent1 = lista_entidades[i].lower()
                    ent2 = lista_entidades[j].lower()
                    
                    # Ordenar alfabeticamente para garantir consistência bidirecional
                    par_ordenado = tuple(sorted([ent1, ent2]))
                    ligacoes_contagem[par_ordenado] = ligacoes_contagem.get(par_ordenado, 0) + 1

        # 3. Inserir as ligações com os pesos (ações em comum) no Grafo
        for (ent1, ent2), peso in ligacoes_contagem.items():
            self.rede_entidades.adicionar_ligacao(ent1, ent2, peso)

    # ====================================================================
    # RF15 - CAMINHO MAIS CURTO E CENTRALIDADE
    # ====================================================================

    def pesquisar_caminho_curto_entidades(self, ent1: str, ent2: str) -> Optional[List[str]]:
        """
        Encontra o caminho mais curto (menos vértices) usando o algoritmo BFS abstrato.
        """
        self.reconstruir_rede_entidades() # Garante que a rede está atualizada
        return caminho_mais_curto_bfs(self.rede_entidades.adjacencias, ent1.lower(), ent2.lower())

    def calcular_centralidade_rede(self) -> List[Tuple[str, float]]:
        """
        Calcula a proximidade de todas as entidades usando a distância geodésica.
        """
        self.reconstruir_rede_entidades()
        centralidades = []

        for entidade in self.rede_entidades.adjacencias.keys():
            soma_dist = soma_distancias_geodesicas_bfs(self.rede_entidades.adjacencias, entidade)
            proximidade = (1.0 / soma_dist) if soma_dist > 0 else 0.0
            
            # Formatar nome original para exibição bonita
            obj_ent = self.consultar_entidade(entidade)
            nome_display = obj_ent.nome if obj_ent else entidade.title()
            
            centralidades.append((nome_display, proximidade))

        # Ordenar por proximidade descendente
        centralidades.sort(key=lambda x: x[1], reverse=True)
        return centralidades

    # ====================================================================
    # RF16 (OPCIONAL) - VISUALIZAÇÃO DA REDE (NETWORKX)
    # ====================================================================

    def visualizar_rede_parceiros(self) -> None:
        """
        Renderiza graficamente a teia da rede de entidades usando NetworkX e Matplotlib.
        Implementa posicionamento radial e pesos descentralizados para evitar sobreposições.
        """
        self.reconstruir_rede_entidades()
        nx_grafo = nx.Graph()

        # 1. Adicionar nós e arestas ao NetworkX
        for entidade, vizinhos in self.rede_entidades.adjacencias.items():
            nx_grafo.add_node(entidade)
            for vizinho, peso in vizinhos.items():
                nx_grafo.add_edge(entidade, vizinho, weight=peso)

        if len(nx_grafo.nodes) == 0:
            print("A rede de entidades está vazia. Não é possível gerar o gráfico.")
            return

        # 2. Layout (Molas bem fortes para espalhar os nós ao máximo)
        pos = nx.spring_layout(nx_grafo, k=2.0, iterations=300, seed=42)

        plt.figure(figsize=(16, 10))
        plt.title("Visualização da Rede de Parcerias entre Entidades (RF16)", fontsize=16, fontweight='bold', color='#005b96')
        
        # 3. DESENHAR ARESTAS (LINHAS)
        if len(nx_grafo.edges()) > 0:
            # Linhas mais finas e ligeiramente transparentes para deixar o texto respirar
            nx.draw_networkx_edges(
                nx_grafo, pos, width=1.5, edge_color='black', alpha=0.5
            )
            
            # 4. DESENHAR OS PESOS (NÚMEROS) - Desviados do centro
            rotulos_arestas = {(u, v): str(d['weight']) for u, v, d in nx_grafo.edges(data=True)}
            nx.draw_networkx_edge_labels(
                nx_grafo, pos,
                edge_labels=rotulos_arestas,
                font_color='red',
                font_size=10,
                font_weight='bold',
                label_pos=0.65, # TRUQUE: 0.65 afasta os números do cruzamento central
                bbox=dict(boxstyle="circle,pad=0.15", edgecolor="red", facecolor="white", alpha=0.9)
            )
        
        # 5. DESENHAR NÓS - Tamanho fixo
        nx.draw_networkx_nodes(
            nx_grafo, pos, 
            node_size=300, 
            node_color='#87CEEB', 
            edgecolors='black', 
            linewidths=1.5
        )
        
        # 6. MATEMÁTICA RADIAL PARA OS RÓTULOS DOS NÓS
        rotulos = {no: no.title() for no in nx_grafo.nodes()}
        
        # Calcula o centro de massa do grafo
        cx = sum([v[0] for v in pos.values()]) / len(pos)
        cy = sum([v[1] for v in pos.values()]) / len(pos)
        
        pos_labels = {}
        for k_no, v_coord in pos.items():
            # Vetor desde o centro até ao nó
            dx = v_coord[0] - cx
            dy = v_coord[1] - cy
            dist = (dx**2 + dy**2)**0.5
            
            if dist > 0.01:
                # Empurra o texto para fora do centro
                pos_labels[k_no] = [v_coord[0] + (dx/dist)*0.08, v_coord[1] + (dy/dist)*0.08]
            else:
                pos_labels[k_no] = [v_coord[0], v_coord[1] + 0.08]
        
        nx.draw_networkx_labels(
            nx_grafo, pos_labels, labels=rotulos, font_size=8, font_weight='bold',
            bbox=dict(boxstyle="round,pad=0.2", edgecolor="none", facecolor="white", alpha=0.9)
        )

        plt.axis('off')
        plt.tight_layout()
        plt.show()