import sys
from loguru import logger

def setup_logging():
    # Удаляем стандартный обработчик
    logger.remove()

    # Добавляем вывод в консоль (цветной, форматированный)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )

    # Добавляем запись в файл с ротацией (каждый день или по размеру)
    logger.add(
        "logs/app.log",
        rotation="1 day",      # каждый день новый файл
        retention="30 days",   # хранить 30 дней
        compression="zip",     # сжимать старые логи
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO"           # в файл пишем INFO и выше (чтобы не засорять)
    )