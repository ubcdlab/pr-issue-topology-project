from collections import defaultdict
from sys import path
from os import makedirs
from os.path import isfile
from pathlib import Path
from typing import Any
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use
from pickle import dump, load
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from click import command, option

path.append("..")

from data_scripts.helpers import all_graphs, num_graphs, to_json, generate_image
from archive.pipeline.picklereader import PickleReader
from archive.pipeline.NetworkVisCreator import NetworkVisCreator


def node_match_with_status(node_1, node_2):
    return node_1["type"] == node_2["type"] and node_1["status"] == node_2["status"]


def node_match_type(node_1, node_2):
    return node_1["type"] == node_2["type"]


@command()
@option("--size", "size", default=5)
@option("--render", "to_render", default=False, is_flag=True)
@option("--status", "with_status", default=False, is_flag=True)
@option("--edge-direction", "edge_direction", default=False, is_flag=True)
def main(size: int, to_render: bool, with_status: bool, edge_direction: bool):
    def parallelize_graph_processing(path: Path):
        path_str = str(path)
        target_repo = to_json(path_str)["repo_url"].replace("https://github.com/", "")

        nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(
            None, target_repo
        )

        local_graph = (
            nx.DiGraph(repository=target_repo)
            if edge_direction
            else nx.Graph(repository=target_repo)
        )
        to_add = []
        edges_to_add = []
        for index, node in enumerate(nodes):
            node_status = node.state
            if node.pull_request is not None:
                if node.pull_request.raw_data["merged_at"] is not None:
                    node_status = "merged"
            to_add.append(
                (
                    f"{target_repo}#{node.number}",
                    {
                        "type": (
                            "pull_request" if node.pull_request is not None else "issue"
                        ),
                        "status": node_status,
                        "repository": target_repo,
                        "number": node.number,
                        "creation_date": node.created_at.timestamp(),
                        "closed_at": (
                            node.closed_at.timestamp()
                            if node.closed_at is not None
                            else 0
                        ),
                        "updated_at": node.updated_at.timestamp(),
                    },
                )
            )
            node_timeline = timeline_list[-index - 1]
            node_timeline = list(
                filter(
                    lambda x: x.event == "cross-referenced"
                    and x.source.issue.repository.full_name == target_repo,
                    node_timeline,
                )
            )
            for mention in node_timeline:
                mentioning_issue_comments = nwvc.find_comment(
                    mention.source.issue.url, comment_list
                )
                edges_to_add.append(
                    (
                        f"{target_repo}#{mention.source.issue.number}",
                        f"{target_repo}#{node.number}",
                        {
                            "link_type": nwvc.find_automatic_links(
                                node.number,
                                mention.source.issue.body,
                                mentioning_issue_comments,
                            )
                        },
                    )
                )

        local_graph.add_nodes_from(to_add)
        local_graph.add_edges_from(edges_to_add)
        return local_graph

    if to_render:
        print("Rendering to images...")

    if with_status:
        print("Including status...")

    if edge_direction:
        print("Including edge direction...")

    total_patterns = 0
    all_patterns = defaultdict(int)

    pr = PickleReader([])
    nwvc = NetworkVisCreator(None, [])

    if not isfile(
        f"pattern_dump/graph_{size}{'_undirected' if not edge_direction else ''}.pk"
    ):
        result = []
        with Pool(cpu_count() // 2) as p:
            with tqdm(total=num_graphs(), leave=False) as pbar:
                for res in p.imap_unordered(parallelize_graph_processing, all_graphs()):
                    result.append(res)
                    pbar.update()
        graph = nx.compose_all(result)
        connected_components = [
            graph.subgraph(c).copy()
            for c in nx.connected_components(graph.to_undirected())
        ]
        for cc in connected_components:
            if len(cc.nodes) != size:
                graph.remove_nodes_from(cc)
            else:
                total_patterns += 1
                for pattern in all_patterns:
                    if nx.is_isomorphic(
                        cc,
                        pattern,
                        node_match=(
                            node_match_with_status if with_status else node_match_type
                        ),
                        edge_match=(lambda x, y: x == y) if with_status else None,
                    ):
                        all_patterns[pattern] += 1
                        break
                else:
                    all_patterns[cc] = 1

        try:
            makedirs(f"pattern_dump/")
        except:
            pass
        with open(
            f"pattern_dump/{size}{'_undirected' if not edge_direction else ''}.pk", "wb"
        ) as x:
            dump(all_patterns, x)
        with open(
            f"pattern_dump/graph_{size}{'_undirected' if not edge_direction else ''}.pk",
            "wb",
        ) as x:
            dump(graph, x)
    else:
        with open(
            f"pattern_dump/{size}{'_undirected' if not edge_direction else ''}.pk", "rb"
        ) as x:
            all_patterns = load(x)
        with open(
            f"pattern_dump/graph_{size}{'_undirected' if not edge_direction else ''}.pk",
            "rb",
        ) as x:
            graph = load(x)
        total_patterns = sum(all_patterns.values())

    def generate_image_wrapper(args: Any):
        i, component, all_patterns = args
        generate_image(
            component,
            i,
            f"#{i+1} most frequent pattern of size {component.size()}\n{all_patterns[component]} occurrences, {all_patterns[component]/total_patterns:.2}% of size\nExample occurrence in {component.graph['repository']}",
            10,
            f"image_dump/{'undirected_' if not edge_direction else ''}{component.size()}",
        )

    if to_render:
        use("agg")
        top_20_patterns = list(
            map(
                lambda x: x[0],
                sorted(all_patterns.items(), key=lambda x: x[1], reverse=True)[:20],
            )
        )
        with Pool(cpu_count() // 2) as p:
            with tqdm(total=len(top_20_patterns), leave=False) as pbar:
                for _ in p.imap_unordered(
                    generate_image_wrapper,
                    [
                        (i, component, all_patterns)
                        for i, component in enumerate(top_20_patterns)
                    ],
                ):
                    pbar.update()
