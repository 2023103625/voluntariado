"""Modelo de domínio para inscrições em ações."""


class Inscricao:
    """Representa a candidatura de um voluntário a uma ação.

    :param voluntario: Nome/identificador do voluntário.
    :param acao: Título/identificador da ação.
    :param data_hora_inscricao: Data/hora de registo da inscrição.
    """

    def __init__(self, voluntario: str, acao: str, data_hora_inscricao: str):
        self.voluntario: str = voluntario
        self.acao: str = acao
        self.data_hora_inscricao: str = data_hora_inscricao
        self.estado: str = "pendente"

    def atualizar_estado(self, novo_estado: str) -> bool:
        """Atualiza o estado da inscrição.

        Estados válidos: ``pendente``, ``aprovada``, ``rejeitada``,
        ``lista de espera``.

        :param novo_estado: Novo estado pretendido.
        :return: ``True`` se o estado for válido; caso contrário ``False``.
        """
        estados_validos = ["pendente", "aprovada", "rejeitada", "lista de espera"]
        if novo_estado.lower() in estados_validos:
            self.estado = novo_estado.lower()
            return True
        return False

    def __str__(self) -> str:
        """Retorna representação legível da inscrição."""
        return f"Inscrição: {self.voluntario} na ação '{self.acao}' - Estado: {self.estado}"