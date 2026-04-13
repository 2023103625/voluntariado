"""Modelo de domínio para entidades promotoras."""

from typing import List, Optional


class Entidade:
    """Representa uma entidade promotora de ações.

    :param nome: Nome da entidade.
    :param tipo: Tipo (núcleo, associação, serviço, ONG parceira, etc.).
    :param area: Área de intervenção principal.
    :param localizacao: Localização da entidade.
    :param url: URL institucional (opcional).
    """

    def __init__(
        self,
        nome: str,
        tipo: str,
        area: str,
        localizacao: str,
        url: Optional[str] = None,
    ):
        self.nome = nome
        self.tipo = tipo
        self.area = area
        self.localizacao = localizacao
        self.url = url
        self.tags: List[str] = []
        self.ods_foco: List[int] = []

    def adicionar_tag(self, tag: str) -> bool:
        """Adiciona uma tag da entidade.

        Regras:

        - tag não vazia;
        - sem duplicados;
        - máximo de 6 tags.

        :param tag: Texto da tag.
        :return: ``True`` se foi adicionada; caso contrário ``False``.
        """
        tag_limpa = tag.strip()
        if tag_limpa and tag_limpa not in self.tags and len(self.tags) < 6:
            self.tags.append(tag_limpa)
            return True
        return False

    def adicionar_ods_foco(self, ods_id: int) -> bool:
        """Adiciona ODS principal da entidade.

        Regras:

        - ODS entre 1 e 17;
        - sem duplicados;
        - máximo de 5 ODS.

        :param ods_id: Identificador numérico do ODS.
        :return: ``True`` se foi adicionado; caso contrário ``False``.
        """
        if 1 <= ods_id <= 17 and ods_id not in self.ods_foco and len(self.ods_foco) < 5:
            self.ods_foco.append(ods_id)
            return True
        return False