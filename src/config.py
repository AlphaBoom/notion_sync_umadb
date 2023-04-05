import configparser

_DATA_BASE_ID = "database_id"

class Properties:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        if _DATA_BASE_ID not in self.config:
            self.config[_DATA_BASE_ID] = {}

    def write_database_id(self, key, databaseid) -> None:
        self.config[_DATA_BASE_ID][key] = databaseid
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def read_database_id(self, key) -> str:
        return self.config[_DATA_BASE_ID].get(key)


