import configparser

_DATA_BASE_ID = "database_id"
_FILE_CHANGED_TIME = "file_changed_time"

class Properties:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        if _DATA_BASE_ID not in self.config:
            self.config[_DATA_BASE_ID] = {}
        if _FILE_CHANGED_TIME not in self.config:
            self.config[_FILE_CHANGED_TIME] = {}

    def write_database_id(self, key, databaseid) -> None:
        self.config[_DATA_BASE_ID][key] = databaseid
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def read_database_id(self, key) -> str:
        return self.config[_DATA_BASE_ID].get(key)
    
    def write_file_changed_time(self, key, timestamp):
        self.config[_FILE_CHANGED_TIME][key] = str(timestamp)
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def read_file_changed_time(self, key):
        ret = self.config[_FILE_CHANGED_TIME].get(key)
        if ret:
            return int(ret)
        else:
            return 0


