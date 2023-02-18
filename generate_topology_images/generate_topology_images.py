from json import loads
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass
from tqdm import tqdm
from csv import reader


@dataclass(repr=True)
class ComponentNode:
    repo_name: str
    component_id: int
    link_url: str
    node_1_type: str
    node_1_id: int
    node_1_author: str
    node_1_num_comment: str
    node_2_type: str
    node_2_id: int
    node_2_author: str
    node_2_num_comment: str
    link_type: str
    quotes: str


def generate_image(graph: nx.DiGraph, component_id: int, repo: str):
    def special_case_size() -> bool:
        return component_id not in [38589, 16428]

    pos = nx.nx_agraph.graphviz_layout(graph)
    types = nx.get_node_attributes(graph, "type")
    numbers = nx.get_node_attributes(graph, "number")
    statuses = nx.get_node_attributes(graph, "status")
    labels = dict()
    edge_labels = dict()
    colors = []
    if special_case_size():
        plt.figure(1, figsize=(17, 17), dpi=80)
    if graph.size() >= 10:
        plt.figure(1, figsize=(15, 15), dpi=120)
    else:
        plt.figure(1, figsize=(10, 10))
    plt.title(f"Component #{component_id} in {repo}")
    issues = list(filter(lambda cn: types[cn] == "issue", graph.nodes))
    prs = list(filter(lambda cn: types[cn] == "pull_request", graph.nodes))
    issue_colors = [
        "#f46d75" if statuses[cn] == "closed" else "#9d78cf" if statuses[cn] == "merged" else "#77dd77" for cn in issues
    ]
    pr_colors = [
        "#f46d75" if statuses[cn] == "closed" else "#9d78cf" if statuses[cn] == "merged" else "#77dd77" for cn in prs
    ]
    nx.draw(
        graph,
        pos,
        nodelist=issues,
        node_color=issue_colors,
        node_shape="s",
        font_size=10,
        node_size=400 if special_case_size() else 250,
    )
    nx.draw(
        graph,
        pos,
        nodelist=prs,
        node_color=pr_colors,
        node_shape="o",
        font_size=10,
        node_size=400 if special_case_size() else 250,
    )
    for cn in graph.nodes:
        labels[cn] = f"{'I' if types[cn] == 'issue' else 'PR'} #{numbers[cn]}"
    link_types = nx.get_edge_attributes(graph, "link_type")
    for ce in graph.edges:
        if link_types[ce] != "other":
            edge_labels[ce] = link_types[ce]
    nx.draw_networkx_labels(graph, pos=pos, labels=labels, font_size=12 if special_case_size() else 10)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_labels, font_size=10)
    plt.tight_layout()
    plt.savefig(f"{component_id}.png")
    plt.clf()


with open("sampled-links.csv", "r") as x:
    lines = x.read().splitlines()[1:]

latest_component = nx.DiGraph()
repository: str | None = None
component_id: int | None = None
repo_json = None
for line in tqdm(reader(lines), total=len(list(reader(lines)))):
    if not any(line):
        if component_id is not None and repository is not None:
            generate_image(latest_component, component_id, repository)
        latest_component = nx.DiGraph()
        repository = None
        component_id = None
    if line[0] and line[0] != repository:
        repository = line[0]
        component_id = int(line[1])
        repo_json = loads(open(f"../data/graph_{repository.replace('/','-')}.json", "r").read())
    if repository and repo_json:
        node_1_status = next(filter(lambda x: x["id"] == int(line[4]), repo_json["nodes"]))["status"]
        node_2_status = next(filter(lambda x: x["id"] == int(line[8]), repo_json["nodes"]))["status"]
        latest_component.add_node(f"{repository}#{line[4]}", type=line[3], status=node_1_status, number=line[4])
        latest_component.add_node(f"{repository}#{line[8]}", type=line[7], status=node_2_status, number=line[8])
        if line[11] != "ignore":
            latest_component.add_edge(f"{repository}#{line[4]}", f"{repository}#{line[8]}", link_type=line[11])
