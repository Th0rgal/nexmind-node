import os

def get_file(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", name)
