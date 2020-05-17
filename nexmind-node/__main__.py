from authenticator import AuthDatabase
from web import Web
import argparse


def main():
    auth_database = AuthDatabase()
    parser = argparse.ArgumentParser(description="aiohttp server example")
    parser.add_argument("--path")
    parser.add_argument("--port")
    Web(auth_database, parser.parse_args()).start()


if __name__ == "__main__":
    main()
