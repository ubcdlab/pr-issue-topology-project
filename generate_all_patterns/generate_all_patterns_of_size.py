from collections import defaultdict
import operator
from sys import argv, path
from os import makedirs
from os.path import isfile
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use
from pickle import dump, load
from math import sqrt
from tqdm import tqdm

path.append("..")

from scripts.helpers import all_graphs, num_graphs, to_json
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator


class ExtendedDiGraphMatcher(nx.isomorphism.DiGraphMatcher):
    def is_isomorphic(self):
        default_isomorphic = super().is_isomorphic()
        if not default_isomorphic:
            return default_isomorphic
        non_matching_edge = False
        for edge in self.G1.edges():
            edge_og_1, edge_og_2 = edge
            if not self.G2.has_edge(self.mapping[edge_og_1], self.mapping[edge_og_2]):
                non_matching_edge = True
                break
        return not non_matching_edge


size = 5
for arg in argv:
    if arg.startswith("size"):
        size = int(arg.split("=")[-1])

to_render = False
if "to_render" in argv:
    print("Rendering to images...")
    to_render = True

with_status = False
if "with_status" in argv:
    print("Including status...")
    with_status = True

edge_direction_match = False
if "edge_direction_match" in argv:
    print("Matching edge directions...")
    edge_direction_match = True

graph = nx.DiGraph()
total_patterns = 0
all_patterns = defaultdict(int)

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


def node_match_with_status(node_1, node_2):
    return node_1["type"] == node_2["type"] and node_1["status"] == node_2["status"]


def node_match_type(node_1, node_2):
    return node_1["type"] == node_2["type"]


if not isfile(f"pattern_dump/graph_{size}.pk"):
    for path in tqdm(all_graphs(), total=num_graphs()):
        path_str = str(path)
        target_repo = to_json(path_str)["repo_url"].replace("https://github.com/", "")

        nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, target_repo)

        local_graph = nx.DiGraph()
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
                number=node.number,
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
                    link_type=nwvc.find_automatic_links(
                        node.number, mention.source.issue.body, mentioning_issue_comments
                    ),
                )

        connected_components = [
            local_graph.subgraph(c).copy() for c in nx.connected_components(local_graph.to_undirected())
        ]
        for cc in connected_components:
            if len(cc.nodes) != size:
                local_graph.remove_nodes_from(cc)
            else:
                total_patterns += 1
                for pattern in all_patterns:
                    if not nx.is_isomorphic(
                        cc,
                        pattern,
                        node_match=node_match_with_status if with_status else node_match_type,
                        edge_match=(lambda x, y: x == y) if with_status else None,
                    ):
                        continue
                    matcher_type = nx.isomorphism.DiGraphMatcher if not edge_direction_match else ExtendedDiGraphMatcher
                    dgm = matcher_type(
                        nx.path_graph(cc, create_using=nx.DiGraph),
                        nx.path_graph(pattern, create_using=nx.DiGraph),
                    )
                    dgm.match()
                    if dgm.is_isomorphic():
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
    with open(f"pattern_dump/graph_{size}.pk", "wb") as x:
        dump(graph, x)
else:
    with open(f"pattern_dump/{size}.pk", "rb") as x:
        all_patterns = load(x)
    with open(f"pattern_dump/graph_{size}.pk", "rb") as x:
        graph = load(x)

if to_render:
    use("agg")
    top_20_patterns = list(map(lambda x: x[0], sorted(all_patterns.items(), key=lambda x: x[1], reverse=True)[:20]))
    for i, component in enumerate(tqdm(top_20_patterns, total=len(top_20_patterns))):
        pos = nx.nx_agraph.graphviz_layout(graph)
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
            makedirs(f"image_dump/{size}")
        except:
            pass
        plt.savefig(f"image_dump/{size}/{i}.png")
        plt.clf()
