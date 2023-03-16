from pathlib import Path
from json import loads
from re import match
from typing import List, Tuple, Dict
import networkx as nx
from os import makedirs, scandir, remove
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
    to_highlight: List[int] | Dict[int, int] = [],
    relationships_to_highlight: List[Tuple[int, int] | Tuple[int, int, int]] = [],
    central: List[int] = None,
    link=None,
    legend: List[str] = [],
):
    use("agg")
    pos = nx.nx_agraph.graphviz_layout(component)
    types = nx.get_node_attributes(component, "type")
    numbers = nx.get_node_attributes(component, "number")
    statuses = nx.get_node_attributes(component, "status")
    labels = dict()
    to_highlight_labels = dict()
    edge_labels = dict()
    plt.figure(key, figsize=(side_length, side_length), dpi=dpi)
    plt.title(title)
    COLOR_GROUP_MAP = ["#fede00", "#FF0000", "#ffa500", "#ffff00", "#008000", "#0000ff", "#4b0082"]
    issues = list(filter(lambda cn: types[cn] == "issue", component.nodes))
    prs = list(filter(lambda cn: types[cn] == "pull_request", component.nodes))
    if central:
        central = list(filter(lambda cn: numbers[cn] in central, component.nodes))
    issue_colors = [
        "#f46d75" if statuses[cn] == "closed" else "#a57cde" if statuses[cn] == "merged" else "#77dd77" for cn in issues
    ]
    issue_edge_colors = [
        "#fede00"
        if (type(to_highlight) == list and numbers[cn] in to_highlight) or numbers[cn] == central
        else COLOR_GROUP_MAP[to_highlight[numbers[cn]]]
        if type(to_highlight) == dict and numbers[cn] in to_highlight
        else issue_colors[i]
        for i, cn in enumerate(issues)
    ]
    pr_colors = [
        "#f46d75" if statuses[cn] == "closed" else "#a57cde" if statuses[cn] == "merged" else "#77dd77" for cn in prs
    ]
    pr_edge_colors = [
        "#fede00"
        if (type(to_highlight) == list and numbers[cn] in to_highlight) or numbers[cn] == central
        else COLOR_GROUP_MAP[to_highlight[numbers[cn]]]
        if type(to_highlight) == dict and numbers[cn] in to_highlight
        else pr_colors[i]
        for i, cn in enumerate(prs)
    ]
    nx.draw(
        component,
        pos,
        nodelist=issues,
        node_color=issue_colors,
        edgecolors=issue_edge_colors,
        node_shape="s",
        font_size=font_size,
        node_size=node_size,
        linewidths=2,
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
        linewidths=2,
    )
    if central:
        nx.draw(
            component,
            pos,
            nodelist=central,
            node_color="#fede00",
            node_shape="*",
            font_size=font_size,
            node_size=node_size,
            linewidths=2,
        )
    for cn in component.nodes:
        label = f"{'I' if types[cn] == 'issue' else 'PR'} #{numbers[cn]}"
        if numbers[cn] in to_highlight:
            to_highlight_labels[cn] = label
        else:
            labels[cn] = label
    link_types = nx.get_edge_attributes(component, "link_type")
    if relationships_to_highlight:
        if len(relationships_to_highlight[0]) == 3:
            edge_colors = [
                COLOR_GROUP_MAP[
                    next(
                        filter(lambda a: (a[0], a[1]) == (u, v) or (a[0], a[1]) == (v, u), relationships_to_highlight)
                    )[2]
                ]
                if len(relationships_to_highlight[0]) == 3
                and len(
                    list(filter(lambda a: (a[0], a[1]) == (u, v) or (a[0], a[1]) == (v, u), relationships_to_highlight))
                )
                != 0
                else "#fede00"
                if len(
                    list(filter(lambda a: (a[0], a[1]) == (u, v) or (a[0], a[1]) == (v, u), relationships_to_highlight))
                )
                != 0
                else "#000000"
                for u, v in component.edges
            ]
        else:
            edge_colors = [
                "#fede00" if (u, v) in relationships_to_highlight or (v, u) in relationships_to_highlight else "#000000"
                for u, v in component.edges
            ]
    else:
        edge_colors = ["#000000" for u, v in component.edges]
    for ce in component.edges:
        if link_types[ce] not in ignore_link_types:
            edge_labels[ce] = link_types[ce]
    nx.draw_networkx_labels(component, pos=pos, labels=labels, font_size=font_size)
    nx.draw_networkx_labels(component, pos=pos, labels=to_highlight_labels, font_size=font_size, font_weight="bold")
    nx.draw_networkx_edges(component, pos, edge_color=edge_colors)
    nx.draw_networkx_edge_labels(component, pos=pos, edge_labels=edge_labels, font_size=font_size)
    if link:
        plt.figtext(0.5, 0.01, link, horizontalalignment="center")
    if len(legend):
        custom_lines = [plt.Line2D([0], [0], color=COLOR_GROUP_MAP[i + 1], lw=4) for i in range(len(legend))]
        plt.legend(custom_lines, legend)
    try:
        makedirs(file_path)
    except:
        pass
    plt.tight_layout()
    plt.savefig(f"{file_path}{key}.png")
    plt.clf()
    plt.close()
