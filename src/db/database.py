import sqlite3
import logging


class Database():

    def __init__(self, database: str):
        self.__database = database
        self.__connection = sqlite3.connect(self.__database)
        self.__logger = logging.getLogger("Database")

    def __getCursor(self):
        if(self.__cursor is None):
            if (self.__database is not None) and (self.__connection is not None):
                self.__connection.row_factory = sqlite3.Row
                self.__cursor = self.__connection.cursor()
        return self.__cursor

    def select(self, table: str, condition: dict):
        ret = None
        sql = "SELECT * FROM " + table
        bindee = []
        if(condition):
            sql += " WHERE "
            cnd = []
            for col in condition.keys():
                cnd.append("`" + col + "` = ?")
                bindee.append(condition[col])
            sql += " AND ".join(cnd)

        try:
            self.__cursor.execute(sql, tuple(bindee))
            ret = self.__cursor.fetchall()
        except sqlite3.Error as e:
            self.__logger.error("Exception on %s, error message is %s", sql, e)
            ret = None
        return ret

    def insert(self, table: str, candidate: dict):
        ret = None
        sql = "INSERT INTO " + table + "("
        cols = []
        vals = []
        for col in candidate.keys():
            cols.append(col)
            vals.append(candidate[col])
        sql += ",".join(cols) + "VALUES("
        sql += ",".join("?" * len(vals)) + ")"

        try:
            self.__cursor.execute(sql, tuple(vals))
            ret = self.__cursor.fetchall()
        except sqlite3.Error as e:
            self.__logger.error("Exception on %s, error message is %s", sql, e)
            ret = None
        return ret

    def update(self, table: str, condition: dict, candidate: dict):
        ret = None
        sql = "UPDATE " + table + " SET "
        cols = []
        vals = []
        for col in candidate.keys():
            cols.append(col + "=?")
            vals.append(candidate[col])
        sql += ",".join(cols)

        if(condition):
            sql += " WHERE "
            cnd = []
            for col in condition.keys():
                cnd.append("`" + col + "` = ?")
                vals.append(condition[col])
            sql += " AND ".join(cnd)
        try:
            self.__cursor.execute(sql, tuple(vals))
            ret = self.__cursor.fetchall()
        except sqlite3.Error as e:
            self.__logger.error("Exception on %s, error message is %s", sql, e)
            ret = None
        return ret

    def delete(self, table: str, condition: dict):
        ret = None
        sql = "DELETE FROM " + table
        bindee = []
        if(condition):
            sql += " WHERE "
            cnd = []
            for col in condition.keys():
                cnd.append("`" + col + "` = ?")
                bindee.append(condition[col])
            sql += " AND ".join(cnd)

        try:
            self.__cursor.execute(sql, tuple(bindee))
            ret = self.__cursor.fetchall()
        except sqlite3.Error as e:
            self.__logger.error("Exception on %s, error message is %s", sql, e)
            ret = None
        return ret
