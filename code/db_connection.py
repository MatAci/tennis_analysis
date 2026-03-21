import psycopg2
from configparser import ConfigParser

class DatabaseConnection:
    def __init__(self, config_file='config.ini', section='postgresql'):
        self.params = self._read_config(config_file, section)
        self.schema = self.params.pop('schema', None)  # Ukloni 'schema' iz parametara

    def _read_config(self, filename, section):
        parser = ConfigParser()
        parser.read(filename)
        if section in parser:
            return {key: value for key, value in parser.items(section)}
        else:
            raise Exception(f"Section {section} not found in {filename}")

    def connect(self):
        if not hasattr(self, 'connection') or self.connection is None:
            self.connection = psycopg2.connect(**self.params)
            if self.schema:
                with self.connection.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {self.schema};")  # Postavi shemu
        return self.connection

    def close(self):
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            self.connection = None