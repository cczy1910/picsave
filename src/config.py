from environs import Env

env = Env()

SERVER = {
    'IU_SERVER_PORT': env.int('PORT', 8080),
    'IU_SERVER_HOST': env('HOST', 'localhost')
}

DATABASE_SETTINGS = {
    'user': env('MYSQL_USER', 'root'),
    'password': env('MYSQL_PASSWORD', 'password'),
    'host': env('MYSQL_HOST', '0.0.0.0'),
    'port': env.int('MYSQL_PORT', 3306),
    'db': env('MYSQL_DATABASE', 'mysql'),
}

REDIS_SETTINGS = {
    'host': env('REDIS_LOCAL_HOST', '0.0.0.0'),
    'port': env('REDIS_LOCAL_PORT', 6379),
    'password': env('REDIS_LOCAL_PASSWORD', ''),
    'db': env.int('REDIS_LOCAL_DB', 0),
    'socket_timeout': env.int('REDIS_LOCAL_SOCKET_TIMEOUT', 5)
}
