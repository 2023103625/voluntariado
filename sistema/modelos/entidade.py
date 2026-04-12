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