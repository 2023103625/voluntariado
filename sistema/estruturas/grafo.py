# Criar ficheiro: sistema/estruturas/grafo.py
from typing import Dict

class Grafo:
    """
    TDA Grafo: Implementação de um Grafo Não Direcionado e Pesado 
    através de Listas de Adjacências (Dicionários).
    """

    def __init__(self) -> None:
        # { 'EntidadeA': {'EntidadeB': peso_ab, 'EntidadeC': peso_ac} }
        self.adjacencias: Dict[str, Dict[str, int]] = {}

    def adicionar_entidade(self, nome_entidade: str) -> bool:
        if nome_entidade not in self.adjacencias:
            self.adjacencias[nome_entidade] = {}
            return True
        return False

    def remover_entidade(self, nome_entidade: str) -> bool:
        if nome_entidade not in self.adjacencias:
            return False
        # Remove a entidade das listas de adjacências dos vizinhos
        for vizinho in self.adjacencias[nome_entidade]:
            if nome_entidade in self.adjacencias[vizinho]:
                del self.adjacencias[vizinho][nome_entidade]
        # Remove o vértice
        del self.adjacencias[nome_entidade]
        return True

    def adicionar_ligacao(self, ent1: str, ent2: str, peso: int) -> bool:
        """Adiciona ou atualiza o peso da ligação entre duas entidades."""
        if ent1 in self.adjacencias and ent2 in self.adjacencias and ent1 != ent2:
            self.adjacencias[ent1][ent2] = peso
            self.adjacencias[ent2][ent1] = peso
            return True
        return False

    def remover_ligacao(self, ent1: str, ent2: str) -> bool:
        """Remove a ligação bidirecional entre duas entidades."""
        removido = False
        if ent1 in self.adjacencias and ent2 in self.adjacencias[ent1]:
            del self.adjacencias[ent1][ent2]
            removido = True
        if ent2 in self.adjacencias and ent1 in self.adjacencias[ent2]:
            del self.adjacencias[ent2][ent1]
            removido = True
        return removido