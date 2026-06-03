"""
Módulo de estrutura de dados: Grafo (Rede de Entidades).

Implementa um Grafo Não Direcionado e Pesado usando Listas de Adjacências,
para gerir a rede de entidades parceiras e calcular caminhos mais curtos
e centralidade geodésica (RF14 e RF15).
"""

from typing import Dict, List, Optional, Tuple
from collections import deque

class Grafo:
    """
    Estrutura de dados que representa a Rede de Entidades.
    Os vértices são os nomes das entidades e as arestas representam as ações comuns.
    """

    def __init__(self) -> None:
        """Inicializa um grafo vazio usando um dicionário de adjacências."""
        # Estrutura: { 'EntidadeA': {'EntidadeB': peso_ab, 'EntidadeC': peso_ac} }
        self.adjacencias: Dict[str, Dict[str, int]] = {}

    # ==========================================
    # RF14 - GESTÃO DA REDE (CRUD)
    # ==========================================

    def adicionar_entidade(self, nome_entidade: str) -> bool:
        """Adiciona um novo vértice (entidade) ao grafo."""
        if nome_entidade not in self.adjacencias:
            self.adjacencias[nome_entidade] = {}
            return True
        return False

    def remover_entidade(self, nome_entidade: str) -> bool:
        """Remove um vértice e todas as ligações associadas a ele."""
        if nome_entidade not in self.adjacencias:
            return False
            
        # Remover a entidade da lista de vizinhos das outras entidades
        for vizinho in self.adjacencias[nome_entidade]:
            if nome_entidade in self.adjacencias[vizinho]:
                del self.adjacencias[vizinho][nome_entidade]
                
        # Remover o vértice principal
        del self.adjacencias[nome_entidade]
        return True

    def adicionar_ligacao(self, ent1: str, ent2: str, peso: int) -> bool:
        """Cria ou atualiza uma ligação bidirecional (aresta) entre duas entidades."""
        if ent1 in self.adjacencias and ent2 in self.adjacencias and ent1 != ent2:
            self.adjacencias[ent1][ent2] = peso
            self.adjacencias[ent2][ent1] = peso
            return True
        return False

    def remover_ligacao(self, ent1: str, ent2: str) -> bool:
        """Remove a ligação bidirecional entre duas entidades."""
        if ent1 in self.adjacencias and ent2 in self.adjacencias:
            removido = False
            if ent2 in self.adjacencias[ent1]:
                del self.adjacencias[ent1][ent2]
                removido = True
            if ent1 in self.adjacencias[ent2]:
                del self.adjacencias[ent2][ent1]
                removido = True
            return removido
        return False

    # ==========================================
    # RF15 - CAMINHO MAIS CURTO (BFS)
    # ==========================================

    def caminho_mais_curto(self, origem: str, destino: str) -> Optional[List[str]]:
        """
        Encontra o caminho mais curto (menos vértices) usando Breadth-First Search (BFS).
        O algoritmo iterativo explora a rede em "camadas", garantindo a distância geodésica mínima.
        """
        if origem not in self.adjacencias or destino not in self.adjacencias:
            return None

        # Fila guarda tuplos com o nó atual e o caminho percorrido até ele
        fila = deque([(origem, [origem])])
        visitados = set([origem])

        while fila:
            no_atual, caminho_percorrido = fila.popleft()

            if no_atual == destino:
                return caminho_percorrido

            for vizinho in self.adjacencias[no_atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append((vizinho, caminho_percorrido + [vizinho]))

        return None # Retorna None se não houver ligação possível

    # ==========================================
    # RF15 - CENTRALIDADE DE PROXIMIDADE (Closeness Centrality)
    # ==========================================

    def calcular_centralidade(self) -> List[Tuple[str, float]]:
        """
        Calcula o grau de proximidade de todas as entidades e devolve uma lista 
        ordenada decrescentemente. Proximidade = 1 / Soma_das_Distâncias_Geodésicas
        """
        centralidades = []

        for entidade in self.adjacencias:
            soma_distancias = self._soma_distancias_geodesicas(entidade)
            
            # Se a soma for 0 (a entidade está completamente isolada), a centralidade é 0
            if soma_distancias == 0:
                proximidade = 0.0
            else:
                proximidade = 1.0 / soma_distancias
                
            centralidades.append((entidade, proximidade))

        # Ordenar por proximidade de forma decrescente
        centralidades.sort(key=lambda x: x[1], reverse=True)
        return centralidades

    def _soma_distancias_geodesicas(self, inicio: str) -> int:
        """
        Método auxiliar que corre um BFS modificado para somar a distância
        mínima do vértice 'inicio' a todos os nós alcançáveis do grafo.
        """
        visitados = set([inicio])
        fila = deque([(inicio, 0)]) # Tuplo: (Nó, Distância da Origem)
        soma = 0

        while fila:
            no_atual, dist_atual = fila.popleft()
            soma += dist_atual

            for vizinho in self.adjacencias[no_atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append((vizinho, dist_atual + 1))

        return soma