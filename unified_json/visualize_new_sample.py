from csv import reader
from math import sqrt
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use
from tqdm import tqdm
from click import command, option
from sys import path
from os import makedirs
from multiprocessing import Pool, cpu_count
from typing import List

path.append("..")

from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator


pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


def generate_images(key: int, component: nx.DiGraph):
    pos = nx.nx_agraph.graphviz_layout(component)
    types = nx.get_node_attributes(component, "type")
    numbers = nx.get_node_attributes(component, "number")
    statuses = nx.get_node_attributes(component, "status")
    labels = dict()
    edge_labels = dict()
    colors = []
    side_length = 10 + (sqrt(component.size() - 20) if component.size() > 20 else 0)
    plt.figure(key, figsize=(side_length, side_length))
    plt.title(f"Component #{key} from {component.graph['repository']}")
    issues = list(filter(lambda cn: types[cn] == "issue", component.nodes))
    prs = list(filter(lambda cn: types[cn] == "pull_request", component.nodes))
    issue_colors = [
        "#f46d75" if statuses[cn] == "closed" else "#64389f" if statuses[cn] == "merged" else "#77dd77" for cn in issues
    ]
    pr_colors = [
        "#f46d75" if statuses[cn] == "closed" else "#64389f" if statuses[cn] == "merged" else "#77dd77" for cn in prs
    ]
    nx.draw(
        component,
        pos,
        nodelist=issues,
        node_color=issue_colors,
        node_shape="s",
        font_size=10,
        node_size=200,
    )
    nx.draw(
        component,
        pos,
        nodelist=prs,
        node_color=pr_colors,
        node_shape="o",
        font_size=10,
        node_size=200,
    )
    for cn in component.nodes:
        labels[cn] = f"{types[cn]} #{numbers[cn]}"
    link_types = nx.get_edge_attributes(component, "link_type")
    for ce in component.edges:
        if link_types[ce] != "other":
            edge_labels[ce] = link_types[ce]
    nx.draw_networkx_labels(component, pos=pos, labels=labels, font_size=10)
    nx.draw_networkx_edges(component, pos)
    nx.draw_networkx_edge_labels(component, pos=pos, edge_labels=edge_labels, font_size=10)
    try:
        makedirs(f"unified_json/second_sample_images/")
    except:
        pass
    plt.tight_layout()
    plt.savefig(f"unified_json/second_sample_images/{key}.png")
    plt.clf()
    plt.close()


def parallelize_sample_generation(line: List[str]):
    target_repo = line[1]
    node_list = list(map(lambda l: int(l), line[-1].split("|")))
    nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, target_repo)
    local_graph = nx.DiGraph(repository=target_repo)
    to_add = []
    edges_to_add = []
    for index, node in enumerate(nodes):
        if node.number not in node_list:
            continue
        node_status = node.state
        if node.pull_request is not None:
            if node.pull_request.raw_data["merged_at"] is not None:
                node_status = "merged"
        to_add.append(
            (
                f"{target_repo}#{node.number}",
                {
                    "type": "pull_request" if node.pull_request is not None else "issue",
                    "status": node_status,
                    "repository": target_repo,
                    "number": node.number,
                    "creation_date": node.created_at.timestamp(),
                    "closed_at": node.closed_at.timestamp() if node.closed_at is not None else 0,
                    "updated_at": node.updated_at.timestamp(),
                },
            )
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
            if mention.source.issue.number not in node_list:
                continue
            edges_to_add.append(
                (
                    f"{target_repo}#{mention.source.issue.number}",
                    f"{target_repo}#{node.number}",
                    {
                        "link_type": nwvc.find_automatic_links(
                            node.number, mention.source.issue.body, mentioning_issue_comments
                        )
                    },
                )
            )
    local_graph.add_nodes_from(to_add)
    local_graph.add_edges_from(edges_to_add)
    generate_images(int(line[0]), local_graph)


@command()
@option("--file", "file")
def main(file: str):
    use("qtagg")

    with open(file, "r") as x:
        lines = x.readlines()
        lines = lines[1:]
        total_lines = len(lines)

    with Pool(cpu_count() // 2) as p:
        with tqdm(total=total_lines, leave=False) as pbar:
            for _ in p.imap_unordered(parallelize_sample_generation, reader(lines)):
                pbar.update()


if __name__ == "__main__":
    main()
