from authenticator import AuthDatabase
from web import Web


def main():
    auth_database = AuthDatabase()
    Web(auth_database).start()


if __name__ == "__main__":
    main()
