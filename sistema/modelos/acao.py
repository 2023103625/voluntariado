from typing import List, Dict
from sistema.estruturas.fila import Fila
from sistema.modelos.inscricao import Inscricao

class Acao:
    """
    Representa uma ação de voluntariado.
    
    :ivar titulo: Título da ação.
    :ivar entidade: Entidade promotora.
    :ivar data_hora: Data e hora da realização (formato YYYY-MM-DD HH:MM).
    :ivar duracao: Duração estimada em horas.
    :ivar vagas: Número de vagas disponíveis (>= 0).
    :ivar localizacao: Local onde decorre a ação.
    :ivar fila_inscricoes: Fila (FIFO) com as inscrições pendentes para esta ação (RF02).
    """

    def __init__(self, titulo: str, entidade: str, data_hora: str, 
                 duracao: int, vagas: int, localizacao: str):
        self.titulo = titulo
        self.entidade = entidade
        self.data_hora = data_hora
        self.duracao = duracao
        self.vagas = max(0, vagas) # Garante que as vagas nunca são negativas
        self.localizacao = localizacao
        self.estado = "planeada"
        self.metrica_impacto = 0.0
        
        self.competencias_desejadas: Dict[str, int] = {}
        self.ods_associados: List[int] = []
        
        # RF02: Cada ação tem agora a sua própria fila de inscrições!
        self.fila_inscricoes = Fila()
        self.inscricoes_aprovadas: List['Inscricao'] = []
        
    def __str__(self) -> str:
        return f"Ação: {self.titulo} ({self.data_hora}) - Vagas: {self.vagas}"
    
    def adicionar_competencia(self, nome: str, nivel_minimo: int) -> bool:
        """Adiciona uma competência desejada validando o limite máximo de 6."""
        if len(self.competencias_desejadas) < 6 and 1 <= nivel_minimo <= 5:
            self.competencias_desejadas[nome] = nivel_minimo
            return True
        return False

    def adicionar_ods(self, ods_id: int) -> bool:
        """Adiciona um ODS validando o limite máximo de 3."""
        if len(self.ods_associados) < 3 and ods_id not in self.ods_associados:
            self.ods_associados.append(ods_id)
            return True
        return False