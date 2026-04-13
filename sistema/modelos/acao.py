"""Modelo de domínio para ações de voluntariado."""

from typing import List, Dict
from sistema.estruturas.fila import Fila


class Acao:
    """Representa uma ação de voluntariado.

    :param titulo: Título da ação.
    :param entidade: Nome da entidade promotora.
    :param data_hora: Data/hora da ação (``YYYY-MM-DD HH:MM``).
    :param duracao: Duração estimada em horas.
    :param vagas: Número de vagas disponíveis (>= 0).
    :param localizacao: Localização da ação (campus/externo/online).
    :param area: Área temática da ação.
    """

    def __init__(
        self,
        titulo: str,
        entidade: str,
        data_hora: str,
        duracao: int,
        vagas: int,
        localizacao: str,
        area: str = "",
    ):
        self.titulo = titulo
        self.entidade = entidade
        self.area = area
        self.data_hora = data_hora
        self.duracao = duracao
        self.vagas = max(0, vagas)
        self.localizacao = localizacao
        self.estado = "planeada"
        self.metrica_impacto = 0.0

        self.competencias_desejadas: Dict[str, int] = {}
        self.ods_associados: List[int] = []

        # RF02: fila FIFO para inscrições pendentes
        self.fila_inscricoes = Fila()
        self.inscricoes_aprovadas: List['Inscricao'] = []

    def __str__(self) -> str:
        """Retorna uma representação legível da ação."""
        return f"Ação: {self.titulo} ({self.data_hora}) - Vagas: {self.vagas}"

    def adicionar_competencia(self, nome: str, nivel_minimo: int) -> bool:
        """Adiciona competência desejada da ação.

        Regras:

        - máximo de 6 competências;
        - nível mínimo entre 1 e 5.

        :param nome: Nome da competência.
        :param nivel_minimo: Nível mínimo exigido.
        :return: ``True`` se foi adicionada; caso contrário ``False``.
        """
        if len(self.competencias_desejadas) < 6 and 1 <= nivel_minimo <= 5:
            self.competencias_desejadas[nome] = nivel_minimo
            return True
        return False

    def adicionar_ods(self, ods_id: int) -> bool:
        """Adiciona ODS associado à ação.

        Regras:

        - ODS entre 1 e 17;
        - sem duplicados;
        - máximo de 3 ODS.

        :param ods_id: Identificador numérico do ODS.
        :return: ``True`` se foi adicionado; caso contrário ``False``.
        """
        if 1 <= ods_id <= 17 and len(self.ods_associados) < 3 and ods_id not in self.ods_associados:
            self.ods_associados.append(ods_id)
            return True
        return False