import sqlite3


class BasicDB():
    # __database = None
    # __connection = None
    # __cursor = None

    def __init__(self, database: str):
        self.__database = database
        self.__connection = sqlite3.connect(self.__database)

    def getCursor(self):
        if(self.__cursor is None):
            if (self.__database is not None) and (self.__connection is not None):
                self.__connection.row_factory = sqlite3.Row
                self.__cursor = self.__connection.cursor()
        return self.__cursor
