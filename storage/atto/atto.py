import os
import json
from pathlib import Path

def get_data_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", name)

class Database:

    def __init__(self, name):
        self.name = name
        self.path = get_data_path(name)
        self.load_data()

    def load_data(self):

        if self.name.endswith(".py") or self.name.startswith("."): # should never be triggered
            return

        if os.path.exists(self.path):
            with open(self.path) as json_file:
                data = json.load(json_file)
                self.available_identifiers = data["free"]
                groups = data["groups"]
                for group_name in groups:
                    groups[group_name] = set(groups[group_name])
                self.groups = groups
                self.items = data["items"]
                return

        self.available_identifiers = []
        self.groups = {}
        self.items = []

    def save_data(self):
        groups = self.groups.copy()
        for group_name in groups:
            groups[group_name] = list(groups[group_name])
        data = { "free" : self.available_identifiers, "groups" : groups, "items" : self.items }
        Path( os.path.dirname(self.path) ).mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w') as outfile:
            json.dump(data, outfile)

    def _find_smallest_space(self, spaces_name):
        minimal_space = self.groups[spaces_name[0]]
        if len(spaces_name) > 1:
            for space_name in spaces_name:
                space = self.groups[space_name]
                if len(space) < len(minimal_space):
                    minimal_space = space
        return minimal_space

    def inter(self, *spaces_name):
        smallest_space = self._find_smallest_space(spaces_name)
        condition_spaces = [space_name for space_name in spaces_name if space_name != smallest_space]

        results = set()

        for item_id in smallest_space:
            data = self.items[ item_id ]
            if all(conditional_space in data[1] for conditional_space in condition_spaces):
                results.add(data[0]) # we append the hash

        return results

    def sum(self, *spaces_name):
        result_set = set()
        for space_name in spaces_name:
            result_set = result_set | self.groups[space_name]
        result_hashes = set()
        for id in result_set:
            result_hashes.add( self.items[id][0] )
        return result_hashes 

    def add_data(self, data): # potential amelioration: avoid duplicates
        if len(self.available_identifiers) > 0:
            id = self.available_identifiers.remove[0]
            self.items[id] = data
        else:
            id = len(self.items)
            self.items.append(data)
        
        for space_name in data[1]:
            if space_name in self.groups:
                space = self.groups[space_name]
                space.add( id )
            else:
                self.groups[space_name] = { id }
        self.save_data()

    def remove_data(self, data):
        id = self.items.index(data)
        for space in data[1]:
            self.groups[space].remove(id)
        self.items[id] = None
        self.available_identifiers.append(id)
        self.save_data()