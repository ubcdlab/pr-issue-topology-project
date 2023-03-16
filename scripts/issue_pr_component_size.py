from collections import defaultdict
from statistics import median, pstdev, fmean
from sys import path
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from prettytable import PrettyTable
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from click import command, option
from dataclasses import dataclass

path.append("..")

from scripts.helpers import all_graphs, num_graphs, to_json
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


@dataclass(repr=True)
class IssuePrCountStatistics:
    issue_count: int
    issue_open: int
    issue_closed: int
    pr_count: int
    pr_open: int
    pr_closed: int
    pr_merged: int
    edges_fixes: int
    edges_duplicate: int
    edges_count: int
    count: int


def parallelize_graph_processing(path: Path):
    path_str = str(path)
    target_repo = to_json(path_str)["repo_url"].replace("https://github.com/", "")

    nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, target_repo)

    local_graph = nx.Graph(repository=target_repo)
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
    return local_graph


@command()
def main():
    small_statistics = IssuePrCountStatistics(0, 0, 0, 0, 0, 0, 0, 0)
    large_statistics = IssuePrCountStatistics(0, 0, 0, 0, 0, 0, 0, 0)

    with Pool(cpu_count() // 2) as p:
        with tqdm(total=num_graphs(), leave=False) as pbar:
            for res in p.imap_unordered(parallelize_graph_processing, all_graphs()):
                for component in nx.connected_components(res):
                    to_add_to = None
                    if len(component) < 20:
                        to_add_to = small_statistics
                    elif len(component) > 100:
                        to_add_to = large_statistics
                    else:
                        break
                    to_add_to.count += len(component)
                    for node in res.subgraph(component).nodes(data=True):
                        if node[1]["type"] == "pull_request":
                            if node[1]["status"] == "open":
                                to_add_to.pr_open += 1
                            elif node[1]["status"] == "closed":
                                to_add_to.pr_closed += 1
                            else:
                                to_add_to.pr_merged += 1
                            to_add_to.pr_count += 1
                        else:
                            if node[1]["status"] == "open":
                                to_add_to.issue_open += 1
                            else:
                                to_add_to.issue_closed += 1
                            to_add_to.issue_count += 1
                    for edge in res.subgraph(component).edges(data=True):
                        if edge[2]["link_type"] == "fixes":
                            to_add_to.edges_fixes += 1
                        elif edge[2]["link_type"] == "duplicate":
                            to_add_to.edges_duplicate += 1
                        to_add_to.edges_count += 1
                pbar.update()

    table = PrettyTable()
    table.field_names = [
        "Small Component Count",
        "Issues",
        "Issues %",
        "Issue Status Distribution",
        "PRs",
        "PRs %",
        "PR Status Distribution",
        "Edges",
        "Fixes Edges #, %",
        "Duplicate Edges #, %",
    ]
    table.add_row(
        [
            small_statistics.count,
            small_statistics.issue_count,
            f"{small_statistics.issue_count/small_statistics.count:.2%}",
            f"{small_statistics.issue_open/small_statistics.issue_count:.2%} open, {small_statistics.issue_closed/small_statistics.issue_count:.2%} closed",
            small_statistics.pr_count,
            f"{small_statistics.pr_count/small_statistics.count:.2%}",
            f"{small_statistics.pr_open/small_statistics.pr_count:.2%} open, {small_statistics.pr_closed/small_statistics.pr_count:.2%} closed, {small_statistics.pr_merged/small_statistics.pr_count:.2%} merged",
            small_statistics.edges_count,
            f"{small_statistics.edges_fixes/small_statistics.edges_count:.2%} ({small_statistics.edges_fixes})"
            f"{small_statistics.edges_duplicate/small_statistics.edges_count:.2%} ({small_statistics.edges_duplicate})",
        ]
    )
    print(table)

    table = PrettyTable()
    table.field_names = [
        "Large Component Count",
        "Issues",
        "Issues %",
        "Issue Status Distribution",
        "PRs",
        "PRs %",
        "PR Status Distribution",
    ]
    table.add_row(
        [
            large_statistics.count,
            large_statistics.issue_count,
            f"{large_statistics.issue_count/large_statistics.count:.2%}",
            f"{large_statistics.issue_open/large_statistics.issue_count:.2%} open, {large_statistics.issue_closed/large_statistics.issue_count:.2%} closed",
            large_statistics.pr_count,
            f"{large_statistics.pr_count/large_statistics.count:.2%}",
            f"{large_statistics.pr_open/large_statistics.pr_count:.2%} open, {large_statistics.pr_closed/large_statistics.pr_count:.2%} closed, {large_statistics.pr_merged/large_statistics.pr_count:.2%} merged",
            large_statistics.edges_count,
            f"{large_statistics.edges_fixes/large_statistics.edges_count:.2%} ({large_statistics.edges_fixes})"
            f"{large_statistics.edges_duplicate/large_statistics.edges_count:.2%} ({large_statistics.edges_duplicate})",
        ]
    )
    print(table)


if __name__ == "__main__":
    main()
