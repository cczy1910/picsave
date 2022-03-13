import logging

logging.basicConfig(filename='logs/application.log', encoding='utf-8', level=logging.DEBUG)


def get_logger():
    return logging.getLogger('application.logger')
