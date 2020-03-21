import sys

class Data:

    def __init__(self, spaces, hash, meta=None):
        self.spaces = spaces
        self.hash = hash
        self.meta = meta

available_identifiers = []

groups = {}

items = []

def _find_smallest_space(spaces_name):
    minimal_space = groups[spaces_name[0]]
    if len(spaces_name) > 1:
        for space_name in spaces_name:
            space = groups[space_name]
            if len(space) < len(minimal_space):
                minimal_space = space
    return minimal_space

def inter(*spaces_name):
    smallest_space = _find_smallest_space(spaces_name)
    condition_spaces = [space_name for space_name in spaces_name if space_name != smallest_space]

    results = []

    for item_id in smallest_space:
        data = items[ item_id ]
        if all(conditional_space in data.spaces for conditional_space in condition_spaces):
            results.append(data)

    return results

def sum(*spaces_name):
    result_set = set()
    for space_name in spaces_name:
        result_set = result_set | groups[space_name]
    print( result_set )


def add_data(data):
    if len(available_identifiers) > 0:
        id = available_identifiers.remove[0]
        items[id] = data
    else:
        id = len(items)
        items.append(data)
    
    for space_name in data.spaces:
        if space_name in groups:
            space = groups[space_name]
            space.add( id )
        else:
            groups[space_name] = { id }

def remove_data(data):
    id = items.index(data)
    for space in data.spaces:
        groups[space].remove(id)
    items[id] = None
    available_identifiers.append(id)