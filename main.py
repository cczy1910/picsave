from src import run_server

from common.exit_util import safe_exit
from common.logging.base import get_logger

LOGGER = get_logger()


def main():
    try:
        run_server()
    except Exception as e:
        LOGGER.error(str(e))
        safe_exit(f'Server is temporarily unavailable: {str(e)}')


if __name__ == '__main__':
    main()
