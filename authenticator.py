import os
import sqlite3
import argon2
import exceptions

# VARIABLES
connection = None
password_hasher = argon2.PasswordHasher()


def _get_database_file():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "storage/", "users.db")

def _create_connection(db_file):
    """ create a database connection to a SQLite database """
    connection = None
    try:
        connection = sqlite3.connect(db_file)
    except sqlite3.Error as error:
        print(error)

    return connection

def _has_users_table(connection):
    """ check if the create_table_sql statement has a users table
    :param connection: Connection object
    :return:
    """
    cursor = connection.cursor()

    #get the count of tables with the name
    cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users' ''')

    #if the count is 1, then table exists
    return cursor.fetchone()[0]==1


def _create_users_table(connection):
    """ create a users table
    :param connection: Connection object
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


def load():
    global connection
    connection = _create_connection(_get_database_file())
    if not _has_users_table(connection):
        _create_users_table(connection)

def is_loaded():
    return connection != None

def register(username, password):
    
    cursor = connection.cursor()
    hash = password_hasher.hash(password)

    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hash))

    except sqlite3.IntegrityError as error:
        raise exceptions.Unauthorized("Username taken")

    connection.commit()

def login(username, password):

    cursor = connection.cursor()
    cursor.execute("SELECT hash FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    if result == None:
        raise exceptions.Unauthorized("not registered")
    hash = result[0]

    try:
        password_hasher.verify(hash, password)
        if password_hasher.check_needs_rehash(hash):
            hash = password_hasher.hash(password)
            sql_hash_updater = ''' UPDATE users
                    SET hash = ?
                    WHERE username = ?'''
            cursor.execute(sql_hash_updater, (hash, username))
            connection.commit()

    except argon2.exceptions.VerifyMismatchError as error:
        raise exceptions.Unauthorized("Wrong password")