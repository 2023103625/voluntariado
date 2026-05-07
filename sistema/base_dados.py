"""
Módulo de persistência de dados em formato JSON.

Este módulo fornece a classe BaseDados, que centraliza as operações de 
leitura e escrita no sistema de ficheiros, cumprindo o requisito OR02.
"""

import json
import os
from typing import Dict, Any, Union, List


class BaseDados:
    """
    Responsável pela persistência e carregamento de dados do sistema.

    Esta classe utiliza métodos estáticos para interagir com o formato JSON,
    garantindo que a estrutura de dados da memória é preservada em disco.
    """

    @staticmethod
    def carregar_dados(caminho_ficheiro: str) -> Union[Dict[str, Any], List[Any]]:
        """
        Lê um ficheiro JSON e converte-o para estruturas nativas de Python.

        Se o ficheiro não existir ou estiver corrompido, retorna um 
        dicionário vazio para evitar falhas em cascata no sistema.

        :param caminho_ficheiro: Caminho relativo ou absoluto para o ficheiro.
        :type caminho_ficheiro: str
        :return: Dicionário ou Lista com os dados lidos.
        :rtype: Union[Dict[str, Any], List[Any]]
        """
        if not os.path.exists(caminho_ficheiro):
            print(f"Aviso: Ficheiro {caminho_ficheiro} não encontrado. Será iniciado vazio.")
            return {}
        
        try:
            with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Erro Crítico: O ficheiro {caminho_ficheiro} tem um formato JSON inválido.")
            return {}
        except Exception as e:
            print(f"Erro inesperado ao carregar dados: {e}")
            return {}

    @staticmethod
    def guardar_dados(caminho_ficheiro: str, dados: Any) -> bool:
        """
        Serializa e guarda os dados do sistema num ficheiro JSON.

        Garante automaticamente a criação das pastas necessárias (breadcrumbs)
        antes da escrita e utiliza indentação para legibilidade humana.

        :param caminho_ficheiro: Caminho de destino para o ficheiro JSON.
        :type caminho_ficheiro: str
        :param dados: Estrutura de dados (Dict/List) a ser persistida.
        :type dados: Any
        :return: True se a gravação foi bem-sucedida, False caso contrário.
        :rtype: bool
        """
        try:
            # Garante que a pasta de destino existe
            pasta = os.path.dirname(caminho_ficheiro)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
                
            with open(caminho_ficheiro, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao guardar os dados em {caminho_ficheiro}: {e}")
            return False