import os
import sqlite3
import argon2
import exceptions


class AuthDatabase:
    def __init__(self):
        self.password_hasher = argon2.PasswordHasher()
        self.connection = self._create_connection(self._get_database_file())
        if not self._has_users_table(self.connection):
            self._create_users_table(self.connection)

    def register(self, username, password):

        cursor = self.connection.cursor()
        hash = self.password_hasher.hash(password)

        try:
            cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hash))

        except sqlite3.IntegrityError:
            raise exceptions.Unauthorized("Username taken")

        self.connection.commit()

    def login(self, username, password):

        cursor = self.connection.cursor()
        cursor.execute("SELECT hash FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if not result:
            raise exceptions.Unauthorized("not registered")
        hash = result[0]

        try:
            self.password_hasher.verify(hash, password)
            if self.password_hasher.check_needs_rehash(hash):
                hash = self.password_hasher.hash(password)
                sql_hash_updater = """ UPDATE users
                        SET hash = ?
                        WHERE username = ?"""
                cursor.execute(sql_hash_updater, (hash, username))
                self.connection.commit()

        except argon2.exceptions.VerifyMismatchError as error:
            raise exceptions.Unauthorized("Wrong password")

    def _get_database_file(self):
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "storage/", "users.db"
        )

    def _create_connection(self, db_file):
        """ create a database self.connection to a SQLite database """
        self.connection = None
        try:
            self.connection = sqlite3.connect(db_file)
        except sqlite3.Error as error:
            print(error)

        return self.connection

    def _has_users_table(self, connection):
        """ check if the create_table_sql statement has a users table
        :param self.connection: Connection object
        :return:
        """
        cursor = connection.cursor()

        # get the count of tables with the name
        cursor.execute(
            """ SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users' """
        )

        # if the count is 1, then table exists
        return cursor.fetchone()[0] == 1

    def _create_users_table(self, connection):
        """ create a users table
        :param self.connection: Connection object
        :return:
        """
        sql_create_users_table = """CREATE TABLE IF NOT EXISTS users (
                                    username text UNIQUE PRIMARY KEY NOT NULL,
                                    hash text NOT NULL
                                );"""
        try:
            cursor = connection.cursor()
            cursor.execute(sql_create_users_table)
        except sqlite3.Error as error:
            print(error)
