"""
Testes unitários para o DataWake Logger
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datawake_logger import Logger, MessageLogger


class TestMessageLogger:
    """Testes para o enum MessageLogger"""
    
    def test_message_logger_values(self):
        """Testa se os valores do enum estão corretos"""
        assert MessageLogger.INFO.value == "info"
        assert MessageLogger.DEBUG.value == "debug"
        assert MessageLogger.WARN.value == "warn"
        assert MessageLogger.ERROR.value == "error"
        assert MessageLogger.AVISO.value == "aviso"


class TestLogger:
    """Testes para a classe Logger"""
    
    @pytest.fixture
    def logger_config(self):
        """Configuração padrão para testes"""
        return {
            "uri": "https://test.example.com/logs",
            "sistema": "test_system",
            "username": "test_user",
            "api_user": "api_test",
            "api_password": "api_pass",
            "timeout": 5,
            "cliente": "TestClient",
            "ssl_verify": False
        }
    
    def test_logger_initialization(self, logger_config):
        """Testa a inicialização básica do Logger"""
        logger = Logger(**logger_config)
        assert logger._uri == logger_config["uri"]
        assert logger._sistema == logger_config["sistema"]
        assert logger._username == logger_config["username"]
        assert logger._cliente == logger_config["cliente"]
        assert logger._timeout == logger_config["timeout"]
    
    def test_logger_missing_required_params(self):
        """Testa se ValueError é lançado quando faltam parâmetros obrigatórios"""
        with pytest.raises(ValueError):
            Logger(
                uri="",
                sistema="test",
                username="user",
                api_user="api",
                api_password="pass"
            )
    
    def test_logger_hash_id_generation(self, logger_config):
        """Testa se o hash_id é gerado corretamente"""
        logger1 = Logger(**logger_config)
        logger2 = Logger(**logger_config)
        
        assert len(logger1.hash_id) == 32
        assert logger1.hash_id != logger2.hash_id
    
    @pytest.mark.asyncio
    async def test_logger_context_manager(self, logger_config):
        """Testa o gerenciador de contexto assíncrono"""
        async with Logger(**logger_config) as logger:
            assert logger is not None
            assert not logger._session.closed
        
        # Após sair do contexto, a sessão deve estar fechada
        assert logger._session.closed
    
    @pytest.mark.asyncio
    async def test_log_method_info(self, logger_config):
        """Testa o método log com nível INFO"""
        async with Logger(**logger_config) as logger:
            # Mock do método _log_async
            logger._log_async = AsyncMock()
            
            logger.log(
                MessageLogger.INFO,
                "Test message",
                rotina="test_routine",
                output_print=False
            )
            
            # Aguarda um pouco para garantir que a task foi criada
            await asyncio.sleep(0.1)
    
    def test_log_method_invalid_level(self, logger_config):
        """Testa se TypeError é lançado quando level não é MessageLogger"""
        logger = Logger(**logger_config)
        
        with pytest.raises(TypeError):
            logger.log("invalid_level", "Test message")
    
    def test_log_method_missing_message(self, logger_config):
        """Testa se ValueError é lançado quando mensagem está vazia"""
        logger = Logger(**logger_config)
        
        with pytest.raises(ValueError):
            logger.log(MessageLogger.INFO, "")
    
    @pytest.mark.asyncio
    async def test_log_with_all_parameters(self, logger_config):
        """Testa log com todos os parâmetros opcionais"""
        async with Logger(**logger_config) as logger:
            logger._log_async = AsyncMock()
            
            logger.log(
                MessageLogger.ERROR,
                "Error message",
                rotina="data_processing",
                tabela="users",
                topico="kafka_topic",
                op="OP123",
                unidade_producao="Limeira",
                output_print=False
            )
            
            await asyncio.sleep(0.1)
    
    @patch.dict('os.environ', {
        'LOG_API_URI': 'https://api.test.com/logs',
        'SISTEMA_ORIGEM_LOG': 'test_system',
        'USUARIO_LOG': 'test_user',
        'LOG_API_USER': 'api_user',
        'LOG_API_PASSWORD': 'api_pass'
    })
    def test_from_env_method(self):
        """Testa criação do Logger a partir de variáveis de ambiente"""
        logger = Logger.from_env(cliente="EnvTestClient")
        
        assert logger._uri == "https://api.test.com/logs"
        assert logger._sistema == "test_system"
        assert logger._username == "test_user"
        assert logger._cliente == "EnvTestClient"
    
    def test_from_env_missing_variables(self):
        """Testa se ValueError é lançado quando variáveis de ambiente estão faltando"""
        with pytest.raises(ValueError):
            Logger.from_env()
    
    @pytest.mark.asyncio
    async def test_multiple_logs(self, logger_config):
        """Testa múltiplos logs em sequência"""
        async with Logger(**logger_config) as logger:
            logger._log_async = AsyncMock()
            
            for i in range(5):
                logger.log(
                    MessageLogger.INFO,
                    f"Message {i}",
                    rotina="batch_test",
                    output_print=False
                )
            
            await asyncio.sleep(0.2)
    
    @pytest.mark.asyncio
    async def test_logger_close_waits_for_pending_tasks(self, logger_config):
        """Testa se close aguarda tarefas pendentes"""
        async with Logger(**logger_config) as logger:
            logger._log_async = AsyncMock()
            
            # Cria múltiplos logs
            for i in range(3):
                logger.log(MessageLogger.INFO, f"Message {i}")
            
            # Ao sair do contexto, deve aguardar todas as tarefas
        
        # Todas as tarefas devem ter sido aguardadas
        assert len(logger._pending_tasks) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
