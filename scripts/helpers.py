from pathlib import Path
from json import loads
from re import match
from typing import List, Tuple
import networkx as nx
from os import makedirs
import matplotlib.pyplot as plt
from matplotlib import use


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


def fetch_repo(path_str: str, from_graph: bool = False):
    match_obj = match(rf".*{'graph' if from_graph else 'structure'}_([\w\-.]+).json", path_str)
    if not match_obj:
        print("Could not find repository name from file path.", path_str)
        exit(1)
    return match_obj.groups()[0]


def all_graphs():
    return Path("data/").glob("**/graph_*.json")


def num_graphs():
    return len(list(Path("data/").glob("**/graph_*.json")))


def generate_image(
    component: nx.DiGraph | nx.Graph,
    key: int,
    title: str,
    side_length: float | int,
    file_path: str,
    ignore_link_types: List[str] = ["other"],
    node_size: int = 200,
    font_size: int = 10,
    dpi: int = 100,
    to_highlight: List[int] = [],
    relationships_to_highlight: List[Tuple[int, int]] = [],
):
    use("agg")
    pos = nx.nx_agraph.graphviz_layout(component)
    types = nx.get_node_attributes(component, "type")
    numbers = nx.get_node_attributes(component, "number")
    statuses = nx.get_node_attributes(component, "status")
    labels = dict()
    edge_labels = dict()
    colors = []
    plt.figure(key, figsize=(side_length, side_length), dpi=dpi)
    plt.title(title)
    issues = list(filter(lambda cn: types[cn] == "issue", component.nodes))
    prs = list(filter(lambda cn: types[cn] == "pull_request", component.nodes))
    issue_colors = [
        "#f46d75" if statuses[cn] == "closed" else "#64389f" if statuses[cn] == "merged" else "#77dd77" for cn in issues
    ]
    issue_edge_colors = ["#fede00" if numbers[cn] in to_highlight else issue_colors[i] for i, cn in enumerate(issues)]
    pr_colors = [
        "#f46d75" if statuses[cn] == "closed" else "#64389f" if statuses[cn] == "merged" else "#77dd77" for cn in prs
    ]
    pr_edge_colors = ["#fede00" if numbers[cn] in to_highlight else pr_colors[i] for i, cn in enumerate(prs)]
    nx.draw(
        component,
        pos,
        nodelist=issues,
        node_color=issue_colors,
        edgecolors=issue_colors,
        node_shape="s",
        font_size=font_size,
        node_size=node_size,
    )
    nx.draw(
        component,
        pos,
        nodelist=prs,
        node_color=pr_colors,
        edgecolors=pr_edge_colors,
        node_shape="o",
        font_size=font_size,
        node_size=node_size,
    )
    for cn in component.nodes:
        labels[cn] = f"{'I' if types[cn] == 'issue' else 'PR'} #{numbers[cn]}"
    link_types = nx.get_edge_attributes(component, "link_type")
    edge_colors = ["#fede00" if (u, v) in relationships_to_highlight else "#000000" for u, v in component.edges]
    for ce in component.edges:
        if link_types[ce] not in ignore_link_types:
            edge_labels[ce] = link_types[ce]
    nx.draw_networkx_labels(component, pos=pos, labels=labels, font_size=font_size)
    nx.draw_networkx_edges(component, pos, edge_color=edge_colors)
    nx.draw_networkx_edge_labels(component, pos=pos, edge_labels=edge_labels, font_size=font_size)
    try:
        makedirs(file_path)
    except:
        pass
    plt.tight_layout()
    plt.savefig(f"{file_path}{key}.png")
    plt.clf()
    plt.close()
