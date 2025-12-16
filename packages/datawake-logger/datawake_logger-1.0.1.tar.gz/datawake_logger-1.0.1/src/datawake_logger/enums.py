"""
Enumerações para o DataWake Logger
"""
from enum import Enum


class MessageLogger(Enum):
    """
    Enum para os níveis de log disponíveis.
    """
    INFO = "info"
    DEBUG = "debug"
    WARN = "warn"
    ERROR = "error"
    AVISO = "aviso"
