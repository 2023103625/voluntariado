"""
Módulo de modelo para inscrições em ações.

Este módulo define a classe Inscricao, que representa o vínculo e a
candidatura de um voluntário a uma ação de voluntariado específica.
"""

from sistema.constantes import EstadoInscricao


class Inscricao:
    """
    Representa a candidatura de um voluntário a uma ação.

    Gere a informação de relacionamento entre um Voluntário e uma Ação,
    bem como o estado atual dessa candidatura (pendente, aprovada, etc.).

    :param voluntario: Nome ou identificador único do voluntário.
    :type voluntario: str
    :param acao: Título ou identificador único da ação.
    :type acao: str
    :param data_hora_inscricao: Data e hora de registo da inscrição (formato ISO YYYY-MM-DD HH:MM).
    :type data_hora_inscricao: str
    """

    def __init__(
        self,
        voluntario: str,
        acao: str,
        data_hora_inscricao: str
    ) -> None:
        """
        Inicializa uma nova instância de Inscricao.
        """
        self.voluntario: str = voluntario
        self.acao: str = acao
        self.data_hora_inscricao: str = data_hora_inscricao
        self.estado: str = EstadoInscricao.PENDENTE

    def atualizar_estado(self, novo_estado: str) -> bool:
        """
        Atualiza o estado da inscrição mediante validação.

        Verifica se o novo estado pretendido existe nas constantes
        definidas no enumerador EstadoInscricao.

        :param novo_estado: O novo estado pretendido (ex: 'aprovada', 'rejeitada').
        :type novo_estado: str
        :return: True se o estado for válido e atualizado, False caso contrário.
        :rtype: bool
        """
        estados_validos = [e.value for e in EstadoInscricao]
        novo_estado_formatado = novo_estado.lower()
        
        if novo_estado_formatado in estados_validos:
            self.estado = novo_estado_formatado
            return True
        return False

    def __str__(self) -> str:
        """
        Retorna uma representação textual legível da inscrição.

        :return: String com os detalhes do voluntário, ação e estado atual.
        :rtype: str
        """
        return f"Inscrição: {self.voluntario} na ação '{self.acao}' - Estado: {self.estado}"