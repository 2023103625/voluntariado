from typing import List, Dict, Optional

class Voluntario:
    """Representa um voluntário no sistema universitário."""
    def __init__(self, nome: str, curso: str, faculdade: str, 
                 vinculo: str, ano: Optional[int] = None):
        self.nome = nome
        self.curso = curso
        self.faculdade = faculdade
        self.vinculo = vinculo
        self.ano = ano if vinculo == "estudante" else None
        self.competencias: Dict[str, int] = {}
        self.interesses: List[str] = []
        self.ods_interesse: List[int] = []

    def adicionar_competencia(self, nome: str, nivel: int) -> bool:
        """Adiciona uma competência com limite de 8 e nível entre 1 e 5."""
        if len(self.competencias) < 8 and 1 <= nivel <= 5:
            self.competencias[nome] = nivel
            return True
        return False

    def adicionar_interesse(self, interesse: str) -> bool:
        """Adiciona uma tag de interesse com limite de 6."""
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
        """Adiciona ODS de interesse (1..17) com limite de 3."""
        if 1 <= ods_id <= 17 and ods_id not in self.ods_interesse and len(self.ods_interesse) < 3:
            self.ods_interesse.append(ods_id)
            return True
        return False