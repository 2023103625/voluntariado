"""
Módulo de funções utilitárias de input para a interface terminal.

Este módulo centraliza e isola todas as validações de entrada 
do utilizador, garantindo o rigor exigido pelo requisito OR06.
"""

from typing import List, Optional


def ler_texto_obrigatorio(prompt: str) -> str:
    """
    Lê uma entrada de texto garantindo que não é vazia.

    :param prompt: Mensagem a apresentar ao utilizador no terminal.
    :type prompt: str
    :return: Texto inserido, sem espaços nas extremidades.
    :rtype: str
    """
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        print("Valor obrigatório. Tente novamente.")


def ler_opcao(prompt: str, opcoes_validas: List[str]) -> str:
    """
    Lê uma entrada de texto garantindo que pertence às opções válidas.

    :param prompt: Mensagem a apresentar ao utilizador no terminal.
    :type prompt: str
    :param opcoes_validas: Lista com as opções de resposta permitidas.
    :type opcoes_validas: List[str]
    :return: Opção válida selecionada pelo utilizador.
    :rtype: str
    """
    validas = [o.strip() for o in opcoes_validas]
    while True:
        valor = input(prompt).strip()
        if valor in validas:
            return valor
        print(f"Opção inválida. Opções permitidas: {', '.join(validas)}")


def ler_inteiro_intervalo(prompt: str, minimo: int, maximo: Optional[int] = None) -> int:
    """
    Lê um número inteiro e valida se pertence a um intervalo específico.

    :param prompt: Mensagem a apresentar ao utilizador no terminal.
    :type prompt: str
    :param minimo: Valor numérico mínimo permitido.
    :type minimo: int
    :param maximo: Valor numérico máximo permitido (opcional).
    :type maximo: Optional[int]
    :return: Número inteiro validado.
    :rtype: int
    """
    while True:
        valor = input(prompt).strip()
        
        try:
            numero = int(valor)
        except ValueError:
            print("Valor numérico inválido. Deve ser um número inteiro.")
            continue

        if numero < minimo:
            print(f"Valor inválido. Deve ser >= {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"Valor inválido. Deve ser <= {maximo}.")
            continue
            
        return numero


def ler_data_hora_iso_ou_vazio(prompt: str) -> str:
    """
    Lê uma data e hora no formato ISO ou permite submissão vazia.

    O formato exigido é YYYY-MM-DD HH:MM. Se o utilizador apenas 
    pressionar ENTER sem digitar, devolve uma string vazia.

    :param prompt: Mensagem a apresentar ao utilizador.
    :type prompt: str
    :return: String contendo a data/hora válida ou string vazia.
    :rtype: str
    """
    while True:
        valor = input(prompt).strip()
        if not valor:
            return ""
            
        if _validar_data_hora_iso(valor):
            return valor
            
        print("Formato inválido. Use o formato: YYYY-MM-DD HH:MM.")


def ler_ods_ou_vazio(prompt: str) -> Optional[int]:
    """
    Lê um identificador de ODS (1 a 17) ou permite submissão vazia.

    :param prompt: Mensagem a apresentar ao utilizador.
    :type prompt: str
    :return: ODS validado como inteiro ou None se submetido em branco.
    :rtype: Optional[int]
    """
    while True:
        valor = input(prompt).strip()
        if not valor:
            return None
            
        if valor.isdigit():
            ods = int(valor)
            if 1 <= ods <= 17:
                return ods
                
        print("ODS inválido. Use um valor numérico entre 1 e 17.")


def _validar_data_hora_iso(valor: str) -> bool:
    """
    Valida manualmente uma string de data/hora no formato ISO.
    
    Nota: Como as bibliotecas permitidas (OR07) não incluem o módulo 'datetime', 
    esta validação é feita através de segmentação posicional de texto.

    :param valor: Texto inserido pelo utilizador.
    :type valor: str
    :return: True se cumprir o formato exato YYYY-MM-DD HH:MM, False caso contrário.
    :rtype: bool
    """
    if len(valor) != 16:
        return False
        
    # Verificar separadores
    if valor[4] != "-" or valor[7] != "-" or valor[10] != " " or valor[13] != ":":
        return False
        
    ano_str = valor[0:4]
    mes_str = valor[5:7]
    dia_str = valor[8:10]
    hora_str = valor[11:13]
    minuto_str = valor[14:16]
    
    if not (ano_str + mes_str + dia_str + hora_str + minuto_str).isdigit():
        return False
        
    mes_i = int(mes_str)
    dia_i = int(dia_str)
    hora_i = int(hora_str)
    minuto_i = int(minuto_str)
    
    if not (1 <= mes_i <= 12):
        return False
    if not (1 <= dia_i <= 31):
        return False
    if not (0 <= hora_i <= 23):
        return False
    if not (0 <= minuto_i <= 59):
        return False
        
    return True