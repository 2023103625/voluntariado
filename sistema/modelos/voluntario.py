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
        if len(self.competencias) < 8 and 1 <= nivel <= 5:
            self.competencias[nome] = nivel
            return True
        return False