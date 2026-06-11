from typing import Dict

class Grafo:
    """
    TDA Grafo: Implementação de um Grafo Não Direcionado e Pesado 
    através de Listas de Adjacências (Dicionários).
    """

    def __init__(self) -> None:
        """
        Inicializa a estrutura do grafo vazio.

        :return: Nenhum valor de retorno.
        :rtype: None
        """
        self.adjacencias: Dict[str, Dict[str, int]] = {}

    def adicionar_entidade(self, nome_entidade: str) -> bool:
        """
        Adiciona uma nova entidade (vértice) ao grafo, se esta ainda não existir.

        :param nome_entidade: O identificador único da entidade a ser adicionada.
        :type nome_entidade: str
        :return: True se a entidade foi adicionada com sucesso, False se já existia no grafo.
        :rtype: bool
        """
        
        if nome_entidade not in self.adjacencias:
            self.adjacencias[nome_entidade] = {}
            return True
            
        return False

    def remover_entidade(self, nome_entidade: str) -> bool:
        """
        Remove uma entidade do grafo, bem como todas as ligações (arestas) associadas a ela.

        :param nome_entidade: O identificador da entidade a ser removida.
        :type nome_entidade: str
        :return: True se a entidade foi encontrada e removida, False se não existia no grafo.
        :rtype: bool
        """
        # Retorna falso imediatamente se a entidade não faz parte do grafo
        if nome_entidade not in self.adjacencias:
            return False
            
        # 1. Percorre todos os vizinhos da entidade que será removida
        for vizinho in self.adjacencias[nome_entidade]:
            # 2. Garante que a entidade existe na lista do vizinho antes de tentar apagar
            if nome_entidade in self.adjacencias[vizinho]:
                del self.adjacencias[vizinho][nome_entidade]
                
        # 3. Finalmente, remove a entidade principal da estrutura do grafo
        del self.adjacencias[nome_entidade]
        return True

    def adicionar_ligacao(self, ent1: str, ent2: str, peso: int) -> bool:
        """
        Adiciona ou atualiza o peso da ligação bidirecional entre duas entidades.

        :param ent1: O identificador da primeira entidade.
        :type ent1: str
        :param ent2: O identificador da segunda entidade.
        :type ent2: str
        :param peso: O valor (peso) associado à ligação entre as duas entidades.
        :type peso: int
        :return: True se a ligação foi estabelecida, False se alguma das entidades não existir ou se forem a mesma entidade.
        :rtype: bool
        """
        # Valida se ambas as entidades existem e previne auto-loops (ligação de uma entidade para si mesma)
        if ent1 in self.adjacencias and ent2 in self.adjacencias and ent1 != ent2:
            # Como o grafo é não direcionado, a ligação ocorre nos dois sentidos
            self.adjacencias[ent1][ent2] = peso
            self.adjacencias[ent2][ent1] = peso
            return True
            
        return False

    def remover_ligacao(self, ent1: str, ent2: str) -> bool:
        """
        Remove a ligação bidirecional existente entre duas entidades.

        :param ent1: O identificador da primeira entidade.
        :type ent1: str
        :param ent2: O identificador da segunda entidade.
        :type ent2: str
        :return: True se a ligação foi removida em pelo menos um dos sentidos, False se não havia ligação.
        :rtype: bool
        """
        removido = False
        
        # Remove a referência da ent2 na lista de adjacências da ent1
        if ent1 in self.adjacencias and ent2 in self.adjacencias[ent1]:
            del self.adjacencias[ent1][ent2]
            removido = True
            
        # Remove a referência da ent1 na lista de adjacências da ent2
        if ent2 in self.adjacencias and ent1 in self.adjacencias[ent2]:
            del self.adjacencias[ent2][ent1]
            removido = True
            
        return removido