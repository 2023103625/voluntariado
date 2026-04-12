"""Funções utilitárias de input para a interface terminal.

Este módulo centraliza validações de entrada do utilizador (OR06).
"""

from typing import List, Optional


def ler_texto_obrigatorio(prompt: str) -> str:
    """Lê texto não vazio.

    :param prompt: Mensagem apresentada ao utilizador.
    :return: Texto válido (sem espaços nas extremidades).
    """
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        print("Valor obrigatório. Tente novamente.")


def ler_opcao(prompt: str, opcoes_validas: List[str]) -> str:
    """Lê uma opção garantindo pertença ao conjunto de opções válidas.

    :param prompt: Mensagem apresentada ao utilizador.
    :param opcoes_validas: Lista de opções permitidas.
    :return: Opção válida selecionada.
    """
    validas = [o.strip() for o in opcoes_validas]
    while True:
        valor = input(prompt).strip()
        if valor in validas:
            return valor
        print(f"Opção inválida. Opções permitidas: {', '.join(validas)}")


def ler_inteiro_intervalo(prompt: str, minimo: int, maximo: Optional[int] = None) -> int:
    """Lê um inteiro dentro de um intervalo.

    :param prompt: Mensagem apresentada ao utilizador.
    :param minimo: Valor mínimo permitido.
    :param maximo: Valor máximo permitido (opcional).
    :return: Inteiro validado.
    """
    while True:
        valor = input(prompt).strip()
        if valor.startswith("-"):
            numero_texto = valor[1:]
        else:
            numero_texto = valor
        if not numero_texto.isdigit():
            print("Valor inválido. Deve ser um número inteiro.")
            continue
        numero = int(valor)
        if numero < minimo:
            print(f"Valor inválido. Deve ser >= {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"Valor inválido. Deve ser <= {maximo}.")
            continue
        return numero


def ler_data_hora_iso_ou_vazio(prompt: str) -> str:
    """Lê data/hora no formato ``YYYY-MM-DD HH:MM`` ou vazio.

    :param prompt: Mensagem apresentada ao utilizador.
    :return: String vazia ou data/hora válida no formato esperado.
    """
    while True:
        valor = input(prompt).strip()
        if not valor:
            return ""
        if _validar_data_hora_iso(valor):
            return valor
        print("Formato inválido. Use YYYY-MM-DD HH:MM.")


def ler_ods_ou_vazio(prompt: str) -> Optional[int]:
    """Lê ODS (1..17) ou vazio.

    :param prompt: Mensagem apresentada ao utilizador.
    :return: Inteiro entre 1 e 17, ou ``None`` se vazio.
    """
    while True:
        valor = input(prompt).strip()
        if not valor:
            return None
        if valor.isdigit():
            ods = int(valor)
            if 1 <= ods <= 17:
                return ods
        print("ODS inválido. Use um valor entre 1 e 17.")


def _validar_data_hora_iso(valor: str) -> bool:
    """Valida data/hora no formato ``YYYY-MM-DD HH:MM``.

    :param valor: Texto inserido pelo utilizador.
    :return: ``True`` se válido, caso contrário ``False``.
    """
    if len(valor) != 16:
        return False
    if valor[4] != "-" or valor[7] != "-" or valor[10] != " " or valor[13] != ":":
        return False
    ano = valor[0:4]
    mes = valor[5:7]
    dia = valor[8:10]
    hora = valor[11:13]
    minuto = valor[14:16]
    if not (ano + mes + dia + hora + minuto).isdigit():
        return False
    mes_i = int(mes)
    dia_i = int(dia)
    hora_i = int(hora)
    minuto_i = int(minuto)
    if not (1 <= mes_i <= 12):
        return False
    if not (1 <= dia_i <= 31):
        return False
    if not (0 <= hora_i <= 23):
        return False
    if not (0 <= minuto_i <= 59):
        return False
    return True