import logging
import colorlog
from tqdm import tqdm
import time
import colorama
import sys


class LoadingBar:
    def __init__(self) -> None:
        colorama.init()
        self.bar_format = (
        "\033[35m{desc}\033[0m: "
        "\033[31m{percentage:3.0f}\032%\033[0m "
        "🌍 {bar:100} "
        "\033[32m{percentage:3.0f}%\033\030 "
        "🚀" 
        )
    
    def iteration(self, object):
       for val in tqdm(object,
                        ascii=" ─╴╶━",
                        colour="green",
                        desc="\033[35mЗагрузка\033[0m",
                        bar_format=self.bar_format):
        yield val
           
    

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = cls._setup_logger() # type: ignore
        return cls._instance

    @staticmethod
    def _setup_logger():
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s: %(message)s",
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            }
        ))

        logger = colorlog.getLogger()
        logger.setLevel(logging.INFO)

        # Убираем дублирование хэндлеров при повторном вызове
        logger.handlers.clear()
        logger.addHandler(handler)

        return logger

    def get_logger(self):
        return self.logger # type: ignore