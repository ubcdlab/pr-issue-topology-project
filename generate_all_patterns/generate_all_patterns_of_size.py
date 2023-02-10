from collections import defaultdict
from sys import argv, path
from os import makedirs
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use
from pickle import dump
from tqdm import tqdm

path.append("..")

from scripts.helpers import all_graphs, to_json
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator

size = 5
for arg in argv:
    if arg.startswith("size"):
        size = int(arg.split("=")[-1])

to_render = False
if "to_render" in argv:
    print("Rendering to images...")
    to_render = True

graph = nx.Graph()
total_patterns = 0
all_patterns = defaultdict(int)

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


def node_match(node_1, node_2):
    return node_1["type"] == node_2["type"] and node_1["status"] == node_2["status"]


path_list_len = len(list(all_graphs()))
for path in tqdm(all_graphs(), total=path_list_len):
    path_str = str(path)
    target_repo = to_json(path_str)["repo_url"].replace("https://github.com/", "")

    nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, target_repo)

    local_graph = nx.Graph()
    for index, node in enumerate(nodes):
        node_status = node.state
        if node.pull_request is not None:
            if node.pull_request.raw_data["merged_at"] is not None:
                node_status = "merged"
        local_graph.add_node(
            f"{target_repo}#{node.number}",
            type="pull_request" if node.pull_request is not None else "issue",
            status=node_status,
            repository=target_repo,
            creation_date=node.created_at.timestamp(),
            closed_at=node.closed_at.timestamp() if node.closed_at is not None else 0,
            updated_at=node.updated_at.timestamp(),
        )
        node_timeline = timeline_list[-index - 1]
        node_timeline = list(
            filter(
                lambda x: x.event == "cross-referenced" and x.source.issue.repository.full_name == target_repo,
                node_timeline,
            )
        )
        for mention in node_timeline:
            mentioning_issue_comments = nwvc.find_comment(mention.source.issue.url, comment_list)
            local_graph.add_edge(
                f"{target_repo}#{mention.source.issue.number}",
                f"{target_repo}#{node.number}",
                link_type=nwvc.find_automatic_links(node.number, mention.source.issue.body, mentioning_issue_comments),
            )

    connected_components = [local_graph.subgraph(c).copy() for c in nx.connected_components(local_graph)]
    for cc in connected_components:
        if len(cc.nodes) != size:
            local_graph.remove_nodes_from(cc)
        else:
            total_patterns += 1
            for pattern in all_patterns:
                if nx.is_isomorphic(cc, pattern, node_match=node_match, edge_match=lambda x, y: x == y):
                    all_patterns[pattern] += 1
                    break
            else:
                all_patterns[cc] = 1

    graph = nx.compose(graph, local_graph)

try:
    makedirs(f"pattern_dump/")
except:
    pass
with open(f"pattern_dump/{size}.pk", "wb") as x:
    dump(all_patterns, x)

if to_render:
    use("agg")
    components = [graph.subgraph(c) for c in nx.connected_components(graph)]
    for i, component in enumerate(tqdm(components, total=len(components))):
        pos = nx.spring_layout(graph)
        labels = dict()
        types = nx.get_node_attributes(component, "type")
        statuses = nx.get_node_attributes(component, "status")
        repository = list(nx.get_node_attributes(component, "repository").values())[0]
        colors = []
        for cn in component.nodes:
            labels[cn] = f"{cn}\n{types[cn]}\n{statuses[cn]}"
            color = "#f46d75" if statuses[cn] == "closed" else "#64389f" if statuses[cn] == "merged" else "#77dd77"
            nx.draw(component, pos, nodelist=[cn], node_color=color, node_shape="s" if types[cn] == "issue" else "o")
        link_types = nx.get_edge_attributes(component, "link_type")
        edge_colors = []
        for ce in component.edges:
            edge_colors += [
                "#9cadce" if link_types[ce] == "fixes" else "#7ec4cf" if link_types[ce] == "duplicate" else "#5a5a5a"
            ]
        nx.draw_networkx_labels(component, pos=pos, labels=labels)
        nx.draw_networkx_edges(component, pos, edge_color=edge_colors)
        nx.draw_networkx_edge_labels(component, pos=pos)
        try:
            makedirs(f"image_dump/{repository.replace('/','-')}/{size}")
        except:
            pass
        plt.savefig(f"image_dump/{repository.replace('/','-')}/{size}/{i}.png")
        plt.clf()
