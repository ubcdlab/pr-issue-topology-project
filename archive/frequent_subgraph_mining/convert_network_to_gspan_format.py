from sys import argv, path
import networkx as nx
from pipeline.NetworkVisCreator import NetworkVisCreator
from tqdm import tqdm
from prettytable import PrettyTable

path.append("..")

from pipeline.picklereader import PickleReader
from scripts.helpers import all_graphs, fetch_repo, num_graphs

output_path = None
for arg in argv:
    if "output" in arg:
        output_path = arg.split("=")[-1]

if not output_path:
    print("Must provide output path.")
    exit(1)

graph = nx.Graph()
gspan_format = []

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])
table = PrettyTable()
table.field_names = ["Graph #", "Repository"]

for i, path in tqdm(enumerate(all_graphs()), total=num_graphs()):
    target_repo = fetch_repo(str(path), from_graph=True)
    table.add_row([i, target_repo])
    gspan_format += [f"t # {i}"]
    nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, target_repo)

    for index, node in enumerate(nodes):
        graph.add_node(node.number, type=0 if node.pull_request is not None else 1)
        #  graph.add_node(node.number, type="pull_request" if node.pull_request is not None else "issue")
        node_timeline = timeline_list[-index - 1]
        node_timeline = list(
            filter(
                lambda x: x.event == "cross-referenced"
                and x.source.issue.repository.full_name.replace("/", "-") == target_repo,
                node_timeline,
            )
        )
        for mention in node_timeline:
            mentioning_issue_comments = nwvc.find_comment(mention.source.issue.url, comment_list)
            graph.add_edge(
                mention.source.issue.number,
                node.number,
                link_type=nwvc.find_automatic_links(node.number, mention.source.issue.body, mentioning_issue_comments),
            )

    for node in graph.nodes(data=True):
        gspan_format += [f"v {node[0]} {node[1].get('type', None)}"]

    link_type_map = {"other": 0, "fixes": 1, "duplicate": 2}
    for edge in graph.edges(data=True):
        gspan_format += [f"e {edge[0]} {edge[1]} {link_type_map[edge[2].get('link_type', None)]}"]

gspan_format += ["t # -1"]

with open(output_path, "w") as x:
    x.write("\n".join(gspan_format))

print(table)
