import yaml
import enum


class QueryType(enum.Enum):
    insertOne = 'insertOne'
    readOne = 'readOne'
    readMany = 'readMany'
    updateOne = 'updateOne'


class DatabaseConfig:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.config_path, 'r') as stream:
                data = yaml.safe_load(stream)
            return data
        except FileNotFoundError:
            print('File {} is not found'.format(self.config_path))
        except yaml.YAMLError:
            print('Error while parsing YAML file')

    def get_query(self, relation: str, query_type: QueryType):
        if relation not in self.data['scripts'].keys():
            raise KeyError
        filepath = self.data['scripts'][relation][query_type.value]
        with open(filepath, 'r') as file:
            return file.read()
