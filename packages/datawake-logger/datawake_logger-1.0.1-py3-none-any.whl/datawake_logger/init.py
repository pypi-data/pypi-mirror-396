"""
DataWake Logger - Cliente assíncrono para envio de logs

Uma biblioteca Python para envio assíncrono de logs para a API DataWake.

Exemplo básico de uso:
    ```python
    import asyncio
    from datawake_logger import Logger, MessageLogger
    
    async def main():
        async with Logger.from_env(cliente="MeuApp") as logger:
            logger.log(
                MessageLogger.INFO,
                "Operação concluída",
                rotina="processamento",
                output_print=True
            )
    
    asyncio.run(main())
    ```
"""

__version__ = "1.0.0"
__author__ = "DataWake Team"
__all__ = ["Logger", "MessageLogger"]

from .logger import Logger
from .enums import MessageLogger
