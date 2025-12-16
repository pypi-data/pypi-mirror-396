import pyodbc


class SqlRepository:
    def __init__(self, connection_string: str):
        self._connection_string = connection_string

    def _exec(self, query: str, values: list = None):
        """
        Executa um comando SQL.

        :param query:
        :param values:
        :return:
        """
        conn = pyodbc.connect(self._connection_string)
        cursor = conn.cursor()

        if values is None:
            cursor.execute(query)
        else:
            cursor.execute(query, values)
        cursor.commit()
        cursor.close()
        conn.close()

    def delete(self, delete_command: str, values: list = None):
        """
        Deleta registros de uma tabela.

        :param delete_command:
        :param values:
        :return:
        """
        self._exec(delete_command, values)

    def insert(self, insert_command: str, values: list = None):
        """
        Insere registros em uma tabela.

        :param insert_command:
        :param values:
        :return:
        """
        self._exec(insert_command, values)

    def update(self, update_command: str, values: list = None):
        """
        Atualiza registros de uma tabela.

        :param update_command:
        :param values:
        :return:
        """
        self._exec(update_command, values)

    def read(self, read_command: str, values: list = None) -> list:
        """ordenar a 
        Lê registros de uma tabela.

        :param read_command:
        :param values:
        :return:
        """
        conn = pyodbc.connect(self._connection_string)
        cursor = conn.cursor()

        if values is None:
            cursor.execute(read_command)
        else:
            cursor.execute(read_command, values)

        # print(read_command)

        rows = cursor.fetchall()

        records = [
            {
                field_description[0]: getattr(rec, field_description[0])
                for field_description in rec.cursor_description
            }
            for rec in rows
        ]


        cursor.close()
        conn.close()

        return records
