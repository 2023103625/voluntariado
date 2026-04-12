import os
import sys

# Garante que o Python encontra as pastas do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sistema.gestor import SistemaVoluntariado
from interface.menu import MenuTerminal

def main():
    """
    Função principal que inicia a aplicação.
    Cumpre a estrutura exigida para o pacote 'main'.
    """
    caminho_dados = os.path.join('dados', 'json')
    
    # 1. Cria o objeto que caracteriza o sistema
    sistema = SistemaVoluntariado()
    
    # 2. Carrega os dados (OR02)
    sistema.carregar_sistema(caminho_dados)
    
    # 3. Inicia a interface com o utilizador
    interface = MenuTerminal(sistema)
    interface.mostrar_menu_principal()
    
    # 4. Atualiza e guarda os ficheiros no final da execução (OR02)
    sistema.guardar_sistema(caminho_dados)

if __name__ == "__main__":
    main()