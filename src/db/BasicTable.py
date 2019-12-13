import sqlite3

import logging


class BasicTable():
    __cursor = None
    __logger = logging.getLogger("basicTable")

    def __init__(self, cursor):
        self.__cursor = cursor

    @classmethod
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
            self.__logger.error("exception on " + sql)
            ret = None
        return ret

    @classmethod
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
            self.__logger.error("exception on " + sql)
            ret = None
        return ret

    @classmethod
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
            self.__logger.error("exception on " + sql)
            ret = None
        return ret

    @classmethod
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
            self.__logger.error("exception on " + sql)
            ret = None
        return ret
