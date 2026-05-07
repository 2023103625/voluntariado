"""
Módulo de modelo para entidades promotoras.

Este módulo define a classe Entidade, que representa as organizações
parceiras (núcleos, associações, ONG) que promovem ações de voluntariado.
"""

from typing import Optional, Set


class Entidade:
    """
    Representa uma entidade promotora de ações de voluntariado.

    Gere a informação institucional da entidade, bem como as suas
    tags descritivas e áreas de foco em relação aos ODS.

    :param nome: Nome completo da entidade.
    :type nome: str
    :param tipo: Classificação da entidade (ex: núcleo, associação, serviço, ONG).
    :type tipo: str
    :param area: Área temática principal de intervenção.
    :type area: str
    :param localizacao: Morada ou localização base da entidade.
    :type localizacao: str
    :param url: Endereço do website ou página da entidade (opcional).
    :type url: Optional[str]
    """

    def __init__(
        self,
        nome: str,
        tipo: str,
        area: str,
        localizacao: str,
        url: Optional[str] = None,
    ) -> None:
        """
        Inicializa uma nova instância de Entidade.
        """
        self.nome: str = nome
        self.tipo: str = tipo
        self.area: str = area
        self.localizacao: str = localizacao
        self.url: Optional[str] = url
        
        # Atributos complexos (Coleções)
        self.tags: Set[str] = set()
        self.ods_foco: Set[int] = set()

    def adicionar_tag(self, tag: str) -> bool:
        """
        Adiciona uma tag descritiva à entidade usando um Conjunto (Set).

        Regras de validação:
        - A tag não pode ser vazia após limpeza de espaços.
        - Não permite duplicados.
        - A entidade pode ter um máximo de 6 tags.

        :param tag: Texto da tag a ser adicionada.
        :type tag: str
        :return: True se a tag foi adicionada com sucesso, False caso contrário.
        :rtype: bool
        """
        tag_limpa = tag.strip()
        if tag_limpa and len(self.tags) < 6:
            if tag_limpa not in self.tags:
                self.tags.add(tag_limpa)
                return True
        return False

    def adicionar_ods_foco(self, ods_id: int) -> bool:
        """
        Adiciona um ODS principal à entidade usando um Conjunto (Set).

        Regras de validação:
        - O ID do ODS deve estar entre 1 e 17.
        - Não permite ODS duplicados.
        - A entidade pode ter um máximo de 5 ODS de foco.

        :param ods_id: Identificador numérico do ODS.
        :type ods_id: int
        :return: True se o ODS foi adicionado com sucesso, False caso contrário.
        :rtype: bool
        """
        if 1 <= ods_id <= 17 and len(self.ods_foco) < 5:
            if ods_id not in self.ods_foco:
                self.ods_foco.add(ods_id)
                return True
        return False