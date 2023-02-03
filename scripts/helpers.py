from pathlib import Path
from json import loads
from re import match


def all_structures():
    return Path("data/").glob("**/structure_*.json")


def num_structures():
    return len(list(Path("data/").glob("**/structure_*.json")))


def to_json(path_str: str):
    with open(path_str) as json_file:
        return loads(json_file.read())


def fetch_path(path_str: str, from_graph: bool = False):
    match_obj = match(rf".*{'graph' if from_graph else 'structure'}_([\w\-.]+).json", path_str)
    if not match_obj:
        print("Could not find repository name from file path.", path_str)
        exit(1)
    return f"data/{'graph' if not from_graph else 'structure'}_{match_obj.groups()[0]}.json"


def all_graphs():
    return Path("data/").glob("**/graph_*.json")


def num_graphs():
    return len(list(Path("data/").glob("**/graph_*.json")))
