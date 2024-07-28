import os
import sys

from loguru import logger


def configure_logger(log_dir="logs"):
    """
    Configura o logger com rotação de log de 7 dias, diretório específico e exibição no console com cores.

    Args:
        log_dir (str): Diretório onde os arquivos de log serão salvos.
    """
    # Cria o diretório de logs se não existir
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Remove qualquer configuração anterior do logger
    logger.remove()

    # Configura a rotação de logs para 7 dias e o formato dos arquivos de log
    logger.add(
        os.path.join(log_dir, "app.log"),
        rotation="7 days",  # Rotaciona o log a cada 7 dias
        retention="30 days",  # Mantém os logs por 30 dias
        level="INFO",  # Nível de log
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",  # Formato do log
        backtrace=True,  # Inclui traceback em logs de erro
        diagnose=True,  # Diagnóstico adicional para erros
    )

    # Configura a exibição dos logs no console com cores
    logger.add(
        sys.stdout,
        level="INFO",  # Nível de log
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",  # Formato do log com cores
        filter=lambda record: record["level"].name
        in ("INFO", "ERROR"),  # Filtra os logs para mostrar INFO e ERROR
    )


if __name__ == "__main__":
    configure_logger()
    logger.info("Logger configurado com sucesso!")
    logger.error("Mensagem de erro para testar a cor vermelha.")