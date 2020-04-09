import authenticator
from web import http_server

def main():
    authenticator.load()
    http_server.load()

if __name__ == '__main__':
    main()