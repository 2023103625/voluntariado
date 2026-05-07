"""
Módulo principal de inicialização da aplicação.

Este módulo é responsável por configurar o ambiente, carregar os dados
persistentes, iniciar a interface de terminal e garantir que os dados
são guardados de forma segura ao encerrar. Cumpre a exigência do pacote 'main'.
"""

import os
import sys

# Garante que o Python encontra as pastas do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sistema.gestor import SistemaVoluntariado
from interface.menu import MenuTerminal


def main() -> None:
    """
    Função principal que inicia a aplicação de voluntariado.

    Executa o fluxo principal passo a passo:
    1. Instancia o Gestor Central (SistemaVoluntariado).
    2. Carrega os dados persistentes a partir de ficheiros JSON (OR02).
    3. Inicializa e apresenta o menu interativo no terminal.
    4. Guarda o estado do sistema ao encerrar a aplicação.

    :return: Nada.
    :rtype: None
    """
    caminho_dados: str = os.path.join('dados', 'json')
    
    # 1. Cria o objeto que caracteriza o sistema principal
    sistema: SistemaVoluntariado = SistemaVoluntariado()
    
    # 2. Carrega os dados para a memória (OR02)
    sistema.carregar_sistema(caminho_dados)
    
    # 3. Inicia a interface com o utilizador
    interface: MenuTerminal = MenuTerminal(sistema)
    interface.mostrar_menu_principal()
    
    # 4. Atualiza e guarda os ficheiros no final da execução (OR02)
    sistema.guardar_sistema(caminho_dados)


if __name__ == "__main__":
    main()