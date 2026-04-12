from typing import List, Optional

class Entidade:
    """Representa uma entidade promotora de ações."""
    def __init__(self, nome: str, tipo: str, area: str, localizacao: str, url: Optional[str] = None):
        self.nome = nome
        self.tipo = tipo
        self.area = area
        self.localizacao = localizacao
        self.url = url
        self.tags: List[str] = []
        self.ods_foco: List[int] = []

    def adicionar_tag(self, tag: str) -> bool:
        """Adiciona uma tag à entidade com limite máximo de 6."""
        tag_limpa = tag.strip()
        if tag_limpa and tag_limpa not in self.tags and len(self.tags) < 6:
            self.tags.append(tag_limpa)
            return True
        return False

    def adicionar_ods_foco(self, ods_id: int) -> bool:
        """Adiciona um ODS principal (1..17) com limite de 5."""
        if 1 <= ods_id <= 17 and ods_id not in self.ods_foco and len(self.ods_foco) < 5:
            self.ods_foco.append(ods_id)
            return True
        return False