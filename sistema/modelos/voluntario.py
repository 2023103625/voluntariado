"""Modelo de domínio para voluntários."""

from typing import List, Dict, Optional


class Voluntario:
    """Representa um voluntário no sistema universitário.

    :param nome: Nome completo do voluntário.
    :param curso: Curso associado ao voluntário.
    :param faculdade: Faculdade de pertença.
    :param vinculo: Tipo de vínculo institucional (estudante/docente/tecnico).
    :param ano: Ano letivo, aplicável apenas a estudantes.
    """

    def __init__(
        self,
        nome: str,
        curso: str,
        faculdade: str,
        vinculo: str,
        ano: Optional[int] = None,
    ):
        self.nome = nome
        self.curso = curso
        self.faculdade = faculdade
        self.vinculo = vinculo
        self.ano = ano if vinculo == "estudante" else None
        self.competencias: Dict[str, int] = {}
        self.interesses: List[str] = []
        self.ods_interesse: List[int] = []

    def adicionar_competencia(self, nome: str, nivel: int) -> bool:
        """Adiciona uma competência do voluntário.

        Regras:

        - máximo de 8 competências;
        - nível entre 1 e 5.

        :param nome: Nome da competência.
        :param nivel: Nível da competência (1..5).
        :return: ``True`` se foi adicionada; caso contrário ``False``.
        """
        if len(self.competencias) < 8 and 1 <= nivel <= 5:
            self.competencias[nome] = nivel
            return True
        return False

    def adicionar_interesse(self, interesse: str) -> bool:
        """Adiciona uma tag de interesse.

        Regras:

        - tag não vazia;
        - sem duplicados;
        - máximo de 6 tags.

        :param interesse: Texto da tag.
        :return: ``True`` se foi adicionada; caso contrário ``False``.
        """
        interesse_limpo = interesse.strip()
        if (
            interesse_limpo
            and interesse_limpo not in self.interesses
            and len(self.interesses) < 6
        ):
            self.interesses.append(interesse_limpo)
            return True
        return False

    def adicionar_ods_interesse(self, ods_id: int) -> bool:
        """Adiciona um ODS de interesse.

        Regras:

        - ODS entre 1 e 17;
        - sem duplicados;
        - máximo de 3 ODS.

        :param ods_id: Identificador numérico do ODS.
        :return: ``True`` se foi adicionado; caso contrário ``False``.
        """
        if 1 <= ods_id <= 17 and ods_id not in self.ods_interesse and len(self.ods_interesse) < 3:
            self.ods_interesse.append(ods_id)
            return True
        return False