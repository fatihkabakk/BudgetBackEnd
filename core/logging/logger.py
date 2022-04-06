from time import perf_counter
from functools import wraps
from os.path import dirname
import logging
import os


def _default_name(file_path: str) -> str:
    """ Creates a default name from the given file's path. """
    return file_path.split(os.sep)[-1].rstrip('.py')


class Logger:
    """ Modified Logger class """

    def __init__(self, logger_name: str = __file__, file_name: str = 'Log.log', level=logging.DEBUG) -> None:
        logger_name = _default_name(logger_name)
        file_path = f'{str(os.sep).join([dirname(dirname(dirname(__file__))), "logs", file_name])}'
        print(file_path)
        self.setup_logger(file_path=file_path,
                          logger_name=logger_name, level=level)

    def setup_logger(self, file_path, logger_name, level):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%y %H:%M:%S')
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @staticmethod
    def parse_func_name(func):
        info = func.__qualname__.split(".")

        if len(info) == 2:
            method_info = f"Method '{info[-1]}' of '{'.'.join(info[0:-1])}'"
        else:
            method_info = f"'{info[0]}'"
        return method_info

    def critical(self, func: str):
        method_info = self.parse_func_name(func)

        self.logger.critical(
            f"{method_info} has raised an error.", exc_info=True)

    def _log(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                method_info = self.parse_func_name(func)

                self.logger.info(f"{method_info} is being called.")

                t1 = perf_counter()

                return func(*args, **kwargs)
            except Exception:
                self.logger.critical(
                    f"{method_info} has raised an error.", exc_info=True)
            finally:
                self.logger.debug(
                    f"{method_info} has ended, it lasted for {round((perf_counter()-t1) * 1000, 4)} ms.\n")
        return wrapper

    @property
    def log(self) -> "Logger._log":
        return self._log


def name_test():
    random_names = ['jack', 'captain', 'hello', 'python',
                    'test_logger31', 'names', 'crypto', 'fuckya', 'xo', 'aye']
    for i in random_names:
        assert Logger(i).logger.name == i

    print('Name test is successful!')


if __name__ == '__main__':
    log = Logger(file_name='Client.log').log
    exit(name_test())

    @log
    def test_main():
        print('Test31')

    print('Main called.')
    test_main()
