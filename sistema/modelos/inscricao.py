from typing import Optional

class Inscricao:
    """
    Representa a candidatura de um voluntário a uma ação de voluntariado.
    
    :ivar voluntario: Identificação do voluntário.
    :ivar acao: Identificação da ação com data e hora.
    :ivar data_hora_inscricao: Momento em que a inscrição foi realizada.
    :ivar estado: Estado da inscrição (pendente / aprovada / rejeitada / lista de espera).
    """

    def __init__(self, voluntario: str, acao: str, data_hora_inscricao: str):
        """
        Inicializa uma nova inscrição com o estado padrão 'pendente'.

        :param voluntario: Nome ou objeto do voluntário.
        :param acao: Título ou objeto da ação.
        :param data_hora_inscricao: Data e hora do registo.
        """
        self.voluntario: str = voluntario
        self.acao: str = acao
        self.data_hora_inscricao: str = data_hora_inscricao
        
        # O estado inicial é sempre pendente até ser processado [cite: 48, 54]
        self.estado: str = "pendente"

    def atualizar_estado(self, novo_estado: str) -> bool:
        """
        Atualiza o estado da inscrição validando as opções permitidas.
        
        :param novo_estado: O novo estado a atribuir.
        :return: True se o estado for válido e alterado, False caso contrário.
        """
        estados_validos = ["pendente", "aprovada", "rejeitada", "lista de espera"] #[cite: 48]
        if novo_estado.lower() in estados_validos:
            self.estado = novo_estado.lower()
            return True
        return False

    def __str__(self) -> str:
        """Retorna uma representação legível da inscrição."""
        return f"Inscrição: {self.voluntario} na ação '{self.acao}' - Estado: {self.estado}"