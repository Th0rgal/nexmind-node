import sys

print("test")

class Data:

    def __init__(self, spaces, hash, meta=None):
        self.spaces = spaces
        self.hash = hash
        self.meta = meta

class Database:

    def __init__(self, folder):
        self.folder = folder
        self.available_identifiers = []
        self.groups = {}
        self.items = []

    def _find_smallest_space(self, spaces_name):
        minimal_space = self.groups[spaces_name[0]]
        if len(spaces_name) > 1:
            for space_name in spaces_name:
                space = self.groups[space_name]
                if len(space) < len(minimal_space):
                    minimal_space = space
        return minimal_space

    def inter(self, *spaces_name):
        smallest_space = _find_smallest_space(spaces_name)
        condition_spaces = [space_name for space_name in spaces_name if space_name != smallest_space]

        results = []

        for item_id in smallest_space:
            data = self.items[ item_id ]
            if all(conditional_space in data.spaces for conditional_space in condition_spaces):
                results.append(data)

        return results

    def sum(self, *spaces_name):
        result_set = set()
        for space_name in spaces_name:
            result_set = result_set | self.groups[space_name]
        print( result_set )


    def add_data(self, data):
        if len(available_identifiers) > 0:
            id = available_identifiers.remove[0]
            self.items[id] = data
        else:
            id = len(items)
            self.items.append(data)
        
        for space_name in data.spaces:
            if space_name in self.groups:
                space = self.groups[space_name]
                space.add( id )
            else:
                self.groups[space_name] = { id }

    def remove_data(self, data):
        id = self.items.index(data)
        for space in data.spaces:
            self.groups[space].remove(id)
        self.items[id] = None
        self.available_identifiers.append(id)