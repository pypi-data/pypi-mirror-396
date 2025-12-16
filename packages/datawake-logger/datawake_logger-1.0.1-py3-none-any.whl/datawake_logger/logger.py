"""
Cliente assíncrono para envio de logs para a API DataWake
"""
import asyncio
import os
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

import aiohttp
from aiohttp import BasicAuth

from .enums import MessageLogger


# Constantes
DEFAULT_TIMEOUT_SECS = 10
DEFAULT_USER_AGENT = "Async_NonBlocking_Client/1.0"


class Logger:
    """
    Classe para enviar logs assíncronos para um endpoint via requisição POST.

    Esta classe encapsula a lógica de envio de logs de forma "fire and forget",
    garantindo que o programa principal não seja bloqueado.
    
    Exemplo de uso:
        ```python
        import asyncio
        from datawake_logger import Logger, MessageLogger
        
        async def main():
            async with Logger(
                uri="https://api-logs.example.com/logs",
                sistema="meu_sistema",
                username="usuario",
                api_user="api_user",
                api_password="api_pass",
                cliente="MeuCliente"
            ) as logger:
                logger.log(
                    MessageLogger.INFO,
                    "Processamento iniciado",
                    rotina="processamento",
                    output_print=True
                )
        
        asyncio.run(main())
        ```
    """
    
    def __init__(
        self,
        uri: str,
        sistema: str,
        username: str,
        api_user: str,
        api_password: str,
        timeout: int = DEFAULT_TIMEOUT_SECS,
        cliente: Optional[str] = None,
        ssl_verify: bool = True
    ):
        """
        Inicializa o logger com a URI e configurações padrão.

        Args:
            uri (str): A URI para a qual os logs serão enviados.
            sistema (str): Nome do sistema de origem do log.
            username (str): Nome do usuário/sistema que está gerando o log.
            api_user (str): Usuário para autenticação na API.
            api_password (str): Senha para autenticação na API.
            timeout (int): Tempo limite para a requisição em segundos.
            cliente (str, optional): Nome do cliente/aplicação.
            ssl_verify (bool): Se deve verificar certificados SSL (padrão: True).
        """
        if not uri:
            raise ValueError("O parâmetro 'uri' é obrigatório")
        if not sistema:
            raise ValueError("O parâmetro 'sistema' é obrigatório")
        if not username:
            raise ValueError("O parâmetro 'username' é obrigatório")
        if not api_user:
            raise ValueError("O parâmetro 'api_user' é obrigatório")
        if not api_password:
            raise ValueError("O parâmetro 'api_password' é obrigatório")
        
        self._uri = uri
        self._timeout = timeout
        self._sistema = sistema
        self._username = username
        self._cliente = cliente
        self.hash_id = "%032x" % random.getrandbits(128)
        
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self._timeout),
            headers={
                "User-Agent": username,
                "Content-Type": "application/json"
            },
            auth=BasicAuth(login=api_user, password=api_password),
            connector=aiohttp.TCPConnector(ssl=ssl_verify)
        )
        
        # Lista para manter o controle das tarefas de log pendentes
        self._pending_tasks: List[asyncio.Task] = []

    @classmethod
    def from_env(
        cls,
        env_prefix: str = "",
        timeout: int = DEFAULT_TIMEOUT_SECS,
        cliente: Optional[str] = None,
        ssl_verify: bool = True
    ):
        """
        Cria uma instância do Logger a partir de variáveis de ambiente.
        
        Args:
            env_prefix (str): Prefixo para as variáveis de ambiente.
            timeout (int): Tempo limite para requisições.
            cliente (str, optional): Nome do cliente/aplicação.
            ssl_verify (bool): Se deve verificar certificados SSL.
            
        Variáveis de ambiente esperadas:
            - {prefix}LOG_API_URI
            - {prefix}SISTEMA_ORIGEM_LOG
            - {prefix}USUARIO_LOG
            - {prefix}LOG_API_USER
            - {prefix}LOG_API_PASSWORD
            
        Returns:
            Logger: Instância configurada do logger.
            
        Raises:
            ValueError: Se alguma variável de ambiente obrigatória não estiver definida.
        """
        uri = os.getenv(f"{env_prefix}LOG_API_URI")
        sistema = os.getenv(f"{env_prefix}SISTEMA_ORIGEM_LOG")
        username = os.getenv(f"{env_prefix}USUARIO_LOG")
        api_user = os.getenv(f"{env_prefix}LOG_API_USER")
        api_password = os.getenv(f"{env_prefix}LOG_API_PASSWORD")
        
        if not uri:
            raise ValueError(f"A variável de ambiente '{env_prefix}LOG_API_URI' não está definida")
        if not sistema:
            raise ValueError(f"A variável de ambiente '{env_prefix}SISTEMA_ORIGEM_LOG' não está definida")
        if not username:
            raise ValueError(f"A variável de ambiente '{env_prefix}USUARIO_LOG' não está definida")
        if not api_user:
            raise ValueError(f"A variável de ambiente '{env_prefix}LOG_API_USER' não está definida")
        if not api_password:
            raise ValueError(f"A variável de ambiente '{env_prefix}LOG_API_PASSWORD' não está definida")
        
        return cls(
            uri=uri,
            sistema=sistema,
            username=username,
            api_user=api_user,
            api_password=api_password,
            timeout=timeout,
            cliente=cliente,
            ssl_verify=ssl_verify
        )

    async def __aenter__(self):
        """
        Método de entrada do gerenciador de contexto assíncrono.
        Retorna a própria instância da classe.
        """
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Método de saída do gerenciador de contexto.
        Garante que a sessão e as tarefas pendentes sejam fechadas de forma segura.
        """
        await self.close()
        
    async def close(self):
        """
        Fecha a sessão do cliente e espera a finalização das tarefas pendentes.
        """
        await asyncio.sleep(0.1)
        
        # Espera que todas as tarefas assíncronas de log terminem
        if self._pending_tasks:
            await asyncio.gather(*self._pending_tasks, return_exceptions=True)
            
        await self._session.close()

    async def _log_async(self, dados: Dict[str, Any]) -> None:
        """
        Realiza uma requisição HTTP POST assíncrona para enviar os dados de log.

        Esta função não bloqueia e delega a requisição para o loop de eventos,
        retornando imediatamente.

        Args:
            dados (Dict[str, Any]): Um dicionário com os dados a serem logados.
        """
        try:
            tarefa = asyncio.create_task(
                self._session.post(self._uri, json=dados)
            )
            self._pending_tasks.append(tarefa)

        except aiohttp.ClientError as e:
            print(f"Erro ao tentar fazer a requisição: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

    def log(
        self,
        level: MessageLogger,
        mensagem: str,
        rotina: Optional[str] = None,
        tabela: Optional[str] = None,
        topico: Optional[str] = None,
        op: Optional[str] = None,
        unidade_producao: Optional[str] = None,
        output_print: bool = False
    ):
        """
        Registra uma mensagem de log de forma assíncrona.
        
        Args:
            level (MessageLogger): Nível do log (INFO, DEBUG, WARN, ERROR, AVISO).
            mensagem (str): Mensagem a ser logada.
            rotina (str, optional): Nome da rotina em execução.
            tabela (str, optional): Nome da tabela relacionada ao log.
            topico (str, optional): Nome do tópico Kafka relacionado.
            op (str, optional): Ordem de produção relacionada.
            unidade_producao (str, optional): Unidade de produção relacionada.
            output_print (bool): Se deve imprimir a mensagem no console.
            
        Raises:
            TypeError: Se level não for uma instância de MessageLogger.
            ValueError: Se mensagem não for fornecida.
        """
        if not isinstance(level, MessageLogger):
            raise TypeError("level precisa ser uma instância de MessageLogger")
        if not mensagem:
            raise ValueError("mensagem é um parâmetro obrigatório")

        dados = {
            "tipo": level.value.lower(),
            "sistema": self._sistema,
            "username": self._username,
            "cliente": self._cliente,
            "rotina": rotina,
            "mensagem": f"{self.hash_id}|{mensagem}",
            "tabela": tabela,
            "topico": topico,
            "op": op,
            "unidade_producao": unidade_producao
        }
        
        try:
            asyncio.create_task(self._log_async(dados))
            if output_print:
                timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f')
                print(f"[{timestamp}] [{level.value.lower():<5}] - {mensagem}")
        except Exception as e:
            print(f"Erro ao enfileirar o log: {e}")
