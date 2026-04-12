import json
import os
from typing import Dict, Any

class BaseDados:
    """
    Responsável por carregar e guardar os dados do sistema em formato JSON.
    Cumpre o requisito OR02.
    """

    @staticmethod
    def carregar_dados(caminho_ficheiro: str) -> Dict[str, Any]:
        """
        Lê um ficheiro JSON e retorna o seu conteúdo.

        :param caminho_ficheiro: Caminho para o ficheiro JSON.
        :return: Dicionário com os dados ou um dicionário vazio em caso de erro.
        """
        if not os.path.exists(caminho_ficheiro):
            print(f"Aviso: Ficheiro {caminho_ficheiro} não encontrado. Será criado um novo.")
            return {}
        
        try:
            with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Erro ao ler o ficheiro JSON. Formato inválido.")
            return {}

    @staticmethod
    def guardar_dados(caminho_ficheiro: str, dados: Dict[str, Any]) -> None:
        """
        Guarda os dados do sistema num ficheiro JSON.

        :param caminho_ficheiro: Caminho para o ficheiro JSON.
        :param dados: Dicionário com os dados a serem guardados.
        """
        # Garante que a pasta existe antes de guardar
        os.makedirs(os.path.dirname(caminho_ficheiro), exist_ok=True)
        with open(caminho_ficheiro, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)