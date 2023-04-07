from json import loads
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
from csv import reader
from sys import path

path.append("..")
from scripts.helpers import generate_image


def special_case_size() -> bool:
    return component_id not in [38589, 16428]


with open("sampled-links.csv", "r") as x:
    lines = x.read().splitlines()[1:]

latest_component = nx.DiGraph()
components = []
repository: str | None = None
component_id: int | None = None
repo_json = None
for line in tqdm(reader(lines), total=len(list(reader(lines)))):
    if not any(line):
        if component_id is not None and repository is not None:
            components.append(latest_component)
            generate_image(
                latest_component,
                component_id,
                f"Component #{component_id} in {repository}",
                17 if special_case_size() else 15 if latest_component.size() >= 10 else 10,
                "",
                node_size=400 if special_case_size() else 250,
                font_size=12 if special_case_size() else 10,
                dpi=80 if special_case_size() else 120 if latest_component.size() >= 10 else 100,
            )
        latest_component = nx.DiGraph()
        repository = None
        component_id = None
    if line[0] and line[0] != repository:
        repository = line[0]
        component_id = int(line[1])
        repo_json = loads(open(f"../data/graph_{repository.replace('/','-')}.json", "r").read())
    if repository and repo_json:
        node_1_status = next(filter(lambda x: x["id"] == int(line[4]), repo_json["nodes"]))["status"]
        node_1_date = next(filter(lambda x: x["id"] == int(line[4]), repo_json["nodes"]))["creation_date"]
        node_1_user = next(filter(lambda x: x["id"] == int(line[4]), repo_json["nodes"]))["node_creator"]
        node_2_status = next(filter(lambda x: x["id"] == int(line[8]), repo_json["nodes"]))["status"]
        node_2_user = next(filter(lambda x: x["id"] == int(line[8]), repo_json["nodes"]))["node_creator"]
        node_2_date = next(filter(lambda x: x["id"] == int(line[8]), repo_json["nodes"]))["creation_date"]
        latest_component.add_node(
            f"{repository}#{line[4]}",
            type=line[3],
            status=node_1_status,
            number=line[4],
            labels=line[3],
            user=node_1_user,
            creation_date=int(node_1_date),
            repository=repository,
        )
        latest_component.add_node(
            f"{repository}#{line[8]}",
            type=line[7],
            status=node_2_status,
            number=line[8],
            labels=line[3],
            user=node_2_user,
            creation_date=int(node_2_date),
            repository=repository,
        )
        if line[11] != "ignore":
            latest_component.add_edge(
                f"{repository}#{line[4]}", f"{repository}#{line[8]}", link_type=line[11], labels=line[11]
            )

g = nx.union_all(components)
nx.write_graphml(g, "all.graphml", named_key_ids=True)
