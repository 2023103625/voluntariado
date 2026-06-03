"""
Módulo de modelo para ações de voluntariado.

Este módulo define a classe Acao, que representa uma unidade de trabalho
social no sistema, gerindo as suas inscrições e equipas.
"""

from typing import List, Dict, Set
from sistema.estruturas.fila import Fila
from sistema.modelos.inscricao import Inscricao
from sistema.estruturas.pilha import Pilha
from sistema.constantes import EstadoAcao


class Acao:
    """
    Representa uma ação de voluntariado no sistema.

    Esta classe gere os dados base da ação, bem como o fluxo de inscrições
    através de uma fila FIFO e a gestão de equipas com suporte a histórico.

    :param titulo: Título descritivo da ação.
    :type titulo: str
    :param entidade: Nome da entidade promotora da ação.
    :type entidade: str
    :param data_hora: Data e hora da ação (formato ISO YYYY-MM-DD HH:MM).
    :type data_hora: str
    :param duracao: Duração prevista da ação em horas.
    :type duracao: int
    :param vagas: Número de vagas totais disponíveis (mínimo 0).
    :type vagas: int
    :param localizacao: Local da ação (campus, externo ou online).
    :type localizacao: str
    :param area: Área temática da intervenção social.
    :type area: str
    """

    def __init__(
        self,
        titulo: str,
        entidades: List[str],
        data_hora: str,
        duracao: int,
        vagas: int,
        localizacao: str,
        area: str = "",
    ) -> None:
        """
        Inicializa uma nova instância de Acao.
        """
        self.titulo: str = titulo
        self.entidades: Set[str] = set(entidades)
        self.area: str = area
        self.data_hora: str = data_hora
        self.duracao: int = duracao
        self.vagas: int = max(0, vagas)
        self.localizacao: str = localizacao
        self.estado: EstadoAcao = EstadoAcao.PLANEADA
        self.metrica_impacto: float = 0.0

        # Atributos complexos (TDA e Coleções)
        self.competencias_desejadas: Dict[str, int] = {}
        self.ods_associados: Set[int] = set()
        self.equipa: Set[str] = set()
        self.historico_equipa: Pilha = Pilha()

        # RF02: Fila FIFO para gestão de inscrições pendentes
        self.fila_inscricoes: Fila = Fila()

        # Lista de inscrições validadas (aprovadas)
        self.inscricoes_aprovadas: List[Inscricao] = []

    def __str__(self) -> str:
        """
        Retorna uma representação textual resumida da ação.

        :return: Título, data e vagas da ação.
        :rtype: str
        """
        return f"Ação: {self.titulo} ({self.data_hora}) - Vagas: {self.vagas}"

    def adicionar_competencia(self, nome: str, nivel_minimo: int) -> bool:
        """
        Adiciona uma competência necessária à ação, validando os limites.

        Garante que a ação não ultrapassa as 6 competências e que o nível
        está entre 1 e 5.

        :param nome: Nome da competência (ex: "Programação").
        :type nome: str
        :param nivel_minimo: Nível de proficiência exigido (1 a 5).
        :type nivel_minimo: int
        :return: True se a competência foi adicionada, False caso contrário.
        :rtype: bool
        """
        if len(self.competencias_desejadas) < 6 and 1 <= nivel_minimo <= 5:
            self.competencias_desejadas[nome] = nivel_minimo
            return True
        return False

    def adicionar_ods(self, ods_id: int) -> bool:
        """
        Associa um Objetivo de Desenvolvimento Sustentável (ODS) à ação.

        Uma ação pode estar associada a um máximo de 3 ODS (entre 1 e 17).

        :param ods_id: Identificador numérico do ODS (1 a 17).
        :type ods_id: int
        :return: True se o ODS foi associado com sucesso, False caso contrário.
        :rtype: bool
        """
        if 1 <= ods_id <= 17 and len(self.ods_associados) < 3:
            if ods_id not in self.ods_associados:
                self.ods_associados.add(ods_id)
                return True
        return False