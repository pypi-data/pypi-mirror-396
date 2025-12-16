# DataWake Logger

Cliente assíncrono em Python para envio de logs para a API DataWake.

## 🚀 Características

- ✅ **Assíncrono**: Não bloqueia a execução do seu código
- ✅ **Fire and Forget**: Os logs são enviados em background
- ✅ **Context Manager**: Gerenciamento automático de recursos
- ✅ **Type Hints**: Código totalmente tipado
- ✅ **Configuração via .env**: Suporte a variáveis de ambiente
- ✅ **SSL Configurável**: Funciona em ambientes de desenvolvimento e produção

## 📦 Instalação

```bash
pip install datawake-logger
```

Ou para instalação em modo de desenvolvimento:

```bash
pip install datawake-logger[dev]
```

## 🔧 Configuração

### Usando Variáveis de Ambiente

Crie um arquivo `.env` na raiz do seu projeto:

```env
LOG_API_URI=sua_uri
LOG_API_USER=seu_usuario
LOG_API_PASSWORD=sua_senha
SISTEMA_ORIGEM_LOG=nome_do_seu_sistema
USUARIO_LOG=identificador_usuario
```

### Usando Configuração Direta

Você também pode configurar diretamente no código:

```python
from datawake_logger import Logger, MessageLogger

logger = Logger(
    uri="https://sua_url",
    sistema="meu_sistema",
    username="usuario_app",
    api_user="api_user",
    api_password="api_password",
    cliente="meu_cliente"
)
```

## 📖 Uso Básico

### Exemplo 1: Usando variáveis de ambiente

```python
import asyncio
from datawake_logger import Logger, MessageLogger

async def main():
    # Carrega configurações do .env automaticamente
    async with Logger.from_env(cliente="MeuApp") as logger:
        logger.log(
            MessageLogger.INFO,
            "Aplicação iniciada",
            rotina="inicializacao",
            output_print=True
        )
        
        logger.log(
            MessageLogger.DEBUG,
            "Processando dados",
            rotina="processamento",
            tabela="usuarios",
            output_print=True
        )
        
        logger.log(
            MessageLogger.ERROR,
            "Erro ao conectar ao banco",
            rotina="conexao_db",
            output_print=True
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Exemplo 2: Configuração manual

```python
import asyncio
from datawake_logger import Logger, MessageLogger

async def main():
    async with Logger(
        uri="sua_uri",
        sistema="meu_sistema",
        username="usuario_app",
        api_user="api_user",
        api_password="api_password",
        cliente="meu_cliente",
        ssl_verify=False  # Apenas para desenvolvimento
    ) as logger:
        
        logger.log(
            MessageLogger.WARN,
            "Processamento demorado detectado",
            rotina="etl_process",
            tabela="sales_data",
            output_print=True
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Exemplo 3: Integração com PySpark

```python
from pyspark.sql import SparkSession
from datawake_logger import Logger, MessageLogger
import asyncio

async def process_spark_job():
    spark = SparkSession.builder.appName("ETL").getOrCreate()
    
    async with Logger.from_env(cliente="SparkETL") as logger:
        logger.log(
            MessageLogger.INFO,
            "Iniciando job Spark",
            rotina="spark_etl",
            output_print=True
        )
        
        try:
            # Seu código Spark aqui
            df = spark.read.parquet("s3://bucket/data")
            
            logger.log(
                MessageLogger.INFO,
                f"Lidos {df.count()} registros",
                rotina="spark_etl",
                tabela="raw_data",
                output_print=True
            )
            
        except Exception as e:
            logger.log(
                MessageLogger.ERROR,
                f"Erro no job: {str(e)}",
                rotina="spark_etl",
                output_print=True
            )
            raise

if __name__ == "__main__":
    asyncio.run(process_spark_job())
```

## 📊 Níveis de Log

A biblioteca suporta 5 níveis de log:

- `MessageLogger.INFO` - Informações gerais
- `MessageLogger.DEBUG` - Informações de debug
- `MessageLogger.WARN` - Avisos
- `MessageLogger.ERROR` - Erros
- `MessageLogger.AVISO` - Avisos especiais

## 🔍 Parâmetros do Método `log()`

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `level` | `MessageLogger` | ✅ Sim | Nível do log |
| `mensagem` | `str` | ✅ Sim | Mensagem a ser logada |
| `rotina` | `str` | ❌ Não | Nome da rotina em execução |
| `tabela` | `str` | ❌ Não | Nome da tabela do banco de dados |
| `topico` | `str` | ❌ Não | Nome do tópico Kafka |
| `op` | `str` | ❌ Não | Ordem de produção |
| `unidade_producao` | `str` | ❌ Não | Unidade de produção |
| `output_print` | `bool` | ❌ Não | Imprimir no console (padrão: False) |

## 🎯 Recursos Avançados

### Hash ID Único

Cada instância do Logger gera um hash ID único de 128 bits que é automaticamente anexado a todas as mensagens, permitindo rastrear logs da mesma sessão.

### Gerenciamento de Tarefas

O Logger mantém controle de todas as tarefas assíncronas pendentes e garante que todas sejam finalizadas antes de fechar a sessão.

### SSL Configurável

Para ambientes de desenvolvimento, você pode desabilitar a verificação SSL:

```python
async with Logger.from_env(
    cliente="DevApp",
    ssl_verify=False  # Desabilita verificação SSL
) as logger:
    # seu código aqui
    pass
```

## 🧪 Testes

Execute os testes com:

```bash
pytest tests/
```

Com cobertura:

```bash
pytest --cov=datawake_logger tests/
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- DataWake Team - [contato@datawake.cloud](mailto:contato@datawake.cloud)

## 🐛 Reportar Problemas

Encontrou um bug? [Abra uma issue](https://github.com/datawake/datawake-logger/issues)

## 📚 Documentação Adicional

Para mais informações sobre a API DataWake, consulte a documentação oficial em [https://docs.datawake.cloud](https://docs.datawake.cloud)
