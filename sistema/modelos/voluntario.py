"""
Módulo de modelo para voluntários.

Este módulo define a classe Voluntario, que representa os utilizadores
(estudantes, docentes ou técnicos) registados no programa de voluntariado.
"""

from typing import Dict, Optional, Set
from sistema.constantes import VinculoVoluntario


class Voluntario:
    """
    Representa um voluntário no sistema universitário.

    Gere a informação pessoal, o vínculo institucional e o perfil de
    competências e interesses do utilizador.

    :param nome: Nome completo do voluntário.
    :type nome: str
    :param curso: Curso ou departamento associado ao voluntário.
    :type curso: str
    :param faculdade: Faculdade de pertença.
    :type faculdade: str
    :param vinculo: Tipo de vínculo institucional (ex: estudante, docente, tecnico).
    :type vinculo: str
    :param ano: Ano letivo, aplicável e guardado apenas para estudantes.
    :type ano: Optional[int]
    """

    def __init__(
        self,
        nome: str,
        curso: str,
        faculdade: str,
        vinculo: str,
        ano: Optional[int] = None,
    ) -> None:
        """
        Inicializa uma nova instância de Voluntario.
        """
        self.nome: str = nome
        self.curso: str = curso
        self.faculdade: str = faculdade
        self.vinculo: str = vinculo
        
        # O ano só é gravado se o vínculo for efetivamente o de estudante
        self.ano: Optional[int] = ano if vinculo == VinculoVoluntario.ESTUDANTE else None
        
        # Atributos complexos (Coleções e Dicionários)
        self.competencias: Dict[str, int] = {}
        self.interesses: Set[str] = set()
        self.ods_interesse: Set[int] = set()

    def adicionar_competencia(self, nome: str, nivel: int) -> bool:
        """
        Adiciona ou atualiza uma competência do voluntário.

        Regras de validação:
        - O nível deve estar entre 1 e 5.
        - O voluntário pode registar um máximo de 8 competências.

        :param nome: Nome da competência (ex: "Programação").
        :type nome: str
        :param nivel: Nível de proficiência associado (1 a 5).
        :type nivel: int
        :return: True se a competência foi adicionada, False caso contrário.
        :rtype: bool
        """
        if len(self.competencias) < 8 and 1 <= nivel <= 5:
            self.competencias[nome] = nivel
            return True
        return False

    def adicionar_interesse(self, interesse: str) -> bool:
        """
        Adiciona uma tag de interesse ao perfil usando um Conjunto (Set).

        Regras de validação:
        - A tag não pode ser vazia após limpeza de espaços.
        - Não permite interesses duplicados.
        - O voluntário pode ter um máximo de 6 tags de interesse.

        :param interesse: Texto representativo do interesse.
        :type interesse: str
        :return: True se o interesse foi adicionado com sucesso, False caso contrário.
        :rtype: bool
        """
        interesse_limpo = interesse.strip()
        if interesse_limpo and len(self.interesses) < 6:
            if interesse_limpo not in self.interesses:
                self.interesses.add(interesse_limpo)
                return True
        return False

    def adicionar_ods_interesse(self, ods_id: int) -> bool:
        """
        Adiciona um ODS de interesse ao perfil usando um Conjunto (Set).

        Regras de validação:
        - O ID do ODS deve estar entre 1 e 17.
        - Não permite ODS duplicados.
        - O voluntário pode escolher um máximo de 3 ODS.

        :param ods_id: Identificador numérico do ODS.
        :type ods_id: int
        :return: True se o ODS foi adicionado com sucesso, False caso contrário.
        :rtype: bool
        """
        if 1 <= ods_id <= 17 and len(self.ods_interesse) < 3:
            if ods_id not in self.ods_interesse:
                self.ods_interesse.add(ods_id)
                return True
        return False