import configparser


def config_reader():
    # reading the config files
    config = configparser.ConfigParser()

    # for Aditya
    config.read("D:/Projects/config/config2.ini")

    # for Manel
    # config.read("./config.ini")

    CONFIG = dict()

    CONFIG['DB-CONFIG'] = config['db-config']

    CONFIG['AUTOCOMMIT'] = config['db-settings']['enable_autocommit']

    return CONFIG