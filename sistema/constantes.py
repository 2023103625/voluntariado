"""Módulo central com as constantes e enumerações do sistema.

A utilização destas constantes elimina as "Magic Strings" espalhadas pelo código,
facilitando a manutenção e prevenindo erros de digitação (typos).
"""

from enum import Enum


class VinculoVoluntario(str, Enum):
    """Tipos de vínculo institucional permitidos para os voluntários."""
    ESTUDANTE = "estudante"
    DOCENTE = "docente"
    TECNICO = "tecnico"


class TipoEntidade(str, Enum):
    """Tipos de entidades promotoras parceiras."""
    NUCLEO = "núcleo"
    ASSOCIACAO = "associação"
    SERVICO = "serviço"
    ONG = "ong parceira"


class EstadoAcao(str, Enum):
    """Estados do ciclo de vida de uma ação de voluntariado."""
    PLANEADA = "planeada"
    CONCLUIDA = "concluída"
    CANCELADA = "cancelada"


class LocalizacaoAcao(str, Enum):
    """Tipos de localização onde as ações podem decorrer."""
    CAMPUS = "campus"
    EXTERNO = "externo"
    ONLINE = "online"


class EstadoInscricao(str, Enum):
    """Estados possíveis do processamento de uma inscrição."""
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    ESPERA = "lista de espera"