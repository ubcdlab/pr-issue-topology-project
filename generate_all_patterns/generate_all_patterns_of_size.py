from collections import defaultdict
from sys import argv, path
from os import makedirs
import networkx as nx
import matplotlib.pyplot as plt

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
    return node_1 == node_2


for path in all_graphs():
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
                if nx.is_isomorphic(cc, pattern, node_match=node_match):
                    all_patterns[pattern] += 1
                    break
            else:
                all_patterns[cc] = 1

    graph = nx.compose(graph, local_graph)

    if to_render:
        try:
            makedirs(f"image_dump/{target_repo.replace('/','-')}/{size}")
        except:
            pass
        for i, component in enumerate([local_graph.subgraph(c) for c in nx.connected_components(local_graph)]):
            pos = nx.spring_layout(graph)
            labels = dict()
            types = nx.get_node_attributes(component, "type")
            statuses = nx.get_node_attributes(component, "status")
            colors = []
            for cn in component.nodes:
                labels[cn] = f"{cn}\n{types[cn]}\n{statuses[cn]}"
                colors += ["#fce1e4" if types[cn] == "issue" else "#e8dff5"]
            link_types = nx.get_edge_attributes(component, "link_type")
            edge_colors = []
            for ce in component.edges:
                edge_colors += [
                    "#9cadce"
                    if link_types[ce] == "fixes"
                    else "#7ec4cf"
                    if link_types[ce] == "duplicate"
                    else "#5a5a5a"
                ]
            nx.draw(component, pos=pos, node_color=colors, edge_color=edge_colors)
            nx.draw_networkx_labels(component, pos=pos, labels=labels)
            nx.draw_networkx_edge_labels(component, pos=pos)
            plt.savefig(f"image_dump/{target_repo.replace('/','-')}/{size}/{i}.png")
            plt.clf()

    break  # TODO: remove

print(all_patterns)
