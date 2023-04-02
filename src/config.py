import configparser

_DATA_BASE_ID = "database_id"
_config_file = "local.properties"

config = configparser.ConfigParser()
config.read(_config_file)
if _DATA_BASE_ID not in config:
    config[_DATA_BASE_ID] = {}

def write_database_id(key, databaseid) -> None:
    config[_DATA_BASE_ID][key] = databaseid
    with open(_config_file, 'w') as configfile:
        config.write(configfile)

def read_database_id(key) -> str:
    return config[_DATA_BASE_ID].get(key)