import collections.abc


def flatten_json(d, parent_key='', sep='.'):
    """
    Recursively flattens a nested dictionary.

    Example:
    {'a': {'b': 1, 'c': 2}} 
    becomes 
    {'a.b': 1, 'a.c': 2}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            # If value is a dict, recurse
            items.extend(flatten_json(v, new_key, sep=sep).items())
        else:
            # If value is a leaf node (str, int, bool, etc.)
            items.append((new_key, v))
    return dict(items)
