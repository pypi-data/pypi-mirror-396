from typing import Iterable

def flatten(l):
    return [item for sub in l for item in sub]

def top_k_texts_from_retrievals(retrievals):
    """
    Helper to convert retrieval results (e.g. list of lists of (text, score) tuples)
    to list of lists of text IDs or canonical strings.
    """
    converted = []
    for r in retrievals:
        row = []
        for item in r:
            if isinstance(item, (list, tuple)):
                row.append(item[0])
            else:
                row.append(item)
        converted.append(row)
    return converted
